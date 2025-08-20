#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on October 29, 2024

Copyright Alpes Lasers SA, Neuchatel, Switzerland, 2024

@author: chiesa
"""

from setuptools import setup

setup(
    setup_requires=['pbr'],
    pbr=True,
    test_suite = "glider_client.tests"
)