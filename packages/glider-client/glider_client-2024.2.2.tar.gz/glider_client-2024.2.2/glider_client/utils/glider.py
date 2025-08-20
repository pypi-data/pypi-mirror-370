# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

import requests


def get_glider_status(hostname):
    rsp = requests.get('http://{}/api/status'.format(hostname))
    rsp.raise_for_status()
    return rsp.json()


def get_glider_configuration(hostname):
    status = get_glider_status(hostname)
    return status['config']
