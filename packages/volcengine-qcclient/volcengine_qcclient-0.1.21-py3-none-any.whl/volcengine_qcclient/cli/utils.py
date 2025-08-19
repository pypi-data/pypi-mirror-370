from functools import wraps
import os
import yaml


def check_config(keys):
    """
    This decorator function is used to check if the configuration file exists and if the configuration items are complete.
    If the configuration file does not exist or the configuration items are incomplete, it will output the corresponding prompt message and return None.
    If the configuration file exists and the configuration items are complete, it will call the decorated function.

    :param f: The function to be decorated
    :return: The wrapped function
    """
    def checker(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            config_path = os.path.expanduser('~/.volcqc.yaml')
            if not os.path.exists(config_path):
                print('Please run volcqc configure first to complete the configuration.')
                return
            with open(config_path, 'r') as config_file:
                config = yaml.safe_load(config_file) or {}
            if not all(key in config and isinstance(config[key], str) and config[key].strip() for key in keys):
                print('The configuration file is incomplete. Please run `volcqc configure` to reconfigure.')
                return
            return f(qc_config=config, *args, **kwargs)
        return wrapper
    return checker
