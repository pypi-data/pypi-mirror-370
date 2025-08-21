"""Defines the decorators used in this package

Functions:
   verify_region

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
import functools

from .constants import VALID_REGIONS
from .exceptions import BNetRegionNotFoundError


__version__ = '1.0.0'
__author__ = 'David \'Gahd\' Couples'


def verify_region(func):
    """Verifies the function's first parameter is a valid region abbreviation

    Raises:
        BNetRegionNotFoundError: when the region (arg[0]) is not a valid region tag
    """
    @functools.wraps(func)
    def wrapper_verify_region(*args, **kwargs):
        if args[0].lower() not in VALID_REGIONS:
            raise BNetRegionNotFoundError('Region not found')

        return func(*args, **kwargs)
    return wrapper_verify_region

