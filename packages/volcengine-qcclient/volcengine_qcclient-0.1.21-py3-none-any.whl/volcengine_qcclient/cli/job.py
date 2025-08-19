"""
This module contains job related commands for the QC client.
"""
from pathlib import Path
import json
import yaml

from prettytable import PrettyTable
from volcengine_qcclient import QcService, QcBatchJob

from .utils import check_config


@check_config(['ak', 'sk', 'qc_service_id'])
def list_jobs(args, qc_config=None):
    assert qc_config is not None, "QC configuration is not set. Please run 'volcqc configure' first."

    svc = QcService()
    svc.set_ak(qc_config['ak'])
    svc.set_sk(qc_config['sk'])

    params = {
        'QcServiceId': qc_config['qc_service_id'],
        'PageSize': args.page_size,
        'PageNumber': args.page_num,
    }
    if type(args.filter) is str and args.filter.strip() != '':
        params['NameContains'] = args.filter.strip()

    result = svc.list_qc_batch_jobs(params=params)

    jobs = result.get('Items', [])
    if not jobs:
        print("No jobs found.")
        return

    full_columns = args.wide
    table = PrettyTable()
    field_names = ["Name/Label", "Status", "TaskSummary"]
    if full_columns:
        field_names.extend(["CreateTime", "UpdateTime"])
    table.field_names = field_names
    for job in jobs:
        fields = [
            job.get('Name', ''),
            job.get('Status', ''),
            job.get('TaskSummary', ''),
        ]
        if full_columns:
            fields.extend([
                job.get('CreateTime', ''),
                job.get('UpdateTime', '')
            ])
        table.add_row(fields)
    print(table)
    print('cmd to view tasks of individual jobs:\n    volcqc task list --label {job_id}')


@check_config(['ak', 'sk', 'qc_service_id'])
def stop_job(args, qc_config=None):
    assert qc_config is not None, "QC configuration is not set. Please run 'volcqc configure' first."

    batch_job = QcBatchJob(
        ak=qc_config['ak'], 
        sk=qc_config['sk'], 
        qc_service_id=qc_config['qc_service_id'], 
        label=args.label
    )
    batch_job.stop()
    print(f'Job {args.label} stopped.')

@check_config(['ak', 'sk', 'qc_service_id'])
def download_job_outputs(args, qc_config=None):
    assert qc_config is not None, "QC configuration is not set. Please run 'volcqc configure' first."

    batch_job = QcBatchJob(
        ak=qc_config['ak'], 
        sk=qc_config['sk'], 
        qc_service_id=qc_config['qc_service_id'], 
        label=args.label
    )
    print(f'Downloading job {args.label}...')
    batch_job.wait(download_outputs=True, target_dir=args.target_dir,
                   with_molecule_name=True)


@check_config(['ak', 'sk', 'qc_service_id'])
def submit_job(args, qc_config=None):
    assert qc_config is not None, "QC configuration is not set. Please run 'volcqc configure' first."

    input_file, input_dir = validate_input(args.input)
    task_type, task_config = validate_config(args.task_type, args.config)
    if args.dryrun:
        print('Job {job_name} not submitted in the dryrun mode')
        return

    batch_job = QcBatchJob(
        ak=qc_config['ak'],
        sk=qc_config['sk'],
        qc_service_id=qc_config['qc_service_id'],
        label=args.label
    )

    batch_job.load_molecules(from_dir=input_dir, from_file=input_file)

    task_ids = batch_job.submit(task_type=task_type, task_config=task_config)
    job_name = batch_job.get_label()
    print(f'Job {job_name} submitted with total {len(task_ids)} tasks.')

def show_template(args):
    from volcengine_qcclient.drivers import sp_validation, opt_validation, eda_validation
    task_type = args.task_type
    if task_type == 'sp':
        print(yaml.dump(sp_validation.default_config, default_flow_style=False))
    elif task_type == 'opt':
        print(yaml.dump(opt_validation.default_config, default_flow_style=False))
    elif task_type == 'eda':
        print(yaml.dump(eda_validation.default_config, default_flow_style=False))
    else:
        print(f'Template for {task_type} not available')


def validate_input(input: str) -> (str, str):
    path = Path(input)
    assert path.exists(), "Input {input} does not exist."
    
    if path.is_dir():
        return None, input
    elif path.is_file():
        return input, None
    else:
        assert False, "Input {input} is not a file or a directory."


def validate_config(task_type: str, config_path: str) -> dict:
    from volcengine_qcclient.drivers import sp_validation, opt_validation, eda_validation
    path = Path(config_path)
    assert path.exists(), "Config {config} does not exist."
    assert path.is_file(), "Config {config} is not a file."

    with open(config_path, 'r', encoding='utf-8') as f:
        task_config = yaml.safe_load(f)

    if task_type is None:
        # task_config can be defined in the configuration file.
        # In this case, task_type and task_config must be specified in the same
        # configuration file.
        assert 'task_type' in task_config, 'task_type must be specified in the config file.'
        assert 'task_config' in task_config, 'task_config must be specified in the config file.'
        task_type = task_config['task_type']
        task_config = task_config['task_config']
    elif 'task_type' in task_config:
        assert 'task_config' in task_config, 'task_config must be specified in the config file.'
        print(f'task_type {task_type} has been specified from command line. '
              f'the configuration in {config_path} is ignored')
        task_config = task_config['task_config']
    elif isinstance(task_type, str):
        pass
    else:
        print('task_type is not specified')
        exit(1)

    if task_type == 'sp':
        sp_validation.validate(task_config)
    elif task_type == 'opt':
        opt_validation.validate(task_config)
    elif task_type == 'eda':
        eda_validation.validate(task_config)
    return task_type, task_config
