
# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

import logging

from pkg_resources import DistributionNotFound
from distutils.version import StrictVersion
from importlib.metadata import version as pkg_version

pkg = "glider_client"
try:
    version = pkg_version(pkg)
    try:
        StrictVersion(version)
    except ValueError as e:
        version = 'devel'
except Exception as e:
    logging.exception(e)
    version = "devel"