# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

import logging

from glider_client import scan_adc_delay
from glider_client.scripts.stepping_poi import stepping_poi

poi_list = [{'wavenumber': 840 + i/10,
             'laserDwellMs': i%10,
             'postDwellMs': i%10,
             'numberOfPulses': i*10 + 1} for i in range(600)]

channel=1
wn=1000
wn_tol=1
stab_poi=100
scan=1
step=4
over_samp=1
samp_shift=0
glider_host='glidix'
anal1_dl=400
anal2_dl=400
anal1_os=1
anal1_sh=0
anal1_sp=9
anal2_os=1
anal2_sh=0
anal2_sp=9


if __name__ == '__main__':
    while True:
        try:
            stepping_poi(glider_host=glider_host, anal1_sp=anal1_sp, anal1_os=anal1_os, anal1_sh=anal1_sh,
                         anal2_sp=anal2_sp, anal2_os=anal2_os, anal2_sh=anal2_sh,
                         wn_tol=wn_tol, stab_poi=stab_poi,
                         channel=channel, anal1_dl=anal1_dl, anal2_dl=anal2_dl, poi_list=poi_list,
                         store_ssrv=False, plot=False)
        except Exception as e:
            logging.exception(e)
        try:
            scan_adc_delay(glider_host=glider_host, scan=scan, step=step, wn=wn,
                           samp_time=9, over_samp=over_samp,
                           samp_shift=samp_shift, ch=channel, wn_tol=wn_tol,
                           stab_poi=stab_poi, store_ssrv=False, plot=False)
        except Exception as e:
            logging.exception(e)

