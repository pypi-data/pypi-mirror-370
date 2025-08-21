"""Defines the functions that handle the game data APIs for Diablo III

Functions:
    season(region_tag, season_id, locale)
    season_leaderboard(region_tag, season_id, leaderboard_id, locale)
    era(region_tag, era_id, locale)
    era_leaderboard(region_tag, era_id, leaderboard_id, locale)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from typing import Optional

from .. import utils
from ..decorators import verify_region


__version__ = '2.0.0'
__author__ = 'David \'Gahd\' Couples'


@verify_region
def season(
    region_tag: str,
    season_id: Optional[int] = None,
    locale: Optional[str] = None,
):
    """Returns an index of available seasons, or a leaderboard list for
    the specified season.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        season_id (int): the ID of the season

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/d3/season/"
    if season_id:
        uri += f"{season_id}"

    params = {"locale": utils.localize(locale)}

    return uri, params


@verify_region
def season_leaderboard(
    region_tag: str,
    season_id: int,
    leaderboard_id: str,
    locale: Optional[str] = None,
):
    """Returns the specified leaderboard for the specified season.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        season_id (int): the ID of the season
        leaderboard_id (Str): the slug of the leaderboard

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/d3/season/{season_id}/leaderboard/{leaderboard_id}"
    params = {"locale": utils.localize(locale)}

    return uri, params


@verify_region
def era(
    region_tag: str,
    era_id: Optional[int] = None,
    locale: Optional[str] = None,
):
    """Returns an index of available eras, or a leaderboard list for a
    particular era.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        era_id (int): the ID of the era

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/d3/era/"
    if era_id:
        uri += f"{era_id}"

    params = {"locale": utils.localize(locale)}

    return uri, params


@verify_region
def era_leaderboard(
    region_tag: str,
    era_id: int,
    leaderboard_id: str,
    locale: Optional[str] = None,
):
    """Returns the specified leaderboard for the specified era.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        era_id (int): the ID of the season
        leaderboard_id (str): the slug of the leaderboard

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/d3/era/{era_id}/leaderboard/{leaderboard_id}"
    params = {"locale": utils.localize(locale)}
    return uri, params
