import os

from loguru import logger

from syndrilla.utils import call_func_from_yaml, get_path


def create_parity_matrix(yaml_path: str=None, **kwargs):
    """
    This function creates a matrix from a '.matrix.yaml' file.
    """
    header = 'matrix'
    func_name = 'file_type'
    logger.info(f'Creating parity matrix class from <{get_path(yaml_path)}>.')
    output = call_func_from_yaml(yaml_path, header, func_name, os.path.dirname(__file__), **kwargs)
    logger.info(f'Complete.')
    return output

