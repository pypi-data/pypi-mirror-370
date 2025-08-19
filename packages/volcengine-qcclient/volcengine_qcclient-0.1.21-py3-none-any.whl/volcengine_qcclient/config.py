import os
import yaml

config_path = os.path.expanduser('~/.volcqc.yaml')
config_data = {}
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f.read())
        # case insensitive for keys in configuration
        config_data.update({k.lower(): v for k, v in config_data.items()})

if os.getenv('QC_SERVICE_ID'):
    config_data['qc_service_id'] = os.getenv('QC_SERVICE_ID')

def _read_env_then_config(key, default=None):
    if not config_data:
        return default
    val = os.getenv(key)
    if val:
        return val

    key = key.lower() # case insensitive for config keys
    # QC_XYZ or XYZ are both valid keys
    short_name = key[3:]
    if short_name in config_data:
        return config_data[short_name]
    return config_data.get(key, default)

PAGE_SIZE = int(_read_env_then_config('QC_PAGESIZE', 10))

TIMEOUT = _read_env_then_config('QC_TIMEOUT')
if TIMEOUT:
    TIMEOUT = float(TIMEOUT)

VALIDATE_TASK = int(_read_env_then_config('QC_VALIDATE_TASK', 0))

MAX_BATCH_SIZE = int(_read_env_then_config('QC_MAX_BATCH_SIZE', 100))

WAIT_DURATION = float(_read_env_then_config('QC_WAIT_DURATION', 5))

# Read versions from ~/.volcqc.yaml or environment variables
default_versions = config_data.get('versions', {})
default_versions.update(
    # Drop empty entries
    (k, v) for k, v in (
        ('pyscf', os.getenv('PYSCF_VERSION')),
        ('gpu4pyscf', os.getenv('GPU4PYSCF_VERSION')),
        ('volcengine-qcworker', os.getenv('QCWORKER_VERSION')),
    ) if v is not None)
default_versions = {k: str(v) for k, v in default_versions.items()}
