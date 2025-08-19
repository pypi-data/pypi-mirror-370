import os
from loguru import logger

from syndrilla.utils import call_func_from_yaml, get_path


def create_check(yaml_path: str=None, **kwargs):
    """
    This function creates a logical check from a '.check.yaml' file.
    """
    header = 'check'
    func_name = 'check_type'
    logger.info(f'Creating logical error check class from <{get_path(yaml_path)}>.')
    output = call_func_from_yaml(yaml_path, header, func_name, os.path.dirname(__file__), **kwargs)
    logger.info(f'Creating logical error check class complete.')
    return output

