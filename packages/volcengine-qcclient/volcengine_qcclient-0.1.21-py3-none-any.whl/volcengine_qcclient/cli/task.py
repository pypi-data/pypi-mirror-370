"""
This module contains task related commands for the QC client.
"""
from volcengine_qcclient import QcService, QcBatchJob
from prettytable import PrettyTable

from .utils import check_config


@check_config(['ak', 'sk', 'qc_service_id'])
def list_tasks(args, qc_config=None):
    """List all QcTasks of a QcService"""
    assert qc_config is not None, "QC configuration is not set. Please run 'volcqc configure' first."

    svc = QcService()
    svc.set_ak(qc_config['ak'])
    svc.set_sk(qc_config['sk'])
    qc_service_id = qc_config['qc_service_id']
    
    params = {
        'PageSize': args.page_size,
        'PageNumber': args.page_num,
        'QcServiceId': qc_service_id,   
    }
    if isinstance(args.label, str) and args.label.strip() != '':
        params["Label"] = args.label.strip()
#    if type(args.filter) is str and args.filter.strip() != '':
#        params['NameContains'] = args.filter.strip()
    if hasattr(args, 'ids') and args.ids and isinstance(args.ids, list) and all(isinstance(i, str) for i in args.ids):
        params['Ids'] = args.ids
    result = svc.list_qc_tasks(params=params)    
    tasks = result.get('Items', [])
    if not tasks:
        print("No tasks found.")
        return
    
    full_columns = args.wide
    table = PrettyTable()
    field_names = ["TaskID", "Label", "TaskType", "Status", "MoleculeName"]
    if full_columns:
        field_names.extend(["CreateTime", "StartTime", "EndTime"])
    if args.show_config:
        field_names.extend(["TaskConfig"])
    table.field_names = field_names
    for task in tasks:
        fields = [
            task.get('Id', ''),
            task.get('Label', ''),
            task.get('TaskType', ''),
            task.get('Status', ''),
            task.get('MoleculeName', ''),
        ]
        if full_columns:
            fields.extend([
                task.get('CreateTime', ''),
                task.get('StartTime', ''),
                task.get('EndTime', '')
            ])
        if args.show_config:
            fields.extend([task.get('TaskConfig', '')])
        table.add_row(fields)
    print(table)
    print('cmd to show more tasks:\n    volcqc task list --page-size 20 --page-num 2')

@check_config(['ak', 'sk', 'qc_service_id'])
def download_task_outputs(args, qc_config=None):
    assert qc_config is not None, "QC configuration is not set. Please run 'volcqc configure' first."

    task_ids = args.task_ids
    if args.id is not None:
        task_ids.append(args.id)
        print(f'''The option --id is deprecated. Please use the following command instead:
    volcqc task download {args.id}
''')
    if not task_ids:
        print('Error: Please specify at least one task ID.')
        exit(1)

    label = args.label
    if not label:
        svc = QcService()
        svc.set_ak(qc_config['ak'])
        svc.set_sk(qc_config['sk'])
        qc_service_id = qc_config['qc_service_id']

        params = {
            'QcServiceId': qc_service_id,
            'Ids': task_ids,
        }
        result = svc.list_qc_tasks(params=params)
        tasks = result.get('Items', [])
        if not tasks:
            print(f"Tasks {task_ids} not found.")
            return
        labels = set(t['Label'] for t in tasks)

    label = list(labels)[0]
    batch_job = QcBatchJob(
        ak=qc_config['ak'], sk=qc_config['sk'], qc_service_id=qc_service_id, label=label
    )

    print(f'Downloading {task_ids} ...')
    batch_job.wait(task_ids=task_ids)
    batch_job.download_outputs(task_ids, target_dir=args.target_dir,
                               #with_molecule_name=True,
                               overwrite_exists=args.allow_overwritten)
