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
from time import sleep
from copy import deepcopy

import requests

from glider_client.scripts.stepping_poi_plot import stepping_poi_plot
from glider_client.utils.alparser import _positive_float, _positive_int, _strict_positive_int
from glider_client.utils.mcu_registers import ADC_SAMPLING_TIMES
from glider_client.utils.ping import ping
from glider_client.utils.ssrv import store_stepping_poi
from glider_client.utils.glider import get_glider_configuration


def _analog_channel_number(value):
    value = int(value)
    if value not in [1, 2]:
        raise ValueError('Analog channel number must be 1 or 2')
    return value



def run():
    parser = ArgumentParser()
    parser.add_argument('-wn', nargs='+', type=_positive_float,
                        help='wavenumbers [cm-1]')
    parser.add_argument('-ld', nargs='+', type=_positive_int,
                        help='laser dwell time [ms]')
    parser.add_argument('-pd', nargs='+', type=_positive_int,
                        help='post dwell time [ms]')
    parser.add_argument('-c', type=str,
                        help='file path in CSV format, each line containing '
                             'wavenumber, laserDwellMs, postDwellMs')
    parser.add_argument('-wn_tol', type=_positive_float, required=True,
                        help='wavenumber tolerance window [cm-1]')
    parser.add_argument('-stab_poi', type=_positive_int, required=True,
                        help='stable time in POI [ms]')
    parser.add_argument('-pn', nargs='+', type=_strict_positive_int,
                        help='number of acquisition pulses')
    parser.add_argument('-ch', type=int, choices=[1, 2],
                        help='analog channel number, if not specified, both channels are used')
    args, remaining_args = parser.parse_known_args()

    analog_channels = [1, 2]

    if args.ch is not None:
        if args.ch == 1:
            analog_channels = [1]
        if args.ch == 2:
            analog_channels = [2]
    for c in [1, 2]:
        required = (c in analog_channels)
        parser.add_argument('-anal{}_dl'.format(c), type=_positive_int, required=required,
                            help='analog{} acquisition delay after pulse trigger [ns]'.format(c))
        parser.add_argument('-anal{}_os'.format(c), type=int, default=3,
                            help='analog{} oversampling'.format(c))
        parser.add_argument('-anal{}_sh'.format(c), type=int, default=2,
                            help='analog{} oversampling shift'.format(c))
        parser.add_argument('-anal{}_sp'.format(c), type=_positive_int, default=9,
                            help='analog{} sampling time'.format(c), choices=ADC_SAMPLING_TIMES)
    parser.add_argument('-g', type=str, default='localhost', help='host name of glider' )


    args = parser.parse_args()

    if args.c is None:
        if (args.wn is None) or (args.ld is None) or (args.pd is None) or (args.pn is None):
            parser.error('if you do not specify the -c option (CSV file path), '
                         'you will need to specify the POIs by the -wn, -ld, -pd and -pulse_num '
                         'options.')
        num_wavenumbers = len(args.wn)
        num_ld = len(args.ld)
        num_pd = len(args.pd)
        num_pulse_num = len(args.pn)
        wn_list = args.wn
        ld_list = []
        pd_list = []
        pulse_num_list = []
        if num_ld == 1:
            ld_list = num_wavenumbers*args.ld
        elif num_ld == num_wavenumbers:
            ld_list = args.ld
        else:
            parser.error('the length of -ld list must be either 1 or equal to the '
                         'length of the -wn list')
        if num_pd == 1:
            pd_list = num_wavenumbers*args.pd
        elif num_pd == num_wavenumbers:
            pd_list = args.pd
        else:
            parser.error('the length of -ld list must be either 1 or equal to the '
                         'length of the -wn list')
        if num_pulse_num == 1:
            pulse_num_list = num_wavenumbers*args.pn
        elif num_pulse_num == num_wavenumbers:
            pulse_num_list = args.pn
        else:
            parser.error('the length of -pn list must be either 1 or equal to the '
                         'length of the -wn list')
        poi_list = [{'wavenumber': a,
                     'laserDwellMs': b,
                     'postDwellMs': c,
                     'numberOfPulses': d} for a, b, c, d in itertools.zip_longest(wn_list,
                                                                                ld_list,
                                                                                pd_list,
                                                                                pulse_num_list)]
    else:
        if not os.path.exists(args.c):
            parser.error('csv file {} does not exists'.format(args.c))
        with open(args.c, 'r') as f:
            poi_list = [[float(x) for x in l.split(',')] for l in f.readlines()]
        poi_list = [{'wavenumber': x[0],
                     'laserDwellMs': x[1],
                     'postDwellMs': x[2],
                     'numberOfPulses': x[3]
                     } for x in poi_list]

    stepping_poi(glider_host=args.g, anal1_sp=args.anal1_sp, anal1_os=args.anal1_os, anal1_sh=args.anal1_sh,
                 anal2_sp=args.anal2_sp, anal2_os=args.anal2_os, anal2_sh=args.anal2_sh,
                 wn_tol=args.wn_tol, stab_poi=args.stab_poi,
                 channel=args.ch, anal1_dl=args.anal1_dl, anal2_dl=args.anal2_dl, poi_list=poi_list)


