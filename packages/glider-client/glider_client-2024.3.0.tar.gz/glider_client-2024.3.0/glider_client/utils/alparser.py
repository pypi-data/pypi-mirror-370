# -*- coding: utf-8 -*-
"""
Created on September 01, 2015

Copyright Alpes Lasers SA, Neuchatel, Switzerland, 2015

@author: chiesa
"""

import argparse
import logging

logger = logging.getLogger(__name__)

_version = 'undefined'

try:
    from glider_client import pkg, version

    _version = '{} {}'.format(pkg, version)
except Exception as e:
    logger.debug(e, exc_info=1)


def _positive_float(value):
    v = float(value)
    if v < 0.0:
        raise ValueError('{} must be a positive value'.format(v))
    return v

def _positive_int(value):
    v = int(value)
    if v < 0.0:
        raise ValueError('{} must be a positive value'.format(v))
    return v

def _strict_positive_int(value):
    v = int(value)
    if v <= 0.0:
        raise ValueError('{} must be a strict positive value'.format(v))
    return v


baseparser = argparse.ArgumentParser()
baseparser.add_argument("--show-version", help="Show the project version",
                        action="version", version="%s %s" % (pkg, version))




