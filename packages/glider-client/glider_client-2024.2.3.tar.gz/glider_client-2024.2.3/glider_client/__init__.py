# -*- coding: utf-8 -*-
"""
Initialize the logger

Created on October 29, 2024

Copyright Alpes Lasers SA, Neuchatel, Switzerland, 2024

@author: chiesa
"""
import logging
from pkg_resources import DistributionNotFound
import pkg_resources
from distutils.version import StrictVersion

pkg = "glider_client"
try:
    version = pkg_resources.get_distribution(pkg).version
    try:
        StrictVersion(version)
    except ValueError as e:
        version = 'devel'
except DistributionNotFound:
    version = "devel"

try:
    from logserviceclient.utils.logger import initLogger
    try:
        initLogger(pkg)
    except Exception:
        logging.warning("Log service client was not initialized properly")
except ImportError:
    pass
