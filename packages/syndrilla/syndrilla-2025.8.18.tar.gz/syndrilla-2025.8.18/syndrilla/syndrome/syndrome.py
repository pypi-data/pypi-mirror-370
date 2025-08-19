import os

from loguru import logger

from syndrilla.utils import call_func_from_yaml, get_path


def create_syndrome(yaml_path: str=None, **kwargs):
    """
    This function creates a syndrome from a '.syndrome.yaml' file.
    """
    header = 'syndrome'
    func_name = 'measure'
    logger.info(f'Creating syndrome class from <{get_path(yaml_path)}>.')
    output = call_func_from_yaml(yaml_path, header, func_name, os.path.dirname(__file__), **kwargs)
    logger.info(f'Creating syndrome class complete.')
    return output

