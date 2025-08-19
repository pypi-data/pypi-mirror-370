import torch

from loguru import logger


class create():
    """
    This class creates a syndrome.
    """
    def __init__(self, syndrome_cfg, **kwargs) -> None:
        self.syndrome_cfg = syndrome_cfg


    def measure_syndrome(self, error, decoder):
        logger.info(f'Measuring syndrome.')
        # for dummy column cases
        dummy_column = torch.zeros([error.shape[0],1], dtype=error.dtype, device=error.device)
        error = torch.cat((error, dummy_column), dim=1)

        v_c_col = decoder.V_c_col.to(error.device)
        syndrome = error[:, v_c_col].sum(dim = 2)
        syndrome = torch.where((syndrome%2) > 0, 1, 0)
        logger.info(f'Syndrome measurement complete.')
        return syndrome
    