def stepping_poi(glider_host, anal1_sp, anal1_os, anal1_sh,
                 anal2_sp, anal2_os, anal2_sh, wn_tol, stab_poi,
                 channel, anal1_dl, anal2_dl, poi_list, store_ssrv=True,
                 plot=True):

    use_analog1 = True
    use_analog2 = True

    if channel is not None:
        if channel == 1:
            use_analog2 = False
        if channel == 2:
            use_analog1 = False

    results_dir = os.path.expanduser('~/glider/testing/stepping_poi/{}'.format(glider_host))

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    results_file = os.path.join(results_dir, '{}_stepping_poi_'
                                             'st1_{}_os1_{}_sh1_{}'
                                             'st2_{}_os2_{}_sh2_{}.csv'.format(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'),
                                                                               anal1_sp, anal1_os, anal1_sh,
                                                                               anal2_sp, anal2_os, anal2_sh))

    glider_url = 'http://{}:5000/api'.format(glider_host)



    parameters = {'poi_list': poi_list,
                  'tuned_window_invcm': wn_tol,
                  'stable_time_in_poi_ms': stab_poi,
                  'use_analog1': use_analog1,
                  'use_analog2': use_analog2,
                  'analog1_delay_s2m_trigger_ns': anal1_dl,
                  'analog1_oversampling': anal1_os,
                  'analog1_oversampling_shift': anal1_sh,
                  'analog1_sampling_time_ns': anal1_sp,
                  'analog2_delay_s2m_trigger_ns': anal2_dl,
                  'analog2_oversampling': anal2_os,
                  'analog2_oversampling_shift': anal2_sh,
                  'analog2_sampling_time_ns': anal2_sp,
                  }
    print(poi_list)
    print(parameters)
    rsp = requests.post('{}/command'.format(glider_url),
                        params={'command': 'stepping_poi'},
                        json={'parameters': parameters})
    rsp.raise_for_status()
    msg = rsp.json()
    if msg['level'] == 'error':
        raise Exception(msg['message'])
    print('Running POI...')
    data_list = []
    while True:
        rsp = requests.get('{}/command'.format(glider_url))
        status = rsp.json()
        if len(data_list) != len(status['data_list']):
            for l in status['data_list'][len(data_list):]:
                print(', '.join([str(l[k]) for k in ['wavenumber',
                                                     'analog1AdcSum',
                                                     'analog2AdcSum',
                                                     'acquiredPulsesNumber',
                                                     'cavity',
                                                     'errors',
                                                     'status']]))
            data_list = status['data_list']
        if not status['running']:
            break
        sleep(1)
    if status['status']['level'] == 'error':
        raise Exception('{}({})'.format(status['status']['exception'],
                                        status['status']['messages']))

    # if False:
    if store_ssrv and ping('ssrv'):
        glider_config = get_glider_configuration(glider_host)
        dataset = deepcopy(parameters)
        dataset['wavenumber'] = [x['wavenumber'] for x in status['data_list']]
        dataset['analog1adcsum_list'] = [x['analog1AdcSum'] for x in status['data_list']]
        dataset['analog2adcsum_list'] = [x['analog2AdcSum'] for x in status['data_list']]
        dataset['status_number'] = [x['status'] for x in status['data_list']]
        dataset['cavity'] = [x['cavity'] for x in status['data_list']]
        #dataset['errors'] = [x['errors'] for x in status['data_list']]
        dataset['acquiredpulsesnumber_list'] = [x['acquiredPulsesNumber'] for x in status['data_list']]
        store_stepping_poi(glider_config, dataset)
    else:
        with open(results_file, 'w') as f:
            for l in status['data_list']:
                f.write('{}\n'.format(', '.join(str(l[k]) for k in ['wavenumber',
                                                                    'analog1AdcSum',
                                                                    'analog2AdcSum',
                                                                    'acquiredPulsesNumber',
                                                                    'cavity',
                                                                    'errors',
                                                                    'status',
                                                                    ])))
        if plot:
            stepping_poi_plot([results_file])


if __name__ == '__main__':
    run()




