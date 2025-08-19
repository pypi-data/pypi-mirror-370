import torch
import re
import sys, os, time
import pyfiglet, argparse, time
import numpy as np
import csv
import yaml
import subprocess
from loguru import logger
from syndrilla.utils import bcolors
from syndrilla.decoder import create_decoder
from syndrilla.error_model import create_error_model
from syndrilla.syndrome import create_syndrome
from syndrilla.metric import report_metric, save_metric, compute_avg_metrics, load_checkpoint_yaml
from syndrilla.logical_check import create_check


def parse_commandline_args():
    """
    parse command line inputs
    """
    parser = argparse.ArgumentParser(
        description='A PyTorch-based numerical simulator for decoders in quantum error correction.')
    parser.add_argument('-r', '--run_dir', type=str, default='tests/test_outputs',
                        help = 'Run directory to store outputs.')
    parser.add_argument('-d', '--decoder_yaml', type=str, default=None,
                        help = 'Path to decoder yaml.')
    parser.add_argument('-e', '--error_yaml', type=str, default=None,
                        help = 'Path to error model yaml.')
    parser.add_argument('-c', '--logical_yaml', type=str, default=None,
                        help = 'Path to logical error check yaml.')
    parser.add_argument('-s', '--syndrome_yaml', type=str, default=None,
                        help = 'Path to syndrome yaml.')
    parser.add_argument('-ckpt', '--checkpoint_yaml', type=str, default=None,
                        help = 'Path to checkpoint result yaml to resume from.')
    parser.add_argument('-bs', '--batch_size', type=int, default=10000,
                        help = 'Number of samples run each batch.')
    parser.add_argument('-te', '--target_error', type=int, default=100,
                        help = 'Total number of errors to stop decoding.')
    parser.add_argument('-l', '--log_level', type=str, default='INFO',
                        help = 'Level of logger.')

    return parser.parse_args()


def save_metrics_to_csv(csv_path, row_dict, fieldnames):
    """
    Save one row of metrics to a CSV file. Creates a new file with a header
    if one doesn't already exist, otherwise appends to the existing file.
    """
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)


