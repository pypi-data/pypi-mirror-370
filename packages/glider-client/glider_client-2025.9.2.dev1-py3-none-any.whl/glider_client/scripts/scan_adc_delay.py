# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

import itertools
import os
from argparse import ArgumentParser
from datetime import datetime

from glider_client.commands import OptimizeAdcDataset
from glider_client.glider import Glider
from glider_client.scripts.scan_adc_delay_plot import scan_adc_delay_plot
from glider_client.utils.alparser import _positive_int, _positive_float
from glider_client.utils.mcu_registers import ADC_SAMPLING_TIMES
from glider_client.utils.ping import ping
from glider_client.utils.ssrv import store_adc_delay


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
                        help='adc sampling time [ns]', choices=ADC_SAMPLING_TIMES)
    parser.add_argument('-over_samp', type=int, default=3,
                        help='adc oversampling')
    parser.add_argument('-samp_shift', type=int, default=2,
                        help='adc sampling shift')
    parser.add_argument('-stab_poi', type=_positive_int, required=True,
                        help='stable time in POI [ms]')
    parser.add_argument('-g', type=str, default='localhost', help='host name of glider')
    if ping('ssrv'):
        parser.add_argument('--store_local', action='store_true', default=False,
                            help='force local storage of measurements')

    args = parser.parse_args()

    if ping('ssrv'):
        store_local = args.store_local
    else:
        store_local = True

    scan_adc_delay(glider_host=args.g, scan=args.scan, step=args.step, wn=args.wn,
                   samp_time=args.samp_time, over_samp=args.over_samp,
                   samp_shift=args.samp_shift, ch=args.ch, wn_tol=args.wn_tol,
                   stab_poi=args.stab_poi, store_ssrv=(not store_local))


def scan_adc_delay(glider_host, scan, step, wn,
                   samp_time, over_samp, samp_shift, ch, wn_tol,
                   stab_poi, store_ssrv=True, plot=True):
    glider_client = Glider(hostname=glider_host,
                           port=5000)
    glider_client.initialize()

    results_dir = os.path.expanduser('~/glider/testing/optimal_adc_delay/{}'.format(glider_host))

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    results_file = os.path.join(results_dir,
                                '{}_optimal_delay_'
                                'scan_{}_step_{}_wn_{}_st_{}_os_{}_sh_{}.csv'.format(
                                    datetime.now().strftime('%Y_%m_%d_%H_%M_%S'),
                                    scan,
                                    step,
                                    wn,
                                    samp_time,
                                    over_samp,
                                    samp_shift))

    command_proxy = glider_client.execute_command(OptimizeAdcDataset(wavenumber=wn,
                                                                     tuned_window_invcm=wn_tol,
                                                                     analog_channel=ch,
                                                                     stable_time_in_poi_ms=stab_poi,
                                                                     adc_scan_size_us=scan,
                                                                     adc_step_size_ns=step,
                                                                     adc_oversampling=over_samp,
                                                                     adc_oversampling_shift=samp_shift,
                                                                     adc_sampling_time_ns=samp_time))

    if store_ssrv:
        glider_config = glider_client.get_status().config
        dataset = {'wavenumber': wn, 'analog_channel': ch, 'tuned_window_invcm': wn_tol,
                   'stable_time_in_poi_ms': stab_poi, 'adc_scan_size_us': scan, 'adc_step_size_ns': step,
                   'adc_oversampling': over_samp, 'adc_oversampling_shift': samp_shift,
                   'adc_sampling_time_ns': samp_time, 'adcsum_list': command_proxy.result.adcSum,
                   'delayns_list': command_proxy.result.delayNs, 'position': command_proxy.result.position,
                   'status_number': command_proxy.result.status, 'cavity': command_proxy.result.cavity[-1]}
        # dataset['error'] = status['data_list'][-1]['cavity']
        store_adc_delay(glider_config, dataset)
    else:
        r = command_proxy.result
        with open(results_file, 'w') as f:
            for line in itertools.zip_longest(*[getattr(r, x)
                                                for x in
                                                ['adcSum', 'cavity', 'delayNs',
                                                 'position', 'status']]):
                f.write(
                    '{}\n'.format(', '.join(str(x) for x in line)))
        if plot:
            scan_adc_delay_plot([results_file])


if __name__ == '__main__':
    run()
