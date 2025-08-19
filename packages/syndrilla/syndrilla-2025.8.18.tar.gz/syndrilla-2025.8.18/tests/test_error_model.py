import torch
import sys, os, time
import numpy as np
from loguru import logger

sys.path.append(os.getcwd())

from syndrilla.decoder import create_decoder
from syndrilla.error_model import create_error_model
from syndrilla.syndrome import create_syndrome
from syndrilla.metric import report_metric
from syndrilla.logical_check import create_check


def test_error_model():
    # create decoder
    decoders = create_decoder(yaml_path='examples/txt/bp_hx.decoder.yaml')
    
    decoder = decoders[0]
    decoder.eval()

    sample_size = 10000
    batch_size = 1000
    shape = decoder.H_shape
    dtype = decoder.dtype

    benchmark = 0.0005
    zero_qubits = torch.zeros([sample_size, shape[1]], dtype=dtype)
    error_model = create_error_model(yaml_path='examples/txt/bsc.error.yaml')
    error_vector, error_dataloader = error_model.inject_error(zero_qubits, batch_size)

    avg_error_rate = torch.mean(torch.sum(error_vector, 1) / shape[1])
    assert avg_error_rate - 0.05 <= benchmark, 'the different is too higher when p is 0.05'

    err_range = np.linspace(0.01, 0.1, num=10)
    for err_rate in err_range:
        zero_qubits = torch.zeros([sample_size, shape[1]], dtype=dtype)
        error_model.rate = err_rate
        error_vector, error_dataloader = error_model.inject_error(zero_qubits, batch_size)

        avg_error_rate = torch.mean(torch.sum(error_vector, 1) / shape[1])
        assert avg_error_rate - err_rate <= benchmark, 'the different is too higher when p is {err_rate}'


if __name__ == '__main__':
    test_error_model()