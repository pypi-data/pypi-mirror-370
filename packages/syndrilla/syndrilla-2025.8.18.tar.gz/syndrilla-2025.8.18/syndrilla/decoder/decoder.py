import os
import yaml, copy
from loguru import logger

from syndrilla.utils import call_func_from_cfg, get_path, read_yaml, check_yaml_header


def create_decoder(yaml_path: str=None, **kwargs):
    """
    This function creates a decoder from a '.decoder.yaml' file.
    """
    header = 'decoder'
    func_name = 'algorithm'
    logger.info(f'Creating decoder class from <{get_path(yaml_path)}>.')
    # output = call_func_from_yaml(yaml_path, header, func_name, os.path.dirname(__file__), **kwargs)
    # logger.info(f'Creating decoder class complete.')
    full_path = get_path(yaml_path)
    load_cfg = read_yaml(full_path)

    # Check YAML header
    check_yaml_header(load_cfg, header, full_path)

    # Get decoder config
    dec_cfg = load_cfg[header]

    # Read algorithm(s)
    algorithms = dec_cfg[func_name]
    if isinstance(algorithms, str):
        algorithms = [algorithms]  # wrap single decoder into a list

    # Create one decoder per algorithm
    decoders = []
    for algo in algorithms:
        dec_cfg_copy = dec_cfg.copy()
        dec_cfg_copy[func_name] = algo
        decoder = call_func_from_cfg(dec_cfg_copy, header, func_name, os.path.dirname(__file__), **kwargs)
        decoders.append(decoder)

    return decoders