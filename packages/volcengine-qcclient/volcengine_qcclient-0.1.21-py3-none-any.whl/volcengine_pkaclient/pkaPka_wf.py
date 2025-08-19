# pylint: disable=W0621
import argparse as ap
import logging
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Union

import pandas as pd
import yaml
from volcengine_qcclient import QcBatchJob
from volcengine_qcclient.qc_batchjob import get_default_logger

logger = get_default_logger(logging.INFO)


########### DEFAULT VARIABLES ##############

DEFAULT_OPT_CONFIG = {
    "basis": "6-31Gs",
    "xc": "b3lyp",
    "spin": 0,
    "maxsteps": 100,
    "solvent": {
        "eps": 78.3553,
        "method": "IEFPCM",
        "solvent": "water"
    },
    "with_solvent": True,
    "verbose": 4,
    "with_gpu": True,
    "with_df": True
}

DEFAULT_SP_CONFIG = {
    'basis': '6-31Gs',
    'xc': 'b3lyp',
    "spin": 0,
    'maxsteps': 100,
    'solvent': {
        'eps': 78.3553,
        'method': 'IEFPCM',
        'solvent': 'water'
    },
    'with_solvent': True,
    'verbose': 4,
    'with_gpu': True,
    'with_df': True,
    'with_hess': True,
    'save_density': False,
    'with_thermo': True,
    'with_grad': True
}

################################################

check_dup = lambda elements: [ele for ele, count in Counter(elements).items() if count > 1]


def load_json(json_path: Path) -> dict:
    assert json_path.exists()
    with open(json_path, 'r') as f:
        return json.load(f)


def dump_json(json_path: Path, records: dict):
    with open(json_path, 'w') as f:
        json.dump(records, f, indent=2)


class TaskType(Enum):
    STEREOIZER = "stereoizer"
    CONFGEN = "confgen"
    STEREO_ASSIGN = "stereo-assign"
    OPT = "opt"
    SP = "sp"
    PYSISPHUS = "pysisyphus"
    PYSCFRPC = "pyscf-rpc"
    PKA_PREDICT = 'pka-predict'

    @classmethod
    def cpu_task_types(cls):
        return [cls.STEREOIZER.value, cls.STEREO_ASSIGN.value, cls.CONFGEN.value, cls.PKA_PREDICT.value]


@dataclass
class MicroPkaConfig:
    molecule_names: list[str]
    protonated_smiles: list[str]
    deprotonated_smiles: list[str]
    pH: float
    include_intra_HBond_pKa_datapoints: bool
    entropy_correction_mode: Optional[str] = None

    def __post_init__(self):
        dup_mol_names = check_dup(self.molecule_names)
        assert len(dup_mol_names) == 0, f"find dup mol_names: {dup_mol_names}"
        assert len(self.molecule_names) == len(self.protonated_smiles) == len(
            self.deprotonated_smiles
        ), f"{len(self.molecule_names)} vs {len(self.protonated_smiles)} vs {len(self.deprotonated_smiles)}"

        assert len(self.molecule_names) == len(self.protonated_smiles) == len(self.deprotonated_smiles)

    def to_json(self, working_dir: Union[str, Path]):
        # dump micropka calculation for future debug
        working_dir = Path(os.path.abspath(working_dir)) if isinstance(working_dir, str) else working_dir
        working_dir.mkdir(parents=True, exist_ok=True)

        json_path = working_dir / "pkaPka_config.json"

        with open(json_path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)

    # @classmethod
    # def from_json(cls, config_path: str):
    #     assert os.path.exists(config_path), f"config file: {config_path} does not exist"

    #     with open(config_path, "r") as f:
    #         config = json.load(f)

    #     return cls(**config)