def main():
    args = parse_commandline_args()
    
    # set up output log
    logger.remove()
    output_log = args.run_dir + '/main' + '-' + str(time.time()) + '.log'
    logger.add(output_log, level=args.log_level)

    # set up banner
    ascii_banner = pyfiglet.figlet_format('SYNDRILLA')
    print(bcolors.Magenta + ascii_banner + bcolors.ENDC)
    ascii_banner = pyfiglet.figlet_format('UnaryLab')
    print(bcolors.Yellow + ascii_banner + bcolors.ENDC)
    ascii_banner = pyfiglet.figlet_format('https://github.com/UnaryLab/syndrilla', font='term')
    print(bcolors.UNDERLINE + bcolors.Green + ascii_banner + bcolors.ENDC)

    logger.success(f'\n----------------------------------------------\nStep 1: Create decoder\n----------------------------------------------')
    decoders = create_decoder(args.decoder_yaml)
    
    num_decoders = len(decoders)
    algo_name = []
    for decoder in decoders:
        decoder.eval()
        algo_name.append(decoder.algo)
    shape = decoders[0].H_shape
    dtype = decoders[0].dtype
    decoder_device = decoders[0].device
    H_matrix = decoders[0].H_matrix
    
    if decoders[0].check_type.lower() == 'hx':
        H_file_name = decoders[0].Hx_matrix.path
        l_matrix = decoders[0].lx_matrix
    else:
        H_file_name = decoders[0].Hz_matrix.path
        l_matrix = decoders[0].lz_matrix

    num_err = 0
    num_batches = 0

    e_v_all = [torch.empty((0, shape[1]), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
    e_all = torch.empty((0, shape[1]), dtype=dtype, device=decoder_device)
    
    converge_all = [torch.empty((0), dtype=dtype, device=decoder_device) for _ in range(num_decoders+1)]
    iter_all = [torch.empty((0), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
    time_iter_all = [[] for _ in range(num_decoders)]

    check = [[]for _ in range(num_decoders)]
    total_time_all = [0.0 for _ in range(num_decoders)]
    average_time_sample_all = [0.0 for _ in range(num_decoders)]
    average_iter_all = [0.0 for _ in range(num_decoders)]
    average_time_sample_iter_all = [0.0 for _ in range(num_decoders)]
    data_qubit_acc_all = [0.0 for _ in range(num_decoders)]
    data_frame_error_rate_all = [0.0 for _ in range(num_decoders)]
    synd_frame_error_rate_all = [0.0 for _ in range(num_decoders)]
    correction_acc_all = [0.0 for _ in range(num_decoders)]
    logical_error_rate_all = [0.0 for _ in range(num_decoders)]
    invoke_rate_all = [0.0 for _ in range(num_decoders)]
    converge_fail_all = [0.0 for _ in range(num_decoders)]
    converge_succ_all = [0.0 for _ in range(num_decoders)]

    logger.success(f'\n----------------------------------------------\nStep 2: Create error model\n----------------------------------------------')
    error_model = create_error_model(args.error_yaml)

    logger.success(f'\n----------------------------------------------\nStep 3: Check checkpoint file\n----------------------------------------------')
    # To check whether there is a resume yaml
    if args.checkpoint_yaml is not None:
        if not os.path.isfile(args.checkpoint_yaml):
            raise FileNotFoundError(f'Checkpoint file not found: {args.checkpoint_yaml}')
        total_time_all, average_time_sample_all, average_iter_all, average_time_sample_iter_all, data_qubit_acc_all, data_frame_error_rate_all, \
            synd_frame_error_rate_all, correction_acc_all, logical_error_rate_all, invoke_rate_all, converge_fail_all, converge_succ_all, num_err, \
                batch_size, target_error, ckpt_dtype, physical_error_rate, batch_count, ckpt_H = load_checkpoint_yaml(args.checkpoint_yaml)
        if batch_size != args.batch_size:
            raise FileNotFoundError(f'Checkpoint file not match on batch size: ckpt({batch_size}), input({args.batch_size})')
        elif target_error != args.target_error:
            raise FileNotFoundError(f'Checkpoint file not match on target error: ckpt({target_error}), input({args.target_error})')
        elif ckpt_dtype != str(dtype):
            raise FileNotFoundError(f'Checkpoint file not match on data type: ckpt({ckpt_dtype}), input({dtype})')
        elif float(physical_error_rate) != float(error_model.rate):
            raise FileNotFoundError(f'Checkpoint file not match on physical error rate: ckpt({float(physical_error_rate)}), input({float(error_model.rate)})')
        elif ckpt_H != H_file_name:
            raise FileNotFoundError(f'Checkpoint file not match on H matrix file: ckpt({ckpt_H}), input({H_file_name})')
        num_batches = batch_count
    else:
        logger.info(f'No input Checkpoint file.')

    logger.success(f'\n----------------------------------------------\nStep 4: Create syndrome measurer\n----------------------------------------------')
    syndrome_generator = create_syndrome(args.syndrome_yaml)

    logger.success(f'\n----------------------------------------------\nStep 5: Create logical error checker\n----------------------------------------------')
    logical_check = create_check(args.logical_yaml)

    while num_err <= args.target_error:
        logger.success(f'\n----------------------------------------------\nStep 6: Generate error\n----------------------------------------------')
        e_v_all = [torch.empty((0, shape[1]), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
        e_all = torch.empty((0, shape[1]), dtype=dtype, device=decoder_device)
        
        converge_all = [torch.empty((0), dtype=dtype, device=decoder_device) for _ in range(num_decoders+1)]
        iter_all = [torch.empty((0), dtype=dtype, device=decoder_device) for _ in range(num_decoders)]
        time_iter_all = [[] for _ in range(num_decoders)]
        
        # create error
        zero_qubits = torch.zeros([args.batch_size, shape[1]], dtype=dtype)
        error_vector, error_dataloader = error_model.inject_error(zero_qubits, args.batch_size)
        num_batches += 1

        avg_error_rate = torch.mean(torch.sum(error_vector, 1) / shape[1])
        logger.info(f'Specified error rate <{error_model.rate}>.')
        logger.info(f'Generated error rate <{avg_error_rate}>.')
        
        for err, llr, _ in error_dataloader:
            logger.success(f'\n----------------------------------------------\nStep 7: Measure syndrome\n----------------------------------------------')
            # generate the syndrome for decoder
            err = err.to(e_all.device)
            e_all = torch.cat((e_all, err))
            synd = syndrome_generator.measure_syndrome(err, decoders[0])

            io_dict = {
                'synd': synd,
                'llr0': llr,
                'H_matrix': H_matrix
            }

            logger.success(f'\n----------------------------------------------\nStep 8: Decode\n----------------------------------------------')
            decoder_idx = 0
            if decoder_idx == 0:
            # first decoder
                start_time = time.time()
                io_dict = decoders[decoder_idx](io_dict)

                time_iter_all[decoder_idx].append(time.time() - start_time)
                
                e_v_all[decoder_idx] = torch.cat((e_v_all[decoder_idx], io_dict['e_v']), dim=0)
                iter_all[decoder_idx] = torch.cat((iter_all[decoder_idx], io_dict['iter']))
                converge_all[decoder_idx] = torch.cat((converge_all[decoder_idx], torch.zeros_like(io_dict['converge'])), dim=0)
                converge_all[decoder_idx+1] = torch.cat((converge_all[decoder_idx+1], io_dict['converge']), dim=0)
                decoder_idx += 1
            while decoder_idx < num_decoders:
                # second decoder
                start_time = time.time()
                io_dict = decoders[1](io_dict)
                
                time_iter_all[decoder_idx].append(time.time() - start_time)
                e_v_all[decoder_idx] = torch.cat((e_v_all[decoder_idx], io_dict['e_v']), dim=0)
                iter_all[decoder_idx] = torch.cat((iter_all[decoder_idx], io_dict['iter']))
                converge_all[decoder_idx+1] = torch.cat((converge_all[decoder_idx+1], io_dict['converge']), dim=0)
                decoder_idx += 1    

            logger.success(f'\n----------------------------------------------\nStep 9: Check logical error rate\n----------------------------------------------')

            check[0] = logical_check.check(e_v_all[0], e_all, l_matrix, converge_all[1])
            for i in range(1, num_decoders):
                check[i] = logical_check.check(e_v_all[i], e_all, l_matrix, converge_all[i+1])
            num_err += int(torch.sum(check[num_decoders-1]))
            logger.info(f'number of errors at the current batch {num_err}/{args.target_error}')

            # report metric
            logger.success(f'\n----------------------------------------------\nStep 10: Save log\n----------------------------------------------')
            for i in range(num_decoders):
                batch_total_time, batch_average_time_sample, batch_average_iter, batch_average_time_sample_iter, batch_data_qubit_acc, \
                    batch_data_frame_error_rate, batch_synd_frame_error_rate, batch_correction_acc, batch_logical_error_rate, \
                        batch_invoke_rate, batch_converge_fail, batch_converge_succ = report_metric(e_all, e_v_all[i], iter_all[i], time_iter_all[i], check[i], converge_all[i], converge_all[i+1], i)
                total_time_all[i] += batch_total_time
                average_time_sample_all[i] += batch_average_time_sample
                average_iter_all[i] += batch_average_iter
                average_time_sample_iter_all[i] += batch_average_time_sample_iter
                data_qubit_acc_all[i] += batch_data_qubit_acc
                data_frame_error_rate_all[i] += batch_data_frame_error_rate
                synd_frame_error_rate_all[i] += batch_synd_frame_error_rate
                correction_acc_all[i] += batch_correction_acc
                logical_error_rate_all[i] += batch_logical_error_rate
                invoke_rate_all[i] += batch_invoke_rate
                converge_fail_all[i] += batch_converge_fail
                converge_succ_all[i] += batch_converge_succ
            
            if num_batches % 100 == 0:
                all_metrics = []
                logger.success(f'\n----------------------------------------------\nStep 11: Save final log\n----------------------------------------------')
                for i in range(num_decoders):
                    total_time, average_time_sample, average_iter, average_time_sample_iter, data_qubit_acc, \
                        data_frame_error_rate, synd_frame_error_rate, correction_acc, \
                        logical_error_rate, invoke_rate, converge_fail, converge_succ = compute_avg_metrics(args.target_error, i, num_batches, total_time_all,
                                                                                        average_time_sample_all,
                                                                                        average_iter_all,
                                                                                        average_time_sample_iter_all,
                                                                                        data_qubit_acc_all,
                                                                                        data_frame_error_rate_all,
                                                                                        synd_frame_error_rate_all,
                                                                                        correction_acc_all,
                                                                                        logical_error_rate_all,
                                                                                        invoke_rate_all,
                                                                                        converge_fail_all,
                                                                                        converge_succ_all)
                    
                    metrics_dict = {
                        'algorithm': algo_name[i],
                        'total_time': total_time,
                        'average_time_sample': average_time_sample,
                        'average_iter': average_iter,
                        'average_time_sample_iter': average_time_sample_iter,
                        'data_qubit_acc': data_qubit_acc,
                        'data_frame_error_rate': data_frame_error_rate,
                        'synd_frame_error_rate': synd_frame_error_rate,
                        'correction_acc': correction_acc,
                        'logical_error_rate': logical_error_rate,
                        'invoke_rate': invoke_rate,
                        'converge_fail_rate': converge_fail,
                        'converge_succ_rate': converge_succ
                    }
                    all_metrics.append(metrics_dict)

                logger.success(f'Saved log to <{output_log}>.')

                logger.success(f'\n----------------------------------------------\nStep 12: Save final metrics\n----------------------------------------------')
                save_metric(all_metrics, args.run_dir + '/', args.batch_size, args.target_error, str(dtype), error_model.rate, num_batches, num_err, H_file_name)
            
                logger.success(f'Saved metric results to <{args.run_dir}>.')
    all_metrics = []
    logger.success(f'\n----------------------------------------------\nStep 11: Save final log\n----------------------------------------------')
    for i in range(num_decoders):
        total_time, average_time_sample, average_iter, average_time_sample_iter, data_qubit_acc, \
            data_frame_error_rate, synd_frame_error_rate, correction_acc, \
            logical_error_rate, invoke_rate, converge_fail, converge_succ = compute_avg_metrics(args.target_error, i, num_batches, total_time_all,
                                                                            average_time_sample_all,
                                                                            average_iter_all,
                                                                            average_time_sample_iter_all,
                                                                            data_qubit_acc_all,
                                                                            data_frame_error_rate_all,
                                                                            synd_frame_error_rate_all,
                                                                            correction_acc_all,
                                                                            logical_error_rate_all,
                                                                            invoke_rate_all,
                                                                            converge_fail_all,
                                                                            converge_succ_all)

        metrics_dict = {
            'algorithm': algo_name[i],
            'total_time': total_time,
            'average_time_sample': average_time_sample,
            'average_iter': average_iter,
            'average_time_sample_iter': average_time_sample_iter,
            'data_qubit_acc': data_qubit_acc,
            'data_frame_error_rate': data_frame_error_rate,
            'synd_frame_error_rate': synd_frame_error_rate,
            'correction_acc': correction_acc,
            'logical_error_rate': logical_error_rate,
            'invoke_rate': invoke_rate,
            'converge_fail_rate': converge_fail,
            'converge_succ_rate': converge_succ
        }
        all_metrics.append(metrics_dict)

    logger.success(f'Saved log to <{output_log}>.')

    logger.success(f'\n----------------------------------------------\nStep 12: Save final metrics\n----------------------------------------------')
    save_metric(all_metrics, args.run_dir + '/', args.batch_size, args.target_error, str(dtype), error_model.rate, num_batches, num_err, H_file_name)

    logger.success(f'Saved metric results to <{args.run_dir}>.')


if __name__ == '__main__':
    main()
