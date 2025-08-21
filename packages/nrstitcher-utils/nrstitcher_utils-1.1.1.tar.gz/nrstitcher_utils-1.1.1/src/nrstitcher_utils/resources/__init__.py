import sys
from nrstitcher_utils.resources import config_files

if sys.version_info < (3, 9):
    import importlib_resources
else:
    import importlib.resources as importlib_resources


def get_config_file(file_name):
    return importlib_resources.files(config_files) / file_name