class BatchMicroPkaExecutor:

    def __init__(self, working_dir: str, config: MicroPkaConfig):  # pylint: disable=W0621
        self.working_dir = Path(working_dir)
        self.config = config
        self.cpu_qc_batch_job: QcBatchJob = None
        self.gpu_qc_batch_job: QcBatchJob = None
        self.is_full_wf: bool = False

        # json record for each step
        self.batch_stereo_json_path: str = self.working_dir / "01_stereoizer.json"
        self.batch_confgen_json_path = self.working_dir / "02_confgen.json"
        self.batch_stereo_assign_json_path = self.working_dir / "03_stereo_assign.json"
        self.batch_opt_json_path = self.working_dir / "04_opt.json"
        self.batch_sp_json_path = self.working_dir / "05_sp.json"
        
        # json record for failed mol at each step
        self.stereo_failed_mols_path = self.working_dir / "01_failed_mols.json"
        self.confgen_failed_mol_path = self.working_dir / "02_confgen_failed_mol.json"
        self.stereo_assign_failed_mol_path = self.working_dir / "03_stereo_assign_failed_mol.json"
        self.opt_failed_mol_path = self.working_dir / "04_opt_failed_mol.json"
        self.sp_failed_mol_path = self.working_dir / "05_sp_failed_mol.json"
        self.pka_predict_failed_mol_path = self.working_dir / "06_pka_predict_failed_mol.json"
        

        # pKa prediction result record
        self.batch_pka_result: dict = {}

        # steps
        self.steps = [
            self._run_stereoizer, self._run_confgen, self._run_stereo_assign, self._run_opt, self._run_sp,
            self._run_pka_predict
        ]

        self._init_qc_batch_jobs()

    def _init_qc_batch_jobs(self):
        # find availble qc_service accordingly
        # TODO(chenyang): find service is not stable for staging env, here we specifiy qc_service_id
        self.cpu_qc_batch_job = QcBatchJob(is_cpu=True, qc_service_id='qcsvc-20250307132754-rndf8s8vbs5v55klsd2p', logger=logger)
        logger.info(f"cpu qc_batch_job with task_label: {self.cpu_qc_batch_job.get_label()}")
        self.gpu_qc_batch_job = QcBatchJob(qc_service_id='qcsvc-20250311202916-jqtj6t8w5rrr6wgz55l4', logger=logger)
        logger.info(f"gpu qc_batch_job with task_label: {self.gpu_qc_batch_job.get_label()}")   

    def _check_empty_tasks(self, tasks_config: dict):
        if len(tasks_config) == 0:
            logger.warning("no more molecules in the config, exit pka calculation.")
            sys.exit()

    def _run_stereoizer(self):
        assert self.cpu_qc_batch_job is not None
        batch_job = self.cpu_qc_batch_job
        config = self.config

        if self.batch_stereo_json_path.exists():
            logger.info("skip step1: stereoizer")
            succeed_mols_stereoizer_jsons_mapping = load_json(self.batch_stereo_json_path)
        else:
            logger.info("run stereoizer...")

            prot_deprot_smiles = [[prot_smi, deprot_smi]
                                  for prot_smi, deprot_smi in zip(config.protonated_smiles, config.deprotonated_smiles)]
            batch_job.load_smiles(with_molecule_names=config.molecule_names, from_list=prot_deprot_smiles)

            task_ids = batch_job.submit(task_type=TaskType.STEREOIZER.value, task_config={})
            # dump molecule_name_task_ids mapping
            mol_name_task_ids_mapping = {mol_name: task_id for mol_name, task_id in zip(config.molecule_names, task_ids)}
            logger.info(f"submit stereoizer {len(mol_name_task_ids_mapping)} tasks: {mol_name_task_ids_mapping}")

            stereoizer_debug_path = self.working_dir / "01_stereoizer_debug.json"
            with open(stereoizer_debug_path, 'w') as f:
                json.dump(mol_name_task_ids_mapping, f, indent=2)
            
            batch_job.wait()
            
            # download
            for mol_name, task_id in mol_name_task_ids_mapping.items():
                mol_dir = self.working_dir / mol_name
                mol_dir.mkdir(exist_ok=True)

                output_dir = mol_dir / "01_stereoizer_res"

                batch_job.download_outputs(task_ids=[task_id], target_dir=str(output_dir))

            # collect res
            succeed_mols_stereoizer_jsons_mapping, failed_mols = {}, []
            for mol_name in config.molecule_names:
                mol_dir = self.working_dir / mol_name
                stereo_json_pair_file_list = list(mol_dir.glob("01_stereoizer_res/*/stereo_info_pair.json"))
                if not len(stereo_json_pair_file_list):
                    failed_mols.append(mol_name)
                    continue

                assert len(stereo_json_pair_file_list) == 1
                stereo_json_pair_file = stereo_json_pair_file_list[0]

                with open(stereo_json_pair_file, "r") as f:
                    stereo_json_pair = json.load(f)

                succeed_mols_stereoizer_jsons_mapping[mol_name] = stereo_json_pair

            if len(failed_mols) > 0:
                failed_mols_task_ids = {mol_name: mol_name_task_ids_mapping[mol_name] for mol_name in failed_mols}
                logger.warning(f"the following mols failed at stereoizer: {failed_mols} dumped to {self.stereo_failed_mols_path} ")
                
                with open(self.stereo_failed_mols_path, "w") as f:
                    json.dump(failed_mols_task_ids, f, indent=2)

            # dump batch level config json file
            dump_json(self.batch_stereo_json_path, succeed_mols_stereoizer_jsons_mapping)

            batch_job.clear_molecules()

        # check empty tasks
        self._check_empty_tasks(succeed_mols_stereoizer_jsons_mapping)

        return

    def _run_confgen(self) -> dict:
        assert self.cpu_qc_batch_job is not None
        batch_job = self.cpu_qc_batch_job

        if self.batch_confgen_json_path.exists():
            logger.info("Skip step2: confgen")
            stereo_assign_configs = load_json(self.batch_confgen_json_path)
        else:
            logger.info("run confgen...")
            # precheck and load
            succeed_mols_stereoizer_jsons_mapping = load_json(self.batch_stereo_json_path)

            # submit confgen
            confgen_smiles_idxs = []
            stereo_assign_configs = {}
            total_smis = 0
            for mol_name, stereoizer_json in succeed_mols_stereoizer_jsons_mapping.items():
                # load prot smiles
                prot_smiles = stereoizer_json["prot_smi_mapping"]
                total_smis += len(prot_smiles)
                confgen_smiles_idxs.append(total_smis)
                for prot_smi in prot_smiles:
                    batch_job.load_smiles(with_molecule_names=[mol_name], from_list=[[prot_smi]])

                # load deprot smiles
                deprot_smiles = stereoizer_json["deprot_smi_mapping"]
                total_smis += len(deprot_smiles)
                confgen_smiles_idxs.append(total_smis)
                for deprot_smi in deprot_smiles:
                    batch_job.load_smiles(with_molecule_names=[mol_name], from_list=[[deprot_smi]])

                stereo_assign_configs[mol_name] = {"prot_deprot_pairs": stereoizer_json["prot_deprot_pairs"]}

            assert confgen_smiles_idxs[-1] == len(batch_job.molecules)
            assert len(confgen_smiles_idxs) % 2 == 0

            task_ids = batch_job.submit(task_type=TaskType.CONFGEN.value, task_config={})
            logger.info(f"submit confgen tasks with ids: {task_ids}")
            prot_idxs = confgen_smiles_idxs[0::2]
            deprot_idxs = confgen_smiles_idxs[1::2]

            # update stereo_assign_configs
            last_deprot_idx = 0
            for mol_name, stereoizer_json, prot_idx, deprot_idx in zip(succeed_mols_stereoizer_jsons_mapping.keys(),
                                                                       succeed_mols_stereoizer_jsons_mapping.values(),
                                                                       prot_idxs, deprot_idxs):
                prot_task_ids = task_ids[last_deprot_idx:prot_idx]
                prot_smiles = stereoizer_json["prot_smi_mapping"]
                deprot_task_ids = task_ids[prot_idx:deprot_idx]
                deprot_smiles = stereoizer_json["deprot_smi_mapping"]
                last_deprot_idx = deprot_idx

                stereo_assign_configs[mol_name]["prot_smi_sid_mapping"] = {
                    prot_smi: task_id for prot_smi, task_id in zip(prot_smiles, prot_task_ids)
                }
                stereo_assign_configs[mol_name]["deprot_smi_sid_mapping"] = {
                    deprot_smi: task_id for deprot_smi, task_id in zip(deprot_smiles, deprot_task_ids)
                }
                
            # NOTE: this debug json contains the mappings of all mol_name, smiles, task_ids
            confgen_debug_path = self.working_dir / "02_confgen_debug.json"
            with open(confgen_debug_path, 'w') as f:
                json.dump(stereo_assign_configs, f, indent=2)

            batch_job.wait()

            # check confgen res
            num_configs = len(stereo_assign_configs)
            failed_confgen_tasks = {}
            failed_mols = []
            for mol_name, stereo_assign_config in stereo_assign_configs.items():
                prot_idxs = list(stereo_assign_config["prot_smi_sid_mapping"].values())
                deprot_idxs = list(stereo_assign_config["deprot_smi_sid_mapping"].values())
                task_ids = prot_idxs + deprot_idxs
                mol_confgen_dir = self.working_dir / mol_name / "02_confgen_res"
                mol_confgen_dir.mkdir(parents=True, exist_ok=True)

                batch_job.download_outputs(task_ids=task_ids, target_dir=str(mol_confgen_dir))

                failed_prot_task_ids = []
                failed_deprot_task_ids = []
                for task_id in task_ids:
                    conf_0_path = mol_confgen_dir / task_id / "0_crest_qm_output/conf_0.xyz"

                    if not conf_0_path.exists():
                        if task_id in prot_idxs:
                            failed_prot_task_ids.append(task_id)
                        else:
                            failed_deprot_task_ids.append(task_id)

                if len(failed_prot_task_ids) > 0:
                    failed_confgen_tasks[mol_name] = {}
                    failed_confgen_tasks[mol_name]["failed_prot_smi_sid_mapping"] = {smi : task_id for smi, task_id in stereo_assign_config["prot_smi_sid_mapping"].items() if task_id in failed_prot_task_ids}
                
                stereo_assign_config["prot_smi_sid_mapping"] = {
                    k: v
                    for k, v in stereo_assign_config["prot_smi_sid_mapping"].items()
                    if v not in failed_prot_task_ids
                }
                
                if len(failed_deprot_task_ids) > 0:
                    if mol_name not in failed_confgen_tasks:
                        failed_confgen_tasks[mol_name] = {}
                    failed_confgen_tasks[mol_name]["failed_deprot_smi_sid_mapping"] = {smi : task_id for smi, task_id in stereo_assign_config["deprot_smi_sid_mapping"].items() if task_id in failed_deprot_task_ids}
                
                stereo_assign_config["deprot_smi_sid_mapping"] = {
                    k: v
                    for k, v in stereo_assign_config["deprot_smi_sid_mapping"].items()
                    if v not in failed_deprot_task_ids
                }
                
                
                if len(stereo_assign_config["prot_smi_sid_mapping"]) == 0 or len(
                        stereo_assign_config["deprot_smi_sid_mapping"]) == 0:
                    failed_mols.append(mol_name)

            if len(failed_mols) > 0:
                logger.info(f"the following mols failed at confgen {failed_mols} tasks dump to {self.confgen_failed_mol_path}")
                
                # rm failed_mols from config
                for failed_mol in failed_mols:
                    try:
                        assert failed_mol in stereo_assign_configs
                        stereo_assign_configs.pop(failed_mol)
                    except:
                        logger.warning(f"{failed_mol} not in stereo_assign_configs, some error occured")
                
                with open(self.confgen_failed_mol_path, "w") as f:
                    json.dump(failed_confgen_tasks, f, indent=2)

            num_configs_check = len(stereo_assign_configs)
            assert num_configs == num_configs_check + len(failed_mols)

            # dump
            dump_json(self.batch_confgen_json_path, stereo_assign_configs)

            batch_job.clear_molecules()

        # check empty tasks
        self._check_empty_tasks(stereo_assign_configs)

        return

    def _run_stereo_assign(self):
        logger.info("run stereo assign...")
        assert self.cpu_qc_batch_job is not None
        batch_job = self.cpu_qc_batch_job

        if self.batch_stereo_assign_json_path.exists():
            logger.info("Skip step3: stereo_assign")
            mol_sel_smi_mapping = load_json(self.batch_stereo_assign_json_path)
        else:
            # precheck and load
            stereo_assign_configs = load_json(self.batch_confgen_json_path)

            batch_job.load_smiles(with_molecule_names=list(stereo_assign_configs.keys()))

            task_ids = batch_job.submit(task_type=TaskType.STEREO_ASSIGN.value,
                                        task_config=list(stereo_assign_configs.values()))
            stereo_assign_mol_name_task_ids_mapping = {mol_name : task_id for mol_name, task_id in zip(stereo_assign_configs.keys(), task_ids)}
            logger.info(f"submit stereo assign with task_ids: {stereo_assign_mol_name_task_ids_mapping}")
            
            # dump
            stereo_assign_debug_path = self.working_dir / "03_stereo_assign_debug.json"
            with open(stereo_assign_debug_path, 'w') as f:
                json.dump(stereo_assign_mol_name_task_ids_mapping, f, indent=2)

            batch_job.wait()

            for mol_name, task_id in stereo_assign_mol_name_task_ids_mapping.items():
                mol_dir = self.working_dir / mol_name
                mol_dir.mkdir(exist_ok=True)
                stereo_assign_dir = mol_dir / "03_stereo_assign_res"
                stereo_assign_dir.mkdir()

                batch_job.download_outputs(task_ids=[task_id], target_dir=str(stereo_assign_dir))

            # collect res
            mol_sel_smi_mapping = {}
            failed_mols = {}
            for mol_name, _ in stereo_assign_configs.items():
                stereo_assign_path = self.working_dir / mol_name / "03_stereo_assign_res"
                assert stereo_assign_path.exists(), f"{stereo_assign_path} does not exist"
                assigned_chirality_json_path = list(stereo_assign_path.glob("*/assigned_chirality.json"))
                if not len(assigned_chirality_json_path):
                    logger.info(f"molecule {mol_name} is failed at stereo_assign...")
                    failed_mols[mol_name] = stereo_assign_mol_name_task_ids_mapping[mol_name]
                    continue

                assigned_chirality_json_path = assigned_chirality_json_path[0]
                # get select prot_smi and deprot_smi
                with open(assigned_chirality_json_path, 'r') as f:
                    assigned_chirality = json.load(f)

                sel_prot_smi = assigned_chirality["chirality_dom_HA"]
                sel_deprot_smi = assigned_chirality["chirality_dom_A_"]
                sel_prot_charg = assigned_chirality["charge_HA"]
                sel_deprot_charg = assigned_chirality["charge_A_"]

                mol_sel_smi_mapping[mol_name] = [sel_prot_smi, sel_deprot_smi, sel_prot_charg, sel_deprot_charg]
                
            if len(failed_mols) > 0:
                logger.info(f"the following molecules failed at stereo_assign: {failed_mols} dumped to {self.stereo_assign_failed_mol_path}")
                with open(self.stereo_assign_failed_mol_path, "w") as f:
                    json.dump(failed_mols, f, indent=2)

            # dump
            dump_json(self.batch_stereo_assign_json_path, mol_sel_smi_mapping)

            batch_job.clear_molecules()

        # check empty_tasks
        self._check_empty_tasks(mol_sel_smi_mapping)

        return

    def _run_opt(self):
        assert self.gpu_qc_batch_job is not None
        batch_job = self.gpu_qc_batch_job

        if self.batch_opt_json_path.exists():
            logger.info("Skip step4: opt")
            opt_sid_mappings = load_json(self.batch_opt_json_path)
        else:
            logger.info("Run step4: opt")

            # precheck and load
            stereo_assign_configs = load_json(self.batch_confgen_json_path)
            mol_sel_smi_mapping = load_json(self.batch_stereo_assign_json_path)

            succeed_mols, failed_mols = [], []
            num_opt_confs = []
            succeed_task_configs = []
            total_xyzs = 0
            for mol_name, stereo_assign_config in stereo_assign_configs.items():
                sel_prot_smi, sel_deprot_smi, sel_prot_charge, sel_deprot_charge = mol_sel_smi_mapping[mol_name]
                logger.info(
                    f"select protonated smiles: {sel_prot_smi} with charge {sel_prot_charge}, and deprotonated smiles: {sel_deprot_smi} with charge {sel_deprot_charge} for molecule: {mol_name}"
                )

                # prepare opt config
                prot_sid = stereo_assign_config["prot_smi_sid_mapping"][sel_prot_smi]
                deprot_sid = stereo_assign_config["deprot_smi_sid_mapping"][sel_deprot_smi]

                # collect conf.xyzs
                mol_confgen_dir = self.working_dir / mol_name / "02_confgen_res"
                xyzs_file_HA_path = mol_confgen_dir / f"{prot_sid}/0_crest_qm_output"
                assert xyzs_file_HA_path.exists()
                xyzs_file_A_path = mol_confgen_dir / f"{deprot_sid}/0_crest_qm_output"
                assert xyzs_file_A_path.exists()

                with open(f"{xyzs_file_HA_path}/xyz_list.yaml", 'r') as f:
                    xyzs = yaml.safe_load(f)["xyz_list"]

                HA_xyzs = [str(xyzs_file_HA_path / xyz) for xyz in xyzs]
                num_HA_xyzs = len(HA_xyzs)
                HA_task_configs = [{**DEFAULT_OPT_CONFIG, "charge": sel_prot_charge} for _ in range(num_HA_xyzs)]
                total_xyzs += num_HA_xyzs
                num_opt_confs.append(total_xyzs)
                logger.info(f"collect {num_HA_xyzs} conf xyzs for protonated smiles {sel_prot_smi}")
                batch_job.load_molecules(from_list=HA_xyzs)

                with open(f"{xyzs_file_A_path}/xyz_list.yaml", 'r') as f:
                    xyzs = yaml.safe_load(f)["xyz_list"]

                A_xyzs = [str(xyzs_file_A_path / xyz) for xyz in xyzs]
                num_A_xyzs = len(A_xyzs)
                A_task_configs = [{**DEFAULT_OPT_CONFIG, "charge": sel_deprot_charge} for _ in range(num_A_xyzs)]
                total_xyzs += num_A_xyzs
                num_opt_confs.append(total_xyzs)
                logger.info(f"collect {num_A_xyzs} conf xyzs for deprotonated smiles {sel_deprot_smi}")
                batch_job.load_molecules(from_list=A_xyzs)

                succeed_task_configs.extend(HA_task_configs + A_task_configs)

                succeed_mols.append(mol_name)

            assert num_opt_confs[-1] == len(batch_job.molecules) == len(succeed_task_configs)
            assert len(num_opt_confs) % 2 == 0

            # submit opt task
            task_ids = batch_job.submit(task_type=TaskType.OPT.value, task_config=succeed_task_configs)
            logger.info(f"submit opt tasks with ids: {task_ids}")

            # prepare opt_sid_mapping
            opt_sid_mappings = {mol_name: {"prot": [], "deprot": []} for mol_name in succeed_mols}
            opt_debug_mapping = {mol_name: {"prot": {}, "deprot": {}} for mol_name in succeed_mols}
            
            prot_idxs = num_opt_confs[0::2]
            deprot_idxs = num_opt_confs[1::2]

            last_deprot_idx = 0
            
            for mol_name, prot_idx, deprot_idx in zip(succeed_mols, prot_idxs, deprot_idxs):
                prot_task_ids = task_ids[last_deprot_idx:prot_idx]
                deprot_task_ids = task_ids[prot_idx:deprot_idx]
                last_deprot_idx = deprot_idx

                opt_sid_mappings[mol_name]["prot"] = prot_task_ids
                opt_debug_mapping[mol_name]["prot"] = {f"conf_{idx}" : task_id for idx, task_id in enumerate(prot_task_ids)}
                opt_sid_mappings[mol_name]["deprot"] = deprot_task_ids
                opt_debug_mapping[mol_name]["deprot"] = {f"conf_{idx}" : task_id for idx, task_id in enumerate(deprot_task_ids)}
                
            # dump all conf xyz and task_ids mapping for debug
            opt_debug_path = self.working_dir / "04_opt_debug.json"
            with open(opt_debug_path, 'w') as f:
                json.dump(opt_debug_mapping, f, indent=2)

            batch_job.wait()

            # check opt res
            num_mappings = len(opt_sid_mappings)
            failed_opt_tasks = {}
            failed_mols = []
            for mol_name, opt_sid_mapping in opt_sid_mappings.items():
                prot_idxs = opt_sid_mapping["prot"]
                deprot_idxs = opt_sid_mapping["deprot"]
                task_ids = prot_idxs + deprot_idxs
                mol_opt_dir = self.working_dir / mol_name / "04_opt_res"
                mol_opt_dir.mkdir(parents=True, exist_ok=True)

                batch_job.download_outputs(task_ids=task_ids, target_dir=str(mol_opt_dir))
                
                failed_prot_task_ids = []
                failed_deprot_task_ids = []
                for task_id in task_ids:
                    mol_opt_path = mol_opt_dir / task_id / "molecule_opt.xyz"
                    if not mol_opt_path.exists():
                        if task_id in prot_idxs:
                            opt_sid_mapping["prot"].remove(task_id)
                            failed_prot_task_ids.append(task_id)
                        else:
                            opt_sid_mapping["deprot"].remove(task_id)
                            failed_deprot_task_ids.append(task_id)
                
                if len(failed_prot_task_ids) > 0:
                    failed_opt_tasks[mol_name] = {}
                    failed_opt_tasks[mol_name]["failed_prot_task_ids"] = {conf_xyz : task_id for conf_xyz, task_id in opt_debug_mapping[mol_name]["prot"].items() if task_id in failed_prot_task_ids}
            
                if len(failed_deprot_task_ids) > 0:
                    if mol_name not in failed_opt_tasks:
                        failed_opt_tasks[mol_name] = {}
                    failed_opt_tasks[mol_name]["failed_deprot_task_ids"] = {conf_xyz : task_id for conf_xyz, task_id in opt_debug_mapping[mol_name]["deprot"].items() if task_id in failed_deprot_task_ids}

                if len(opt_sid_mapping["prot"]) == 0 or len(opt_sid_mapping["deprot"]) == 0:
                    failed_mols.append(mol_name)

            if len(failed_mols) > 0 or len(failed_opt_tasks) > 0:
                logger.info(f"failed opt tasks are dumped to {self.opt_failed_mol_path}")
                with open(self.opt_failed_mol_path, 'w') as f:
                    json.dump(failed_opt_tasks, f, indent=2)

                # rm failed_mols
                for failed_mol in failed_mols:
                    opt_sid_mappings.pop(failed_mol)

            num_mappings_check = len(opt_sid_mappings)
            assert num_mappings == num_mappings_check + len(failed_mols)

            # dump
            dump_json(self.batch_opt_json_path, opt_sid_mappings)

            batch_job.clear_molecules()

        # check empty tasks
        self._check_empty_tasks(opt_sid_mappings)

        return

    def _run_sp(self):
        assert self.gpu_qc_batch_job is not None
        batch_job = self.gpu_qc_batch_job

        if self.batch_sp_json_path.exists():
            logger.info("Skip step5: sp")
            sp_sid_mappings = load_json(self.batch_sp_json_path)
        else:
            # precheck and load
            opt_sid_mappings = load_json(self.batch_opt_json_path)
            mol_sel_smi_mapping = load_json(self.batch_stereo_assign_json_path)
            
            # load opt debug task_id mapping
            opt_debug_path = self.working_dir / "04_opt_debug.json"
            opt_debug_mapping = load_json(opt_debug_path)

            logger.info("Run step5: sp")
            total_ids = 0
            num_sp_idxs = []
            opt_mol_xyzs = []
            sp_configs = []
            for mol_name, opt_sid_mapping in opt_sid_mappings.items():
                _, _, prot_charge, deprot_charge = mol_sel_smi_mapping[mol_name]
                prot_sids = opt_sid_mapping["prot"]
                total_ids += len(prot_sids)
                num_sp_idxs.append(total_ids)

                deprot_sids = opt_sid_mapping["deprot"]
                total_ids += len(deprot_sids)
                num_sp_idxs.append(total_ids)

                for task_id in (prot_sids + deprot_sids):
                    opt_mol_path = self.working_dir / mol_name / "04_opt_res" / task_id / "molecule_opt.xyz"
                    opt_mol_xyzs.append(str(opt_mol_path))

                HA_sp_configs = [{**DEFAULT_SP_CONFIG, "charge": prot_charge} for _ in range(len(prot_sids))]
                A_sp_configs = [{**DEFAULT_SP_CONFIG, "charge": deprot_charge} for _ in range(len(deprot_sids))]

                sp_configs.extend(HA_sp_configs + A_sp_configs)

            batch_job.load_molecules(from_list=opt_mol_xyzs)
            assert num_sp_idxs[-1] == len(batch_job.molecules) == len(sp_configs)
            assert len(num_sp_idxs) % 2 == 0

            task_ids = batch_job.submit(task_type=TaskType.SP.value, task_config=sp_configs)
            logger.info(f"submit sp tasks with ids: {task_ids}")

            sp_sid_mappings = {mol_name: {"prot": [], "deprot": []} for mol_name in opt_sid_mappings.keys()}
            sp_debug_mapping = {mol_name: {"prot": {}, "deprot": {}} for mol_name in opt_sid_mappings.keys()}
            prot_idxs = num_sp_idxs[0::2]
            deprot_idxs = num_sp_idxs[1::2]

            last_deprot_idx = 0
            for mol_name, prot_idx, deprot_idx in zip(opt_sid_mappings.keys(), prot_idxs, deprot_idxs):
                prot_task_ids = task_ids[last_deprot_idx:prot_idx]
                deprot_task_ids = task_ids[prot_idx:deprot_idx]
                last_deprot_idx = deprot_idx

                opt_prot_task_ids = opt_sid_mappings[mol_name]["prot"]
                opt_deprot_task_ids = opt_sid_mappings[mol_name]["deprot"]
                # filter conf xyz
                opt_prot_conf_names = [conf_name for conf_name, task_id in opt_debug_mapping[mol_name]["prot"].items() if task_id in opt_prot_task_ids]
                opt_deprot_conf_names = [conf_name for conf_name, task_id in opt_debug_mapping[mol_name]["deprot"].items() if task_id in opt_deprot_task_ids]
                
                sp_sid_mappings[mol_name]["prot"] = prot_task_ids
                sp_debug_mapping[mol_name]["prot"] = dict(zip(opt_prot_conf_names, prot_task_ids))
                sp_sid_mappings[mol_name]["deprot"] = deprot_task_ids
                sp_debug_mapping[mol_name]["deprot"] = dict(zip(opt_deprot_conf_names, deprot_task_ids))
                
            # dump all conf xyz and task_ids mapping for debug
            sp_debug_path = self.working_dir / "05_sp_debug.json"
            with open(sp_debug_path, 'w') as f:
                json.dump(sp_debug_mapping, f, indent=2)

            batch_job.wait()

            # check sp res
            num_mappings = len(sp_sid_mappings)
            failed_sp_tasks = {}
            failed_mols = []
            for mol_name, sp_sid_mapping in sp_sid_mappings.items():
                prot_idxs = sp_sid_mapping["prot"]
                deprot_idxs = sp_sid_mapping["deprot"]
                task_ids = prot_idxs + deprot_idxs
                mol_sp_dir = self.working_dir / mol_name / "05_sp_res"
                mol_sp_dir.mkdir(parents=True, exist_ok=True)

                batch_job.download_outputs(task_ids=task_ids, target_dir=str(mol_sp_dir))

                failed_prot_task_ids = []
                failed_deprot_task_ids = []
                for task_id in task_ids:
                    mol_sp_path = mol_sp_dir / task_id / "molecule_pyscf.h5"
                    if not mol_sp_path.exists():
                        if task_id in prot_idxs:
                            sp_sid_mapping["prot"].remove(task_id)
                            failed_prot_task_ids.append(task_id)
                        else:
                            sp_sid_mapping["deprot"].remove(task_id)
                            failed_deprot_task_ids.append(task_id)

                if len(failed_prot_task_ids) > 0:
                    failed_sp_tasks[mol_name] = {}
                    failed_sp_tasks[mol_name]["failed_prot_task_ids"] = {conf_xyz : task_id for conf_xyz, task_id in sp_debug_mapping[mol_name]["prot"].items() if task_id in failed_prot_task_ids}
                
                if len(failed_deprot_task_ids) > 0:
                    if mol_name not in failed_sp_tasks:
                        failed_sp_tasks[mol_name] = {}
                    failed_sp_tasks[mol_name]["failed_deprot_task_ids"] = {conf_xyz : task_id for conf_xyz, task_id in sp_debug_mapping[mol_name]["deprot"].items() if task_id in failed_deprot_task_ids}
                
                if len(sp_sid_mapping["prot"]) == 0 or len(sp_sid_mapping["deprot"]) == 0:
                    failed_mols.append(mol_name)

            if len(failed_mols) > 0 or len(failed_sp_tasks) > 0:
                logger.info(f"failed sp tasks are dumped to {self.sp_failed_mol_path}")
                with open(self.sp_failed_mol_path, "w") as f:
                    json.dump(failed_sp_tasks, f, indent=2)

                # rm failed mols
                for failed_mol in failed_mols:
                    sp_sid_mappings.pop(failed_mol)

            num_mappings_check = len(sp_sid_mappings)
            assert num_mappings == num_mappings_check + len(failed_mols)

            # dump
            dump_json(self.batch_sp_json_path, sp_sid_mappings)

            batch_job.clear_molecules()

        # check empty tasks
        self._check_empty_tasks(sp_sid_mappings)

        return

    def _run_pka_predict(self):
        assert self.cpu_qc_batch_job is not None
        batch_job = self.cpu_qc_batch_job

        # precheck and load
        mol_sel_smi_mapping = load_json(self.batch_stereo_assign_json_path)
        opt_sid_mappings = load_json(self.batch_opt_json_path)
        sp_sid_mappings = load_json(self.batch_sp_json_path)

        task_configs = []
        for mol_name, sp_sid_mapping in sp_sid_mappings.items():
            smi_HA, smi_A_, *_ = mol_sel_smi_mapping[mol_name]
            select_smis = [smi_HA, smi_A_]
            batch_job.load_smiles(with_molecule_names=[mol_name], from_list=[select_smis])

            opt_sid_mapping = opt_sid_mappings[mol_name]

            task_configs.append({"opt_sid_mapping": opt_sid_mapping, "sp_sid_mapping": sp_sid_mapping})

        assert len(batch_job.molecules) == len(task_configs), f"len({batch_job.molecules}) != len({task_configs})"

        task_ids = batch_job.submit(task_type=TaskType.PKA_PREDICT.value, task_config=task_configs)
        pka_predict_debug_path = self.working_dir / "06_pka_predict_debug.json"
        pka_predict_mapping = dict(zip(sp_sid_mappings.keys(), task_ids))
        with open(pka_predict_debug_path, 'w') as f:
            json.dump(pka_predict_mapping, f, indent=2) 
        logger.info(f"submit pka-predict tasks with ids: {pka_predict_mapping}")

        batch_job.wait()

        # collect res
        failed_mols = {}
        for mol_name, task_id in zip(sp_sid_mappings.keys(), task_ids):
            mol_dir = self.working_dir / mol_name
            mol_dir.mkdir(exist_ok=True)
            pka_predict_dir = mol_dir / "06_pka_predict_res"
            pka_predict_dir.mkdir(exist_ok=True)

            batch_job.download_outputs(task_ids=[task_id], target_dir=str(pka_predict_dir))
            micro_pka_json_path = pka_predict_dir / task_id / "micro_pKa_info.json"

            if not micro_pka_json_path.exists():
                failed_mols[mol_name] = task_id
            else:
                with open(micro_pka_json_path, "r") as f:
                    self.batch_pka_result[mol_name] = json.load(f)

        if len(failed_mols) > 0:
            logger.info(f"the following mols failed at pka_predict: {failed_mols} dump to {self.pka_predict_failed_mol_path}")
            with open(self.pka_predict_failed_mol_path, 'w') as f:
                json.dump(failed_mols, f, indent=2)
        else:
            pka_predict_done_flag_path = self.working_dir / "06_pka_predict_success.txt"
            with open(pka_predict_done_flag_path, 'w') as f:
                f.write("All micro-pKa datapoints completed the workflow calculation successfully.")

        batch_job.clear_molecules()

    def run(self, last_step_num: int = None):
        logger.info("start run pkaPka micropka calculation")
        last_step_num = last_step_num if last_step_num is not None else len(self.steps)
        assert 0 < last_step_num <= 6, last_step_num
        self.is_full_wf = True if last_step_num == 6 else False

        for step in range(0, last_step_num):
            self.steps[step]()

        logger.info("Done!")

    def get_result(self):
        logger.info("get successful pkaPka micropka calculation results")
        return self.batch_pka_result

