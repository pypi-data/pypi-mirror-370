# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"


import importlib
import pkgutil
import pytest

def walk_packages(package_name):
    """Yield all modules in the given package."""
    package = importlib.import_module(package_name)
    path = package.__path__  # noqa: SLF001
    for module_info in pkgutil.walk_packages(path, package.__name__ + "."):
        yield module_info.name

@pytest.mark.parametrize("module_name", list(walk_packages("glider_client")))
def test_import_module(module_name):
    """Test that each module in glider_client can be imported."""
    importlib.import_module(module_name)