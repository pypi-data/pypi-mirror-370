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


from glider_client.commands import SteppingPoiDataset, STEPPING_POI_S2_TRIGGER_MODE_INT_CONTINUOUS, SetWavenumberDataset
from glider_client.glider import Glider, GliderTimeout



def run():
    glider_client = Glider(hostname='localhost',
                           port=6661)
    glider_status = glider_client.get_status()
    glider_client.initialize()
    print(glider_status)

    glider_client.execute_command(SetWavenumberDataset(wavenumber=1000))

    print(glider_client.get_status())
    sleep(10)
    glider_client.switch_lasing_off()
    print(glider_client.get_status())

if __name__ == '__main__':
    run()