if __name__ == "__main__":
    parser = ap.ArgumentParser("MicroPKA Workflow using qcclient")
    parser.add_argument("--csv",
                        required=True,
                        type=str,
                        help="pkaPka MicroPka csv file with molecule name, protonated smiles, deprotonated smiles")
    parser.add_argument("--config_path", required=True, type=str, help="pkaPka MicroPka config JSON path")
    parser.add_argument("--workflow_dir", required=True, type=str, help="root directory of pkaPka MicroPka workflow")
    parser.add_argument("--last_step_num", type=int, help="the order number of last, choose from 1 to 6")
    args = parser.parse_args()

    config_path = os.path.abspath(args.config_path)
    assert os.path.exists(config_path), f"{config_path} does not exist"

    csv_path = os.path.abspath(args.csv)
    assert os.path.exists(csv_path), f"{csv_path} does not exist"

    working_dir = os.path.abspath(args.workflow_dir)
    os.makedirs(working_dir, exist_ok=True)

    # load molecule_name, protonated_smiles, deprotnated_smiles
    target_cols = ["molecule_names", "protonated_smiles", "deprotonated_smiles"]
    data = pd.read_csv(csv_path, header=0, delimiter=",", usecols=lambda x: x in target_cols)

    # load config
    with open(config_path, 'r') as f:
        config = json.load(f)

    micro_pka_cfg = MicroPkaConfig(**{**config, **data.to_dict(orient='list')})
    logger.info(f"run micro_pka calculation with qcclient with cfg: {micro_pka_cfg}")

    # dump pkaPka job config
    micro_pka_cfg.to_json(working_dir)

    batch_micro_pka_executor = BatchMicroPkaExecutor(working_dir, micro_pka_cfg)
    batch_micro_pka_executor.run(args.last_step_num)
    
    if batch_micro_pka_executor.is_full_wf:
        result = batch_micro_pka_executor.get_result()
        # Convert dict of dicts to DataFrame with proper column structure
        rows = []
        for mol_name, mol_data in result.items():
            row = {'molecule_name': mol_name}
            row.update(mol_data)
            rows.append(row)
        
        df = pd.DataFrame(rows)
        batch_result_file = os.path.join(working_dir, "batch_result.csv")
        df.to_csv(batch_result_file, index=False)
    
        logger.info(f"successful results output to {batch_result_file}")
