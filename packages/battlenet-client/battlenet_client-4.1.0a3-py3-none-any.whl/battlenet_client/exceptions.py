"""Defines exceptions related to the Battle.net API wrappers

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""


__version__ = '1.0.0'
__author__ = 'David \'Gahd\' Couples'


class BNetError(Exception):
    """Battle.net Base Exception class
    """
    pass


class BNetRegionError(BNetError):
    """Exception raised when there is a problem with the region, when the region does exist
    """
    pass


class BNetValueError(BNetError):
    """Exception for when bad data is present"""
    pass


class BNetReleaseError(BNetError):
    """Exception raised when there is a problem with the region
    """
    pass
