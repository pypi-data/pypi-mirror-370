"""Miscellaneous functions to support for World of Warcraft

Functions:
    namespace(api_type, release, region)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from ..decorators import verify_region
from ..exceptions import BNetValueError
from .constants import Release

from typing import Optional

__version__ = '1.0.0'
__author__ = 'David \'Gahd\' Couples'


@verify_region
def namespace(region: str, api_type: str, release: Optional[str] = 'retail') -> str:
    """Returns the namespace required by the WoW API endpoint

    Returns:
        str: the namespace string

    Raises:
        BNetValueError: when api type is not of static, dynamic or profile, or an invalid release
    """

    if api_type.lower() not in ('static', 'dynamic', 'profile'):
        raise BNetValueError('Invalid API type: needs to be static, dynamic, or profile')

    if not release:
        release = 'retail'

    if release.lower() not in Release.all():
        raise BNetValueError(f"Invalid Release: needs to be one of: {','.join(Release.all())}")

    if release.lower() != "retail":
        return f"{api_type}-{release.lower()}-{region.lower()}"

    return f"{api_type}-{region.lower()}"
