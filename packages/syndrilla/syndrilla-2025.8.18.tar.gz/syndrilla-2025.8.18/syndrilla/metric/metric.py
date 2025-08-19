import torch, time, os
import yaml
import numpy as np

from loguru import logger


def report_metric(e_estimated, e_actual, iteration, time_iteration, check, converge, coverge_next, decode_idx):
    """
    This function reports the decoding iteration and accuracy.
    """
    
    logger.info(f'Reporting decoding metric for decoder {decode_idx}.')
    
    sample_size = e_estimated.shape[0]
    total_time = np.sum(time_iteration)
    logger.info(f'Total time for <{sample_size}> samples: {total_time} seconds.')

    average_iter = torch.mean(iteration).item()
    logger.info(f'Average iterations per sample: {average_iter}')

    if total_time == 0:
        average_time_sample = 0
        logger.info(f'Average time per sample: {average_time_sample} seconds.')
        
        average_time_sample_iter = 0
        logger.info(f'Average time per iteration: {average_time_sample_iter}')
    else:
        average_time_sample = total_time/sample_size
        logger.info(f'Average time per sample: {average_time_sample} seconds.')
        
        average_time_sample_iter = (average_time_sample/average_iter).item()
        logger.info(f'Average time per iteration: {average_time_sample_iter}')

    e_estimated = e_estimated.to(e_estimated.device)
    comparison = torch.unique(e_estimated == e_actual, return_counts=True)[1]
    if int(comparison.shape[0]) == 1:
        data_qubit_acc = 1.0
        logger.info(f'Data qubit accuracy: {data_qubit_acc}')
    else:
        data_qubit_acc = float(comparison[1]) / (float(comparison[1]) + float(comparison[0]))
        logger.info(f'Data qubit accuracy: {data_qubit_acc}')

    num_error = torch.sum(e_estimated != e_actual)
   
    total_ones = torch.sum((e_estimated == 1) | (e_actual == 1))
    if float(num_error) == 0:
        correction_acc = 1
        logger.info(f'Correction accuracy: {correction_acc}')
    else:
        correction_acc = 1 - float(num_error)/float(total_ones)
        logger.info(f'Correction accuracy: {correction_acc}')

    if torch.isinf(torch.sum(converge)) or torch.isnan(torch.sum(converge)):
        invoke_rate = 1.0
        logger.info(f'Decoder invoke rate: {invoke_rate}')
    else:
        if int(torch.sum(converge)) == 0:
            invoke_rate = 1.0
            logger.info(f'Decoder invoke rate: {invoke_rate}')
        else:
            invoke_rate = 1.0 - ((int(torch.sum(converge)))/(check.size()[0]))
            logger.info(f'Decoder invoke rate: {invoke_rate}')

    result = (e_estimated == e_actual).all(dim=1).int()
    num_correct = (result == 1).sum()
    num_incorrect = (result == 0).sum()
    if int(result.shape[0]) == 1:
        data_frame_error_rate = 0.0
        logger.info(f'Decoder data frame error rate: {data_frame_error_rate}')
    else:
        data_frame_error_rate = float(num_incorrect) / (float(num_incorrect) + float(num_correct))
        logger.info(f'Decoder data frame error rate: {data_frame_error_rate}')
    
    if torch.isinf(torch.sum(coverge_next)) or torch.isnan(torch.sum(coverge_next)):
        synd_frame_error_rate = 0
        logger.info(f'Decoder syndrome frame error rate: {synd_frame_error_rate}')
    else:
        if int(torch.sum(coverge_next)) == 0:
            synd_frame_error_rate = 0.0
            logger.info(f'Decoder syndrome frame error rate: {synd_frame_error_rate}')
        else:
            synd_frame_error_rate = ((check.size()[0] - int(torch.sum(coverge_next)))/(check.size()[0]))
            logger.info(f'Decoder syndrome frame error rate: {synd_frame_error_rate}')
    
    if int(torch.sum(check)) == 0:
        logical_error_rate = 0
        logger.info(f'Output logical error rate: {logical_error_rate}')
    else:
        logical_error_rate = (int(torch.sum(check))/(check.size()[0]))
        logger.info(f'Output logical error rate: {logical_error_rate}')
    
    converge_fail = torch.where((check == 1) & (coverge_next == 1), torch.tensor(1), torch.tensor(0))
    if int(torch.sum(converge_fail)) == 0:
        converge_fail_rate = 0
        logger.info(f'Output converge failure rate: {converge_fail_rate}')
    else:
        converge_fail_rate = (int(torch.sum(converge_fail))/(check.size()[0]))
        logger.info(f'Output converge failure rate: {converge_fail_rate}')
    
    converge_succ = torch.where((check == 0) & (coverge_next == 1), torch.tensor(1), torch.tensor(0))
    if int(torch.sum(converge_succ)) == 0:
        converge_succ_rate = 0
        logger.info(f'Output converge failure rate: {converge_succ_rate}')
    else:
        converge_succ_rate = (int(torch.sum(converge_succ))/(check.size()[0]))
        logger.info(f'Output converge failure rate: {converge_succ_rate}')

    logger.info(f'Complete.')

    return total_time, average_time_sample, average_iter, average_time_sample_iter, \
        data_qubit_acc, data_frame_error_rate, synd_frame_error_rate, \
            correction_acc, logical_error_rate, invoke_rate, converge_fail_rate, converge_succ_rate


