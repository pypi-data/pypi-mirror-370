# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

import logging

from dataclasses import asdict

from time import sleep, time


from glider_client.commands import SteppingPoiDataset, STEPPING_POI_S2_TRIGGER_MODE_INT_CONTINUOUS
from glider_client.glider import Glider, GliderTimeout

REPETITIONS = 10

def run():
    glider_client = Glider(hostname='localhost',
                           port=6661)
    glider_status = glider_client.get_status()
    glider_client.initialize()

    wavenumbers = []

    for cp in glider_status.config.profiles[1].cavityProfiles.values():
        wavenumbers.append(min(cp.calibWnInvCm) + 1)
        wavenumbers.append(max(cp.calibWnInvCm) - 1)


    poi_list = [{'wavenumber': x,
                 'laserDwellMs': 0,
                 'postDwellMs': 0,
                 'numberOfPulses': 10,
                 'analog1PGA': 4,
                 'analog2PGA': 4,
                 } for x in sorted(wavenumbers)]

    use_analog1 = True
    use_analog2 = True

    parameters = {'poi': poi_list,
                  'tuned_window_invcm': 1,
                  'stable_time_in_poi_ms': 1,
                  'use_analog1': use_analog1,
                  'use_analog2': use_analog2,
                  'analog1_delay_s2m_trigger_ns': 200,
                  'analog1_oversampling': 3,
                  'analog1_oversampling_shift': 2,
                  'analog1_sampling_time_ns': 9,
                  'analog2_delay_s2m_trigger_ns': 200,
                  'analog2_oversampling': 3,
                  'analog2_oversampling_shift': 2,
                  'analog2_sampling_time_ns': 9,
                  's2_trigger_mode': STEPPING_POI_S2_TRIGGER_MODE_INT_CONTINUOUS,
                  'repetitions': REPETITIONS,
                  }
    command_proxy = None

    timeout = 3 * 60
    try:
        command_proxy = glider_client.execute_command_async(command_dataset=SteppingPoiDataset(**parameters))
        start_time = time()
        while True:
            if time() - start_time > timeout:
                raise GliderTimeout
            command_proxy.update()
            if command_proxy.hasExecuted:
                break
            sleep(0.1)
        command_proxy.update()
        if command_proxy.hasErrors:
            print('Error executing the scan')
    finally:
        # if this script is interrupted, stop the current execution
        if command_proxy:
            command_proxy.stop()


    status = glider_client.get_status()
    print(glider_client.get_results(command_proxy.status, result_indexes=list(range(REPETITIONS))))
    print(asdict(status))



if __name__ == '__main__':
    run()
