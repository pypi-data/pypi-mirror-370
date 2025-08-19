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


import os
import logging
from typing import List, Dict, Optional, Union
from volcengine_qcclient.config import config_data
from volcengine_qcclient.qc_batchjob import QcBatchJob, get_default_logger

class QcClient:
    def __init__(
        self,
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        qc_service_id: Optional[str] = None,
        log_level: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        if logger:
            self.logger = logger
        elif log_level:
            self.logger = get_default_logger(log_level)
        else:
            self.logger = get_default_logger(logging.INFO)

        self.ak = ak or config_data.get('ak')
        self.sk = sk or config_data.get('sk')
        self.qc_service_id = qc_service_id or config_data.get('qc_service_id')
        # TODO: create QcService once here and reuse it in QcBatchJob

    def submit(self,
               task_type: str,
               task_config: Union[Dict, List[Dict]],
               molecules: Union[str, List[str]] = None,
               label: str = None) -> QcBatchJob:
        '''
        Create and submit a Batch Job for the given molecules and task configurations.
        Note this job cannot be submitted again.
        '''
        job = QcBatchJob(self.ak, self.sk, self.qc_service_id, label=label, logger=self.logger)
        if molecules is not None:
            if isinstance(molecules, str):
                if os.path.isdir(molecules):
                    job.load_molecules(from_dir=molecules)
                else:
                    job.load_molecules(from_file=molecules)
            else:
                job.load_molecules(from_list=molecules)
        job.submit(task_type, task_config)
        return job

    def download_outputs(self,
                         label: str,
                         task_ids: Optional[List[str]] = None,
                         target_dir: Optional[str] = None,
                         with_molecule_name: bool = False,
                         overwrite_exists: bool = False):
        job = QcBatchJob(self.ak, self.sk, self.qc_service_id, label=label, logger=self.logger)
        job.download_outputs(task_ids, target_dir, with_molecule_name, overwrite_exists)