def save_metric(out_dict, curr_dir, batch_size, target_error, dtype, physical_error_rate, num_batches, error_reach, file_name):
    """
    Saves decoding metrics for all decoders into a single YAML file.
    
    Parameters:
        out_dict (list of dicts): each item is a dict with metric keys
        curr_dir (str): directory path to save YAML
        physical_error_rate (float or str): label for file naming
    """

    logger.info('Saving all decoding metrics to a YAML file.')

    def float_representer(dumper, value):
        return dumper.represent_scalar('tag:yaml.org,2002:float', f"{value:.17e}")

    def format_time(value):
        return f'{float(value):.17e}'

    all_metrics_results = {}

    total_time_sum = 0.0
    last_logical_error_rate = 0.0

    for i, decoder_metrics in enumerate(out_dict):
        decoder_key = f'decoder_{i}'

        total_time_sum += float(decoder_metrics['total_time'])
        last_logical_error_rate = float(decoder_metrics['logical_error_rate'])
        all_metrics_results[decoder_key] = {
            'algorithm': decoder_metrics['algorithm'],
            'data qubit accuracy': float(decoder_metrics['data_qubit_acc']),
            'data qubit correction accuracy': float(decoder_metrics['correction_acc']),
            'data frame error rate': float(decoder_metrics['data_frame_error_rate']),
            'syndrome frame error rate': float(decoder_metrics['synd_frame_error_rate']),
            'logical error rate': float(decoder_metrics['logical_error_rate']),
            'converge failure rate': float(decoder_metrics['converge_fail_rate']),
            'converge success rate': float(decoder_metrics['converge_succ_rate']),
            'decoder invoke rate': float(decoder_metrics['invoke_rate']),
            'average iteration': float(decoder_metrics['average_iter']),
            'total time (s)': format_time(decoder_metrics['total_time']),
            'average time per batch (s)': format_time(decoder_metrics['total_time']/num_batches),
            'average time per sample (s)': format_time(decoder_metrics['average_time_sample']),
            'average time per iteration (s)': format_time(decoder_metrics['average_time_sample_iter'])
        }

    all_metrics_results['decoder_full'] = {
        'H matrix': file_name,
        'batch size': batch_size,
        'batch count': num_batches,
        'target error': target_error,
        'target error reached': error_reach,
        'data type': dtype,
        'physical error rate': physical_error_rate,
        'logical error rate': last_logical_error_rate,
        'total time (s)': format_time(total_time_sum)
    }

    os.makedirs(curr_dir, exist_ok=True)  # Ensure directory exists
    output_path = os.path.join(curr_dir, f'result_phy_err_{physical_error_rate}.yaml')

    yaml.add_representer(float, float_representer)
    with open(output_path, 'w') as f:
        yaml.safe_dump(all_metrics_results, f, sort_keys=False)

    logger.info(f'Saved all decoder metrics to: {output_path}')


