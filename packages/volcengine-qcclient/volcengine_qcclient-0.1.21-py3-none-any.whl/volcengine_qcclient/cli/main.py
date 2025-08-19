"""
This module is the entry point for the command - line interface of the QC client.
It parses command - line arguments and executes corresponding commands such as
configuring the client, listing jobs, removing jobs, stopping jobs, and downloading
job outputs.
"""
import argparse

from . import service, job, task, configure


def main():
    """
    The main function of the program, responsible for parsing command-line arguments and executing corresponding commands.
    Supported commands include configuration, listing jobs, removing jobs, stopping jobs, and downloading job outputs.
    """
    parser = argparse.ArgumentParser(prog='volcqc', description='Volcengine Quantum Chemistry Cli.')
    # Set default function to show help when no arguments provided
    parser.set_defaults(func=lambda _: parser.print_help())

    subparsers = parser.add_subparsers()
    # configure command
    configure_parser = subparsers.add_parser('config', help='Configure ak, sk and qc_service_id')
    configure_parser.add_argument('--ak', required=False, help='Access Key ID')
    configure_parser.add_argument('--sk', required=False, help='Secret Access Key')
    configure_parser.add_argument('--qc_service_id', required=False, help='QC Service ID')
    configure_parser.set_defaults(func=configure.configure)

    # service command
    svc_parser = subparsers.add_parser('service', help='Manage QC services')
    svc_parser.set_defaults(func=lambda _: svc_parser.print_help())
    svc_subparsers = svc_parser.add_subparsers()

    # service list command
    list_parser = svc_subparsers.add_parser('list', help='List all QC services')
    list_parser.add_argument('-f', '--filter', type=str, help='Filter output based on job name.')
    list_parser.add_argument('--ids', type=lambda x: [i.strip() for i in x.replace(',', ' ').split()], help='Filter by service IDs (comma or space separated).')
    list_parser.add_argument('-n', '--page-size', type=int, default=10, help='Number of items to show per page')
    list_parser.add_argument('-pn', '--page-num', type=int, default=1, help='Page number to show')
    list_parser.add_argument('-w', '--wide', action='store_true', help='Display additional columns in the output table.')
    list_parser.set_defaults(func=service.list_services)
    
    # job command
    job_parser = subparsers.add_parser('job', help='Manage QC jobs')
    job_parser.set_defaults(func=lambda _: job_parser.print_help())
    job_subparsers = job_parser.add_subparsers()

    # job list command
    job_list_parser = job_subparsers.add_parser('list', help='List jobs')
    job_list_parser.add_argument('-f', '--filter', type=str, help='Filter output based on job name.')
    job_list_parser.add_argument('--ids', type=lambda x: [i.strip() for i in x.replace(',', ' ').split()], help='Filter by service IDs (comma or space separated).')
    job_list_parser.add_argument('-n', '--page-size', type=int, default=10, help='Number of items to show per page')
    job_list_parser.add_argument('-pn', '--page-num', type=int, default=1, help='Page number to show')
    job_list_parser.add_argument('-w', '--wide', action='store_true', help='Display additional columns in the output table.')
    job_list_parser.set_defaults(func=job.list_jobs)
    
    # job stop command
    job_stop_parser = job_subparsers.add_parser('stop', help='Stop jobs.')
    job_stop_parser.add_argument('--name', '--label', dest='label', type=str, required=True, help='Job Name to stop.')
    job_stop_parser.set_defaults(func=job.stop_job)

    # job download command
    job_download_parser = job_subparsers.add_parser('download', help='Download job outputs.')
    job_download_parser.add_argument('--name', '--label', dest='label', type=str, required=True, help='Job Name to download.')
    job_download_parser.add_argument('--target-dir', type=str, required=False, help='Output directory to save job outputs.', default=None)
    job_download_parser.set_defaults(func=job.download_job_outputs)

    # TODO: job submit command (need tests.)
    job_submit_parser = job_subparsers.add_parser('submit', help='Submit a QC batchjob.',
                                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                                  description=r'''
When submitting job, the job config should include both the task_type and task_config fields.
For example, the config file for a single point calculation (task_type=sp) can be written

task_type:
  sp
task_config:
  basis: def2-tzvp
  xc: wb97m-d3bj
  with_thermo: true

If config file is not specified, the default config for task_type=sp calculation is

    charge: 0
    basis: def2-tzvpp
    xc: b3lyp
    grids: atom_grid: [99, 590]
    scf_conv_tol: 1e-10
    with_solvent: false
    with_grad: true
    with_hess: true
    with_dm: true
    with_chelpg: true
    with_dipole: true

The config for geometry optimization task_type=opt is

    charge: 0
    basis: def2-tzvpp
    xc: b3lyp
    disp: null
    grids: atom_grid: [99, 590]
    scf_conv_tol: 1e-10
    with_solvent: false

Then template of task_confign can be obtained using the command
    volcqc job show-template --task_type sp
    volcqc job show-template --task_type opt
    volcqc job show-template --task_type eda

''')
    job_submit_parser.add_argument('--name', '--label', dest='label', type=str, required=False, help='Job Name to submit.', default=None)
    job_submit_parser.add_argument('--task-type', type=str, required=False, help='Task Type to submit.', 
    choices=['sp', 'opt', 'eda', 'pysisyphus'])
    job_submit_parser.add_argument('--config', type=str, required=False, help='Job configuration file path. (in json format)')
    job_submit_parser.add_argument('--dryrun', action='store_true', help='Dryrun mode, test input.')
    job_submit_parser.add_argument('input', type=str, help='Input a .xyz file path or a folder path of .xyz files.')
    job_submit_parser.set_defaults(func=job.submit_job)

    job_tpl_parser = job_subparsers.add_parser('show-template', help='Print a job template for task_type.')
    job_tpl_parser.add_argument('--task-type', type=str, help='Task Type to dump.',
                                choices=['sp', 'opt', 'eda', 'pysisyphus'])
    job_tpl_parser.set_defaults(func=job.show_template)

    # task command
    task_parser = subparsers.add_parser('task', help='Manage QC tasks')
    task_parser.set_defaults(func=lambda _: task_parser.print_help())
    task_subparsers = task_parser.add_subparsers()

     # task list command
    task_list_parser = task_subparsers.add_parser('list', help='List all tasks')
    task_list_parser.add_argument('--ids', type=lambda x: [i.strip() for i in x.replace(',', ' ').split()], help='Filter by service IDs (comma or space separated).')
    task_list_parser.add_argument('-l', '--label', '--job-name', dest='label',
                                  type=str, required=False, default=None, help='Job ID/name/label of the task')
    #task_list_parser.add_argument('-f', '--filter', type=str, help='Filter output based on task name.')
    task_list_parser.add_argument('-n', '--page-size', type=int, default=10, help='Number of items to show per page')
    task_list_parser.add_argument('-pn', '--page-num', type=int, default=1, help='Page number to show')
    task_list_parser.add_argument('-w', '--wide', action='store_true', help='Display additional columns in the output table.')
    task_list_parser.add_argument('--show-config', action='store_true', help='Display task_config for each task.')
    task_list_parser.set_defaults(func=task.list_tasks)

     # task download command
    task_dl_parser = task_subparsers.add_parser('download', help='Download the output of a task')
    task_dl_parser.add_argument('--id', type=str, help='Task Id. (deprecated)')
    task_dl_parser.add_argument('task_ids', type=str, nargs='*', help='multiple TaskIDs..')
    task_dl_parser.add_argument('--label', type=str, required=False,
                                default=None, help='Job ID/name/label of the task')
    task_dl_parser.add_argument('--target-dir', type=str, required=False, help='Output directory', default=None)
    task_dl_parser.add_argument('--allow-overwritten', action='store_true', help='Overwrite existing files', default=None)
    task_dl_parser.set_defaults(func=task.download_task_outputs)

    try:
        args = parser.parse_args()
        args.func(args)
    except KeyboardInterrupt:
        print('\nInterrupt signal received, the program will exit...')


if __name__ == '__main__':
    main()
