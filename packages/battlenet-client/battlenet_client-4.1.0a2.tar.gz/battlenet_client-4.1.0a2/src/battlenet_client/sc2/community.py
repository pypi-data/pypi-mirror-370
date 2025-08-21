"""Defines the functions that handle the community APIs for Starcraft 2
for the non-chinese regions

Functions:
    static(region_tag, region_id, locale)
    metadata(region_tag, region_id, realm_id, profile_id, locale)
    profile(region_tag, region_id, realm_id, profile_id, locale)
    ladder(region_tag, region_id, realm_id, profile_id, ladder_id, locale)
    grandmaster(region_tag, region_id, locale)
    season(region_tag, region_id, locale)
    player(region_tag, account_id, locale)
    legacy_profile(region_tag, region_id, realm_id, profile_id, locale)
    legacy_ladders(region_tag, region_id, realm_id, profile_id, locale)
    legacy_match_history( region_tag, region_id, realm_id, profile_id, locale)
    legacy_ladder( region_tag, region_id, ladder_id, locale)
    legacy_achievements( region_tag, region_id, locale)
    legacy_rewards(region_tag, region_id, locale)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""

from typing import Optional, Union

from .. import utils
from .decorators import sc2_region
from ..exceptions import BNetRegionError
from ..decorators import verify_region

__version__ = '2.0.0'
__author__ = 'David \'Gahd\' Couples'


@sc2_region
@verify_region
def static(
    region_tag: str,
    region_id: int,
    locale: Optional[str] = None,
):
    """Returns all static SC2 profile data (achievements, categories, criteria, and rewards).

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (str): region for the profile, or use sc2.constants  (used outside CN only)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """
    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region ID")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/static/profile/{region_id}"
    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def metadata(
    region_tag: str,
    region_id: int,
    realm_id: int,
    profile_id: int,
    locale: Optional[str] = None,
):
    """Returns metadata for an individual's profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        realm_id (int): the realm of the profile (1 or 2)
        profile_id (int): the profile ID

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """
    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/metadata/profile/{region_id}/{realm_id}/{profile_id}"
    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def profile(
    region_tag: str,
    region_id: int,
    realm_id: int,
    profile_id: int,
    locale: Optional[str] = None
):
    """Returns data about an individual SC2 profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        realm_id (int): the realm of the profile (1 or 2)
        profile_id (int): the profile ID

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """

    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/profile/{region_id}/{realm_id}/{profile_id}"

    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def ladder(
    region_tag: str,
    region_id: int,
    realm_id: int,
    profile_id: int,
    *,
    ladder_id: Optional[Union[int, str]] = "summary",
    locale: Optional[str] = None,
):
    """Returns a ladder summary, or specific ladder for an individual SC2 profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        realm_id (int): the realm of the profile (1 or 2)
        profile_id (int): the profile ID
        ladder_id (int, optional): the ID of a specific ladder, if desired

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """

    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/profile/{region_id}/{realm_id}/{profile_id}/ladder/{ladder_id}"

    params = {"locale": utils.localize(locale)}

    return uri, params


@sc2_region
@verify_region
def grandmaster(
    region_tag: str, region_id: int, locale: Optional[str] = None
):
    """Returns ladder data for the current season's grandmaster leaderboard.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """

    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/ladder/grandmaster/{region_id}"
    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def season(region_tag: str, region_id: int, locale: Optional[str] = None):
    """Returns data about the current season.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """
    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/ladder/season/{region_id}"
    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def player(region_tag: str, account_id: str, locale: Optional[str] = None):
    """Returns the player data for the provided `account_id`.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        account_id (int): the account ID to request

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
    """

    uri = f"{utils.api_host(region_tag)}/sc2/player/{account_id}"
    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def legacy_profile(
    region_tag: str,
    region_id: int,
    realm_id: int,
    profile_id: int,
    locale: Optional[str] = None,
):
    """Retrieves data about an individual SC2 profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        realm_id (int): the realm of the profile (1 or 2)
        profile_id (int): the profile ID

    Returns:
         tuple: The URL (str) and parameters (dict)

     Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
   """

    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}"
    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def legacy_ladders(
    region_tag: str,
    region_id: int,
    realm_id: int,
    profile_id: int,
    locale: Optional[str] = None,
):
    """Retrieves data about an individual SC2 profile's ladders.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        realm_id (int): the realm of the profile (1 or 2)
        profile_id (int): the profile ID

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """

    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}/ladders"
    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def legacy_match_history(
    region_tag: str,
    region_id: int,
    realm_id: int,
    profile_id: int,
    locale: Optional[str] = None,
):
    """Returns data about an individual SC2 profile's match history.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        realm_id (int): the realm of the profile (1 or 2)
        profile_id (int): the profile ID

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """

    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}/matches"

    params = {"locale": utils.localize(locale)}

    return uri, params


@sc2_region
@verify_region
def legacy_ladder(
    region_tag: str,
    region_id: int,
    ladder_id: int,
    locale: Optional[str] = None,
):
    """Returns data about an individual SC2 profile's match history.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): region for the profile, or use sc2.constants
        ladder_id (int): ladder ID for the request

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """

    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/legacy/ladder/{region_id}/{ladder_id}"
    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def legacy_achievements(
    region_tag: str, region_id: int, locale: Optional[str] = None
):
    """Returns the player data for the provided `account_id`.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): the account ID to request

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """

    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/legacy/data/achievements/{region_id}"

    params = {"locale": utils.localize(locale)}
    return uri, params


@sc2_region
@verify_region
def legacy_rewards(region_tag: str, region_id: int, locale: Optional[str] = None):
    """Returns the player data for the provided `account_id`.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        region_id (int): the account ID to request

    Returns:
        tuple: The URL (str) and parameters (dict)

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetRegionError: when the region tag is 'cn'
        BNetRegionError: when region ID is not valid
    """

    try:
        if region_id not in (1, 2, 3, 5):
            raise BNetRegionError("Invalid Region")
    except ValueError as error:
        raise BNetRegionError(error)

    uri = f"{utils.api_host(region_tag)}/sc2/legacy/data/rewards/{region_id}"

    params = {"locale": utils.localize(locale)}
    return uri, params