def compute_avg_metrics(target_error, i, num_batches,
                        total_time_all,
                        average_time_sample_all,
                        average_iter_all,
                        average_time_sample_iter_all,
                        data_qubit_acc,
                        data_frame_error_rate_all,
                        synd_frame_error_rate_all,
                        correction_acc_all,
                        logical_error_rate_all,
                        invoke_rate_all,
                        converge_fail_all,
                        converge_succ_all):
    logger.info(f'Reporting decoding metric for decoder {i}.')
    total_time = total_time_all[i]
    average_time_batch = total_time / num_batches
    average_time_sample = average_time_sample_all[i] / num_batches
    average_iter = average_iter_all[i] / num_batches
    average_time_sample_iter = average_time_sample_iter_all[i] / num_batches
    data_qubit_acc = data_qubit_acc[i] / num_batches
    data_frame_error_rate = data_frame_error_rate_all[i] / num_batches
    synd_frame_error_rate = synd_frame_error_rate_all[i] / num_batches
    correction_acc = correction_acc_all[i] / num_batches
    logical_error_rate = logical_error_rate_all[i] / num_batches
    invoke_rate = invoke_rate_all[i] / num_batches
    converge_fail = converge_fail_all[i] / num_batches
    converge_succ = converge_succ_all[i] / num_batches
    logger.info(f'Total time for <{target_error}> errors: {total_time} seconds.')
    logger.info(f'Total number of batches: {num_batches}.')
    logger.info(f'Average time per batch: {average_time_batch} seconds.')
    logger.info(f'Average time per sample: {average_time_sample} seconds.')
    logger.info(f'Average iterations per sample: {average_iter}')
    logger.info(f'Average time per iteration: {average_time_sample_iter}')
    logger.info(f'Data qubit accuracy: {data_qubit_acc}')
    logger.info(f'Data qubit correction accuracy: {correction_acc}')
    logger.info(f'Data frame error rate: {data_frame_error_rate}')
    logger.info(f'Syndrome frame error rate: {synd_frame_error_rate}')
    logger.info(f'Output logical error rate: {logical_error_rate}')
    logger.info(f'Decoder invoke rate: {invoke_rate}')
    logger.info(f'converge failure rate: {converge_fail}')
    logger.info(f'Converge success rate: {converge_succ}')

    logger.info(f'Complete.')

    return total_time, average_time_sample, average_iter, average_time_sample_iter, data_qubit_acc, \
        data_frame_error_rate, synd_frame_error_rate, correction_acc, logical_error_rate, \
            invoke_rate, converge_fail, converge_succ


def load_checkpoint_yaml(path):
     with open(path, 'r') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        
        full = data['decoder_full']
        ckpt_H = full.get('H matrix', 0)
        batch_size = int(full.get('batch size', 0))
        batch_count = int(full.get('batch count', 0))
        target_error = int(full.get('target error', 0))
        error_reach = int(full.get('target error reached', 0))
        dtype = full.get('data type', 0)
        physical_error_rate = float(full.get('physical error rate', 0.0))
    
        decoder_keys = sorted(
            [k for k in data if k.startswith('decoder_') and k[8:].isdigit()],
            key=lambda x: int(x.split('_')[1])
        )
        num_decoders = len(decoder_keys)

        # Initialize lists
        total_time_all = [0.0 for _ in range(num_decoders)]
        average_time_sample_all = [0.0 for _ in range(num_decoders)]
        average_iter_all = [0.0 for _ in range(num_decoders)]
        average_time_sample_iter_all = [0.0 for _ in range(num_decoders)]
        data_qubit_acc = [0.0 for _ in range(num_decoders)]
        data_frame_error_rate_all = [0.0 for _ in range(num_decoders)]
        synd_frame_error_rate_all = [0.0 for _ in range(num_decoders)]
        correction_acc_all = [0.0 for _ in range(num_decoders)]
        logical_error_rate_all = [0.0 for _ in range(num_decoders)]
        invoke_rate_all = [0.0 for _ in range(num_decoders)]
        converge_fail_all = [0.0 for _ in range(num_decoders)]
        converge_succ_all = [0.0 for _ in range(num_decoders)]

        # Populate from YAML
        for idx, key in enumerate(decoder_keys):
            entry = data[key]
            total_time_all[idx] = float(entry['total time (s)'])*batch_count
            average_time_sample_all[idx] = float(entry['average time per sample (s)'])*batch_count
            average_iter_all[idx] = float(entry['average iteration'])*batch_count
            average_time_sample_iter_all[idx] = float(entry['average time per iteration (s)'])*batch_count
            data_qubit_acc[idx] = float(entry['data qubit accuracy'])*batch_count
            data_frame_error_rate_all[idx] = float(entry['data frame error rate'])*batch_count
            synd_frame_error_rate_all[idx] = float(entry['syndrome frame error rate'])*batch_count
            correction_acc_all[idx] = float(entry['data qubit correction accuracy'])*batch_count
            logical_error_rate_all[idx] = float(entry['logical error rate'])*batch_count
            invoke_rate_all[idx] = float(entry['decoder invoke rate'])*batch_count
            converge_fail_all[idx] = float(entry['converge failure rate'])*batch_count
            converge_succ_all[idx] = float(entry['converge failure rate'])*batch_count

        return (total_time_all,
                average_time_sample_all,
                average_iter_all,
                average_time_sample_iter_all,
                data_qubit_acc,
                data_frame_error_rate_all,
                synd_frame_error_rate_all,
                correction_acc_all,
                logical_error_rate_all,
                invoke_rate_all,
                converge_fail_all,
                converge_succ_all, error_reach, batch_size, target_error, dtype, physical_error_rate, batch_count, ckpt_H)
     
