from pathlib import Path
import json
import os

# def get_config_value(config, keys, default_value=None):
#     value = config
#
#     for key in keys:
#         if isinstance(value, dict) and key in value:
#             value = value[key]
#         else:
#             return default_value
#
#     return value

def load_config(program_name):
    path_to_config_file = Path.home().joinpath('.config', program_name, 'config.json')

    if not os.path.isfile(path_to_config_file):
        return {}

    with open(path_to_config_file, encoding='utf-8', mode='r') as config_file:
        return json.load(config_file)
