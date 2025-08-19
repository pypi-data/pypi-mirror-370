# Copyright (2025) Beijing Volcano Engine Technology Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import logging
import sys
import time
from typing import List, Dict, Optional, Union
import os
from datetime import datetime
import random
import string
from enum import Enum
from retry import retry
import requests
import tarfile
import shutil
import json
import yaml
from requests.exceptions import ReadTimeout, Timeout
from urllib3.exceptions import ReadTimeoutError

from volcengine_qcclient import QcService, config
from volcengine_qcclient.qc_service import ServiceError
from volcengine_qcclient.drivers import sp_validation, opt_validation, eda_validation

validTaskStatuses = [
    "Pending",
    "Running",
    "Succeeded",
    "Failed",
    "Killed",
    "Stopped",
]

MAX_BATCH_SIZE = config.MAX_BATCH_SIZE # 100 by default


class TaskType(Enum):
    STEREOIZER = "stereoizer"
    CONFGEN = "confgen"
    STEREO_ASSIGN = "stereo-assign"
    OPT = "opt"
    EDA = 'eda'
    SP = "sp"
    PYSISPHUS = "pysisyphus"
    PYSCFRPC = "pyscf-rpc"
    PKA_PREDICT = 'pka-predict'

    @classmethod
    def cpu_task_types(cls):
        return [cls.STEREOIZER.value, cls.STEREO_ASSIGN.value, cls.CONFGEN.value, cls.PKA_PREDICT.value]


def _generate_label(prefix='qcbatchjob'):
    now = datetime.now()
    date_str = now.strftime("%Y%m%d%H%M")

    # generate random string with length 5.
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    # generate final label.
    label = f"{prefix}-{date_str}-{random_str}"
    return label


def encode_base64(raw: str) -> str:
    return base64.b64encode(raw.encode('utf-8')).decode('utf-8')


def decode_base64(raw: str) -> str:
    return base64.b64decode(raw.encode('utf-8')).decode('utf-8')


def hide_str(s: str, hide_length=30):
    if not s:
        return ''
    if len(s) <= hide_length:
        return '*' * len(s)

    start_index = (len(s) - hide_length) // 2
    end_index = start_index + hide_length

    hidden_string = s[:start_index] + '*' * hide_length + s[end_index:]

    return hidden_string


def is_valid_xyz_content(content: str) -> bool:
    lines = content.split('\n')

    # Check if there are enough lines
    if len(lines) < 2:
        return False

    # Check if the first line is a valid integer
    try:
        num_atoms = int(lines[0])
    except ValueError:
        return False

    # Check if the number of atom lines matches the specified number of atoms
    if len(lines) != num_atoms + 2:
        return False

    # Validate each atom line
    for i in range(2, len(lines)):
        parts = lines[i].split()
        if len(parts) != 4:
            return False

        element, x, y, z = parts

        # Check if the element symbol is alphabetic
        if not element.isalpha():
            return False

        # Check if x, y, z are valid floating point numbers
        try:
            float(x)
            float(y)
            float(z)
        except ValueError:
            return False

    return True


def is_finished(summary: dict) -> bool:
    for status in ["Running", "Pending", "Killed"]:
        if status in summary and summary[status] > 0:
            return False
    return True


# download_output download output of qc task to target_dir.
@retry(exceptions=Exception, tries=3, delay=2)
def download_output(url: str, target_dir: str):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    os.makedirs(target_dir, exist_ok=True)
    # todo: `.h5` output is deprecated, need to remove in the future.
    if ".h5" in url:
        output_h5 = os.path.join(target_dir, "output.h5")
        with open(output_h5, 'wb') as f:
            f.write(requests.get(url).content)
    elif "tar.gz" in url:
        output_targz = os.path.join(target_dir, "output.tar.gz")
        try:
            with open(output_targz, 'wb') as f:
                f.write(requests.get(url).content)
            with tarfile.open(output_targz, 'r:gz') as tar:
                tar.extractall(path=target_dir)
        except Exception as e:
            print("download and untar output failed")
            e.args = ("download and untar output failed",) + e.args

            # clean target_dir for manual retry later.
            shutil.rmtree(target_dir)
            raise

        os.remove(output_targz)
    else:
        print("unsupported file type")


