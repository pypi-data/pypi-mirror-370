"""
This module contains configuration related commands for the QC client.
"""
import os
import yaml
from getpass import getpass


def configure(args):
    config_path = os.path.expanduser('~/.volcqc.yaml')
    
    # If the configuration file exists, read and display the current configuration
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file) or {}
        
        print('Current configuration:')
        if 'ak' in config:
            ak = config['ak']
            print(f'  AK: {ak[:6]}******{ak[-6:]}')
        if 'sk' in config:
            sk = config['sk']
            print(f'  SK: {sk[:6]}******{sk[-6:]}')
        if 'qc_service_id' in config:
            print(f'  QC Service ID: {config["qc_service_id"]}')
        print('\nPress Enter to keep the current value, or enter a new value to replace it.')
    else:
        config = {}

    # Interactive input
    ak = getpass('Enter AK (at least 12 characters): ') or config.get('ak', '')
    while len(ak) < 12:
        print('AK length is insufficient. Please re-enter.')
        ak = getpass('Enter AK (at least 12 characters): ') or config.get('ak', '')

    sk = getpass('Enter SK (at least 12 characters): ') or config.get('sk', '')
    while len(sk) < 12:
        print('SK length is insufficient. Please re-enter.')
        sk = getpass('Enter SK (at least 12 characters): ') or config.get('sk', '')

    qc_service_id = input('Enter QC Service ID: ') or config.get('qc_service_id', '')

    # save configuration file.
    config.update({
        'ak': ak,
        'sk': sk,
    })
    if qc_service_id:
        config['qc_service_id'] = qc_service_id

    with open(config_path, 'w') as config_file:
        yaml.dump(config, config_file)
    print(f'\nConfiguration has been saved to {config_path}')
