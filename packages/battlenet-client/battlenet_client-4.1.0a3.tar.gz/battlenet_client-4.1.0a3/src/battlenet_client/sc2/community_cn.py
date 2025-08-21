"""Defines the functions that handle the community APIs for Starcraft 2
for the chinese regions

Functions:
    profile(region_tag, profile_id, realm_id, profile_name, locale)
    ladder(region_tag, profile_id, realm_id, profile_name, locale)
    match_history( region_tag, profile_id, realm_id, profile_name, locale)
    ladder( region_tag, ladder_id, locale)
    achievements(region_tag, locale)
    rewards(region_tag, locale)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from typing import Optional

from .. import utils
from ..exceptions import BNetRegionError
from ..decorators import verify_region
from .decorators import sc2_cn_only


__version__ = '2.0.0'
__author__ = 'David \'Gahd\' Couples'


@sc2_cn_only
@verify_region
def profile(
    region_tag: str,
    profile_id: int,
    region_id: int,
    profile_name: str,
    locale: Optional[str] = None
):
    """Returns data about an individual SC2 profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        profile_id (int): the profile ID
        profile_name (str): name to use with the CN endpoint

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is not 'cn'
    """
    if region_tag != 'cn':
        raise BNetRegionError("CN Region required")

    uri = f"{utils.api_host(region_tag)}/sc2/profile/{profile_id}/{region_id}/{profile_name}"

    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_cn_only
@verify_region
def ladders(
    region_tag: str,
    profile_id: int,
    region_id: int,
    profile_name: str,
    locale: Optional[str] = None
):
    """Returns a ladder summary, or specific ladder for an individual SC2 profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        profile_id (int): the profile ID
        profile_name (str): Name of the profile

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is not 'cn'
    """
    if region_tag != 'cn':
        raise BNetRegionError("CN Required")

    uri = f"{utils.api_host(region_tag)}/sc2/profile/{profile_id}/{region_id}/{profile_name}/ladders"

    params = {"locale": utils.localize(locale)}

    return uri, params


@sc2_cn_only
@verify_region
def match_history(
        region_tag: str,
        profile_id: int,
        region_id: int,
        profile_name: str,
        locale: Optional[str] = None
):
    """Returns data about an individual SC2 profile's match history.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        profile_id (int): the profile ID
        profile_name(str): profile name for the CN region request

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region is not 'cn'
    """
    uri = f"{utils.api_host(region_tag)}/sc2/profile/{profile_id}/{region_id}/{profile_name}/matches"

    params = {"locale": utils.localize(locale)}

    return uri, params


@sc2_cn_only
@verify_region
def ladder(
    region_tag: str,
    ladder_id: int,
    locale: Optional[str] = None,
):
    """Returns a ladder summary, or specific ladder for an individual SC2 profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        ladder_id (int): region for the profile, or use sc2.constants

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is not 'cn'
    """
    if region_tag != 'cn':
        raise BNetRegionError("CN Required")

    uri = f"{utils.api_host(region_tag)}/sc2/ladder/{ladder_id}"

    params = {"locale": utils.localize(locale)}

    return uri, params


@sc2_cn_only
@verify_region
def achievements(
    region_tag: str,
    locale: Optional[str] = None,
):
    """Returns a ladder summary, or specific ladder for an individual SC2 profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is not 'cn'
    """
    if region_tag != 'cn':
        raise BNetRegionError("CN Required")

    uri = f"{utils.api_host(region_tag)}/sc2/data/achievements"

    params = {"locale": utils.localize(locale)}

    return uri, params


@sc2_cn_only
@verify_region
def rewards(
    region_tag: str,
    locale: Optional[str] = None,
):
    """Returns a ladder summary, or specific ladder for an individual SC2 profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is not 'cn'
    """
    if region_tag != 'cn':
        raise BNetRegionError("CN Required")

    uri = f"{utils.api_host(region_tag)}/sc2/data/rewards"

    params = {"locale": utils.localize(locale)}

    return uri, params
