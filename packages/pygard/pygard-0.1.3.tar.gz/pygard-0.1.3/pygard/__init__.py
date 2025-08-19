# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 11:07
# @Description: 

"""
PyGard - A modern async Python client for Gard data service.

This package provides a comprehensive client for interacting with the Gard data service,
featuring async support, OOP design, and excellent extensibility.
"""

from .client import GardClient
from .config import GardConfig
from .models import Gard, GardFilter, GardPage
from pygard.utils.exceptions import GardException, GardConnectionError, GardValidationError

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("pygard")
except PackageNotFoundError as e:
    raise e

__all__ = [
    "GardClient",
    "GardConfig",
    "Gard",
    "GardFilter",
    "GardPage",
    "GardException",
    "GardConnectionError",
    "GardValidationError",
]
