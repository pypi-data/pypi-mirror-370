"""
This module contains service related commands for the QC client.
"""
from volcengine_qcclient import QcService
from prettytable import PrettyTable

from .utils import check_config


@check_config(['ak', 'sk'])
def list_services(args, qc_config=None):
    """List all QC services"""
    assert qc_config is not None, "QC configuration is not set. Please run 'volcqc configure' first."

    svc = QcService()
    svc.set_ak(qc_config['ak'])
    svc.set_sk(qc_config['sk'])
    
    params = {
        'PageSize': args.page_size,
        'PageNumber': args.page_num
    }
    if type(args.filter) is str and args.filter.strip() != '':
        params['NameContains'] = args.filter.strip()
    if hasattr(args, 'ids') and args.ids and isinstance(args.ids, list) and all(isinstance(i, str) for i in args.ids):
        params['Ids'] = args.ids
    result = svc.list_qc_services(params=params)    
    services = result.get('Items', [])
    if not services:
        print("No services found.")
        return

    full_columns = args.wide
    table = PrettyTable()
    field_names = ["ServiceId", "Name", "Description", "ServiceType"]
    if full_columns:
        field_names.extend(["Status", "TaskSummary", "Containers", "CreateTime", "UpdateTime"])
    table.field_names = field_names
    for service in services:
        description = service.get('Description', '')
        if len(description) > 50:
            description = description[:47] + '...'
        fields = [
            service.get('Id', ''),
            service.get('Name', ''),
            description,
            service.get('ServiceType', '')
        ]
        if full_columns:
            containers = {
                "Min": service.get('Min', None),
                "Max": service.get('Max', None),
                "Desired": service.get('Desired', None),
                "Current": service.get('Current', None),
            }
            fields.extend([
                service.get('Status', ''),
                service.get('TasksSummary', ''),
                containers,
                service.get('CreateTime', ''),
                service.get('UpdateTime', '')
            ])
        table.add_row(fields)
    print(table)
