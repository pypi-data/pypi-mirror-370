import os

from loguru import logger

from syndrilla.utils import call_func_from_yaml, get_path


def create_error_model(yaml_path: str=None, **kwargs):
    """
    This function creates an error model from a '.error.yaml' file.
    """
    header = 'error'
    func_name = 'model'
    logger.info(f'Creating error model class from <{get_path(yaml_path)}>.')
    output = call_func_from_yaml(yaml_path, header, func_name, os.path.dirname(__file__), **kwargs)
    logger.info(f'Creating error model class complete.')
    return output

