# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

import os
from argparse import ArgumentParser
from datetime import datetime
from time import sleep
from copy import deepcopy

import requests

from glider_client.scripts.scan_adc_delay_plot import scan_adc_delay_plot
from glider_client.utils.alparser import _positive_float, _positive_int
from glider_client.utils.mcu_registers import ADC_SAMPLING_TIMES
from glider_client.utils.ping import ping
from glider_client.utils.ssrv import store_adc_delay
from glider_client.utils.glider import get_glider_configuration


def run():
    parser = ArgumentParser()
    parser.add_argument('-wn', type=float, required=True, help='angle')
    parser.add_argument('-ch', type=int, required=False, choices=[1, 2],
                        default=2,
                        help='analog channel to be optimized')
    parser.add_argument('-scan', type=_positive_int, default=1,
                        help='scan size micro seconds')
    parser.add_argument('-step', type=_positive_int, default=4,
                        help='scan step in nano seconds (must be a multiple of 4)')
    parser.add_argument('-wn_tol', type=_positive_float, required=True,
                        help='wavenumber tolerance window [cm-1]')
    parser.add_argument('-samp_time', type=_positive_int, default=9,
                        help='adc sampling time', choices=ADC_SAMPLING_TIMES)
    parser.add_argument('-over_samp', type=int, default=3,
                        help='oversampling')
    parser.add_argument('-samp_shift', type=int, default=2,
                        help='oversampling')
    parser.add_argument('-stab_poi', type=_positive_int, required=True,
                        help='stable time in POI [ms]')
    parser.add_argument('-g', type=str, default='localhost', help='host name of glider' )

    args = parser.parse_args()
    glider_host = args.g
    glider_url = 'http://{}:5000/api'.format(glider_host)

    results_dir = os.path.expanduser('~/glider/testing/optimal_adc_delay/{}'.format(args.g))

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    results_file = os.path.join(results_dir,
                                '{}_optimal_delay_'
                                'scan_{}_step_{}_wn_{}_st_{}_os_{}_sh_{}.csv'.format(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'),
                                                                                     args.scan,
                                                                                     args.step,
                                                                                     args.wn,
                                                                                     args.samp_time,
                                                                                     args.over_samp,
                                                                                     args.samp_shift))
    parameters =  {'wavenumber': args.wn,
                   'analog_channel': args.ch,
                   'tuned_window_invcm': args.wn_tol,
                   'stable_time_in_poi_ms': args.stab_poi,
                   'adc_scan_size_us': args.scan,
                   'adc_step_size_ns': args.step,
                   'adc_oversampling': args.over_samp,
                   'adc_oversampling_shift': args.samp_shift,
                   'adc_sampling_time_ns': args.samp_time,
                   }
    rsp = requests.post('{}/command'.format(glider_url),
                        params={'command': 'optimize_adc'},
                        json={'parameters': parameters})
    rsp.raise_for_status()
    msg = rsp.json()
    if msg['level'] == 'error':
        raise Exception(msg['message'])
    print('Running ADC delay scan...')
    data_list = []
    while True:
        rsp = requests.get('{}/command'.format(glider_url))
        status = rsp.json()
        if len(data_list) != len(status['data_list']):
            for x in status['data_list'][len(data_list):]:
                print(x)
            data_list = status['data_list']
        if not status['running']:
            break
        sleep(1)
    if status['status']['level'] == 'error':
        raise Exception('{}({})'.format(status['status']['exception'],
                                        status['status']['messages']))
    # if False:
    if ping('ssrv'):
        glider_config = get_glider_configuration(glider_host)
        dataset = deepcopy(parameters)
        dataset['adcsum_list'] = [x['adcSum'] for x in status['data_list']]
        dataset['delayns_list'] = [x['delayNs'] for x in status['data_list']]
        dataset['position'] = [x['position'] for x in status['data_list']]
        dataset['status_number'] = [x['status'] for x in status['data_list']]
        dataset['cavity'] = status['data_list'][-1]['cavity']
       # dataset['error'] = status['data_list'][-1]['cavity']
        store_adc_delay(glider_config , dataset)
    else:
        with open(results_file, 'w') as f:
            for l in status['data_list']:
                f.write('{}\n'.format(', '.join(str(l[k]) for k in ['adcSum', 'cavity', 'delayNs', 'position', 'status'])))

            scan_adc_delay_plot([results_file])


if __name__ == '__main__':
    run()