def get_default_logger(log_level):
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # Create a handler to output DEBUG and INFO level log messages to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)  # 设置处理器的最低日志级别
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)  # 过滤仅输出 DEBUG 和 INFO 级别的日志

    # Create a handler to output WARNING level and above log messages to stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)  # 设置处理器的最低日志级别

    # Create a formatter for the log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    return logger

def _apply_default_versions(task_config):
    '''Apply the default versions configured in ~/.volcqc.yaml or environments'''
    default_versions = config.default_versions
    if not default_versions:
        return task_config
    if 'versions' in task_config:
        # Merge the versions configuration in task_config and the default_versions
        versions = {**default_versions, **task_config['versions']}
    else:
        versions = default_versions
    return {**task_config, 'versions': versions}

# QcBatchJob: A batch job of qc tasks
# This class is used to manage a batch of quantum chemistry (QC) tasks. It provides methods for initializing the job,
# loading molecules, submitting tasks, checking task status, downloading outputs, and more.
class QcBatchJob:

    def __init__(
        self,
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        qc_service_id: Optional[str] = None,
        label: Optional[str] = None,
        log_level: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        is_cpu: bool = False,
    ):

        if logger:
            self.logger = logger
        elif log_level:
            self.logger = get_default_logger(log_level)
        else:
            self.logger = get_default_logger(logging.INFO)

        # init volcengine qc_service.
        self.qc_service = QcService()
        ak = ak or config.config_data.get('ak')
        sk = sk or config.config_data.get('sk')
        self.qc_service_id = qc_service_id or config.config_data.get('qc_service_id')

        if ak and sk:
            self.qc_service.set_ak(ak)
            self.qc_service.set_sk(sk)
        else:
            self.logger.warning('Config file ~/.volcqc.yaml does not exist, try to load ak/sk from env(`VOLC_ACCESSKEY` or `VOLC_SECRETKEY`) or ~/.volc/credentials.')

        # check if ak/sk is set.
        if not self.qc_service.service_info.credentials.ak or not self.qc_service.service_info.credentials.sk:
            raise ValueError("ak/sk can not load from env(`VOLC_ACCESSKEY` or `VOLC_SECRETKEY`) or "
                             "`~/.volc/credentials`.")

        self.logger.debug(f"ak: {hide_str(self.qc_service.service_info.credentials.ak)}")
        if label is None:
            self.label = _generate_label()
        else:
            self.label = label
        self.logger.info(f"task label is {self.label}")

        self.task_type = None
        self.molecules = []
        self.task_ids = []
        self.is_cpu = is_cpu

        if self.qc_service_id is None:
            self.qc_service_id = self.find_available_qc_service()

    def get_label(self) -> str:
        return self.label

    def find_available_qc_service(self) -> str:
        data = self.qc_service.list_qc_services(params={})
        for qc_service in data['Items']:
            # servicetype should match with server
            if self.is_cpu and qc_service['ServiceType'] not in TaskType.cpu_task_types():
                continue
            if qc_service['Status'] == 'Enabled':
                self.logger.info(f"Available qc service found: {qc_service['Id']}")
                return qc_service['Id']

        raise ValueError("No available qc service found.")

    def check_qc_service(self, qc_service_id) -> bool:
        data = self.qc_service.list_qc_services(params={
            "Ids": [qc_service_id],
        })
        if not isinstance(data["Items"], list) or len(data["Items"]) != 1:
            self.logger.error(f"qc_service_id {qc_service_id} is not found.")
            return False
        qc_service = data["Items"][0]
        if qc_service['Status'] != 'Enabled':
            self.logger.error(f"qc_service_id {qc_service_id} is not enabled.")
            return False
        return True

    # load molecules from local dir or file path or python list variable.
    def load_molecules(self,
                       from_dir: Optional[str] = None,
                       from_file: Optional[str] = None,
                       from_list: Optional[List[str]] = None,
                       with_molecule_names: Optional[List[str]] = None):
        if from_dir is not None:
            if not os.path.isdir(from_dir):
                raise ValueError("Directory does not exist.")
            for file_name in sorted(os.listdir(from_dir)):
                if file_name.endswith(".xyz"):
                    # parse molecule name from file_name.
                    molecule_name = file_name.rstrip(".xyz")
                    file_path = os.path.join(from_dir, file_name)
                    with open(file_path, "r") as file:
                        xyz_content = file.read()
                        xyz_content = xyz_content.strip("\n").strip()
                        self.molecules.append({
                            "molecule_name": molecule_name,
                            "content": xyz_content,
                        })

        if from_file is not None:
            if os.path.isfile(from_file) and from_file.endswith(".xyz"):
                molecule_name = os.path.basename(from_file).rstrip(".xyz")
                with open(from_file, "r") as file:
                    xyz_content = file.read()
                    xyz_content = xyz_content.strip("\n").strip()
                    self.molecules.append({
                        "molecule_name": molecule_name,
                        "content": xyz_content,
                    })

        if from_list is not None:
            if with_molecule_names is not None and len(with_molecule_names) != len(from_list):
                raise ValueError("`with_molecule_names` must be the same length as `from_list`.")

            for i in range(len(from_list)):
                xyz_content = from_list[i]
                if xyz_content.endswith(".xyz"):
                    with open(xyz_content, "r") as file:
                        xyz_content = file.read()

                xyz_content = xyz_content.strip("\n").strip()
                if not is_valid_xyz_content(xyz_content):
                    raise ValueError("Invalid xyz content.")

                self.molecules.append({
                    "molecule_name": "" if with_molecule_names is None else with_molecule_names[i],
                    "content": xyz_content,
                })

    def load_smiles(self, with_molecule_names: list[str], from_list: list[list[str]] = None):
        # we require molecule name for confgen task
        if with_molecule_names is None:
            raise ValueError("`with_molecule_names` must be set for stereoizer/confgen task.")

        if from_list is None:
            for molecule_name in with_molecule_names:
                self.molecules.append({
                    "molecule_name": molecule_name,
                })  # for stereo-assign
        else:
            if len(from_list) != len(with_molecule_names):
                raise ValueError("`with_molecule_names` must be the same length as `from_list`.")
            for smiles, molecule_name in zip(from_list, with_molecule_names):
                if len(smiles) == 1:  # for confgen
                    self.molecules.append({"molecule_name": molecule_name, "smiles": smiles[0]})
                elif len(smiles) == 2:  # for stereoizer, need protonated_smiles and deprotonated_smiles
                    self.molecules.append({
                        "molecule_name": molecule_name,
                        "protonated_smiles": smiles[0],
                        "deprotonated_smiles": smiles[1]
                    })

    def get_molecules(self) -> List[str]:
        return self.molecules

    def clear_molecules(self):
        self.molecules = []
        self.task_ids = []

    def validate(self, task_type, task_config, molecule=None):
        if config.VALIDATE_TASK:
            xyz = None
            if molecule is not None:
                xyz = molecule['content']
            if task_type == 'sp' or task_type == 'sp-test':
                sp_validation.validate(task_config, xyz)
            elif task_type == 'opt' or task_type == 'opt-test':
                opt_validation.validate(task_config, xyz)
            elif task_type == 'eda':
                eda_validation.validate(task_config, xyz)

    # submit qc tasks to server.
    def submit(self, task_type: str, task_config: Union[str, Dict, List[Dict]]) -> List[str]:
        # double-check task type.
        if self.task_ids:
            raise RuntimeError('BatchJob has been submitted. Jobs can only be submitted once.')

        if self.is_cpu and task_type not in TaskType.cpu_task_types():
            raise ValueError("cpu qc service only support stereoizer/stereo-assign/confgen task.")

        if len(self.molecules) == 0:
            self.logger.info("there are no molecules loaded, skip submit.")
            return []

        if isinstance(task_config, str):
            task_config = yaml.safe_load(task_config)

        self.task_type = task_type
        self.logger.info(f"task type is {self.task_type}")
        qc_tasks = []
        if isinstance(task_config, list):
            if len(task_config) != len(self.molecules):
                raise ValueError(f"task config is array(len {len(task_config)}),"
                                 f" but the length not equals preloaded molecules(len {len(self.molecules)}).")
            for i in range(len(self.molecules)):
                task_config_i = _apply_default_versions(task_config[i])
                self.validate(task_type, task_config_i, self.molecules[i])
                if (task_type == TaskType.OPT.value and 'constraints' in task_config_i and
                        os.path.exists(task_config_i['constraints'])):
                    with open(task_config_i['constraints'], 'r') as f:
                        task_config_i['constraints'] = f.read()
                if task_type in TaskType.cpu_task_types():
                    task_config_i.update(self.molecules[i])
                qc_tasks.append({
                    "MoleculeXyzData":
                        encode_base64(self.molecules[i]["content"])
                        if task_type not in TaskType.cpu_task_types() else "",
                    "MoleculeName":
                        self.molecules[i]["molecule_name"],
                    "QcTaskConfig":
                        task_config_i,
                })
        elif isinstance(task_config, dict):
            task_config = _apply_default_versions(task_config)
            self.validate(task_type, task_config, self.molecules[0])
            if (task_type == TaskType.OPT.value and 'constraints' in task_config and
                    os.path.exists(task_config['constraints'])):
                with open(task_config['constraints'], 'r') as f:
                    task_config['constraints'] = f.read()
            for molecule in self.molecules:
                if task_type in TaskType.cpu_task_types():
                    # Smells like a bug. Shouldn't this be
                    # task_config = {**_task_config, **molecule} ?
                    task_config = {**task_config.copy(), **molecule}
                qc_tasks.append({
                    "MoleculeXyzData":
                        encode_base64(molecule["content"]) if task_type not in TaskType.cpu_task_types() else "",
                    "MoleculeName":
                        molecule["molecule_name"],
                    "QcTaskConfig":
                        task_config,
                })
        else:
            raise ValueError("task_config must be either dict or list[dict]")

        offset = 0
        task_ids = []
        while offset < len(qc_tasks):
            batch_tasks = qc_tasks[offset:offset + MAX_BATCH_SIZE]
            params = {
                "QcServiceId": self.qc_service_id,
                "TaskType": task_type,
                "Label": self.label,
                "QcTasks": batch_tasks,
            }
            try:
                data = self.qc_service.submit_qc_tasks(params=params)
            except ServiceError as e:
                resp = json.loads(e.args[0])
                if resp['ResponseMetadata']['Error']['CodeN'] == 1709900:
                    if not self.check_qc_service(self.qc_service_id):
                        raise ValueError(f'qc_service_id {self.qc_service_id} is invalid.')
                raise
            task_ids.extend(data["Ids"])
            offset += MAX_BATCH_SIZE
        self.task_ids = task_ids
        return task_ids

    @retry(exceptions=(ReadTimeout, ReadTimeoutError, Timeout), tries=5, delay=2)
    def get_task_summary(self, task_ids=None) -> Dict[str, int]:
        params = {
            "QcServiceId": self.qc_service_id,
            "Label": self.label,
        }
        if task_ids is None:
            task_ids = self.task_ids
        if task_ids:
            params["Ids"] = task_ids
        return self.qc_service.get_qc_tasks_summary(params=params)

    def wait(
        self,
        download_outputs: bool = False,
        target_dir: Optional[str] = None,
        with_molecule_name: bool = False,
        overwrite_exists: bool = False,
        duration: int = config.WAIT_DURATION, # 5 by default
        timeout: int = None,
        task_ids: List[str] = None,
    ):
        self.logger.info(f"download_outputs is set {download_outputs}, overwrite_exists is set {overwrite_exists}.")
        while True:
            summary = self.get_task_summary(task_ids)
            self.logger.info(f"tasks summary: {summary}")

            if download_outputs:
                self.download_outputs(target_dir=target_dir,
                                      with_molecule_name=with_molecule_name,
                                      overwrite_exists=overwrite_exists)

            if len(summary) == 0:
                raise ValueError("no tasks found. Did you forget to call `submit()`?")

            if is_finished(summary):
                self.logger.info("batch job finished.")
                if 'Failed' in summary and summary['Failed'] > 0:
                    # TODO: print the failed tasks
                    # TODO: If download_outputs is True, parse the log.log file
                    # from download and print the error message
                    self.logger.error(f'{summary["Failed"]} tasks failed')
                break

            time.sleep(duration)
            if timeout is not None:
                timeout -= duration
                if timeout < 0:
                    self.stop()
                    raise TimeoutError

    def is_finished(self) -> bool:
        summary = self.get_task_summary()
        return is_finished(summary)

    def download_outputs(self,
                         task_ids: Optional[List[str]] = None,
                         target_dir: Optional[str] = None,
                         with_molecule_name: bool = False,
                         overwrite_exists: bool = False):
        if target_dir is None:
            target_dir = "./"

        if not task_ids:
            self.logger.info(f"try to download outputs of batch job {self.label} to {target_dir}")
        else:
            self.logger.info(f"try to download outputs of batch job {self.label} task_ids {task_ids} to {target_dir}")

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        params = {
            "QcServiceId": self.qc_service_id,
            "Label": self.label,
            "PageSize": MAX_BATCH_SIZE,
            "SortBy": "CreateTime",
            "SortOrder": "Asc",
        }
        if isinstance(task_ids, list) and len(task_ids) > 0:
            params["Ids"] = task_ids

        page_number = 1
        while True:
            params["PageNumber"] = page_number
            try:
                data = self.qc_service.list_qc_tasks(params=params)
            except Exception as e:
                self.logger.warning(f"list_qc_tasks failed, will retry again, error: {e}")
                continue

            if not data["Items"] or not isinstance(data["Items"], list):
                break

            for task in data["Items"]:
                task_id = task["Id"]
                output_url = task["OutputUrl"]
                if not output_url:
                    self.logger.debug(
                        f"output url of task_id: {task_id} is empty, skip download, task_status: {task['Status']}")
                    continue

                molecule_name = task["MoleculeName"].strip()
                if with_molecule_name and molecule_name != "":
                    task_dir = os.path.join(target_dir, molecule_name)
                else:
                    task_dir = os.path.join(target_dir, task_id)
                if os.path.exists(task_dir) and not overwrite_exists:
                    self.logger.debug(
                        f"task {task_id} output already exists and `overwrite_exists` is set {overwrite_exists}, "
                        f"skip download, task_dir: {task_dir}")
                    continue
                try:
                    download_output(output_url, task_dir)
                    self.logger.info(f"task {task_id} output downloaded, task_dir: {task_dir}")
                except tarfile.ReadError as e:
                    self.logger.error(f"download task {task_id} output failed, output_url: {output_url}, error: {e}"
                                      "\n\nYou can continue the download by executing the command\n"
                                      f"    volcqc job download --name {self.label} --target-dir {task_dir}")
                    continue
                except Exception as e:
                    self.logger.error(f"download task {task_id} output failed, output_url: {output_url}, error: {e}")
                    continue
            page_number += 1

    def get_tasks(self, task_ids: Optional[List[str]] = None) -> List[Dict]:
        params = {
            "QcServiceId": self.qc_service_id,
            "Label": self.label,
            "PageSize": MAX_BATCH_SIZE,
            "SortBy": "CreateTime",
            "SortOrder": "Asc",
        }
        if task_ids is not None and len(task_ids) > 0:
            params["Ids"] = task_ids

        tasks = []

        page_number = 1
        while True:
            params["PageNumber"] = page_number
            data = self.qc_service.list_qc_tasks(params=params)
            if data["Items"] is not None and len(data["Items"]) > 0:
                tasks.extend(data["Items"])
            else:
                break
            page_number += 1

        return tasks

    def stop(self):
        params = {
            "QcServiceId": self.qc_service_id,
            "Label": self.label,
        }
        self.qc_service.stop_qc_tasks(params=params)

    def retry(self, status: Optional[str] = None):
        params = {
            "QcServiceId": self.qc_service_id,
            "Label": self.label,
        }
        if status is not None:
            if status not in validTaskStatuses:
                raise ValueError(f"status must be in {validTaskStatuses}")
            params["Status"] = status

        self.qc_service.retry_qc_tasks(params=params)
