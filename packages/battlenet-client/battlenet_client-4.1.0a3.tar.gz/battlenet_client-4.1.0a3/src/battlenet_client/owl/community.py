"""Defines the functions that handle the community APIs for Diablo III

Functions:
    summary(region_tag, locale)
    player(region_tag, player_id, locale)
    matches(region_tag, match_id, locale)
    follower(region_tag, follower_slug, locale)
    segment(region_tag, segment_id, locale)
    team(region_tag, team_id, locale)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: September 13, 2023
"""

from typing import Union, Optional

from ..decorators import verify_region
from ..utils import localize, api_host


__version__ = "2.0.0"
__author__ = "David \"Gahd\" Couples"


@verify_region
def summary(
    region_tag: str,
    *,
    locale: Optional[str] = None
):
    """Returns a summary of league data

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{api_host(region_tag)}/owl/v1/owl2"

    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def player(
    region_tag: str,
    *,
    player_id: Union[str, int],
    locale: Optional[str] = None
):
    """Returns player data

    Args:
        region_tag (str): region_tag abbreviation
        player_id (str or int):  player ID to query
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{api_host(region_tag)}/owl/v1/players/{player_id}"
    params = {"locale": localize(locale)}
    return uri, params


@verify_region
def match(
    region_tag: str,
    *,
    match_id: Union[str, int],
    locale: Optional[str] = None
):
    """Returns match data

    Args:
        region_tag (str): region_tag abbreviation
        match_id (str or int):  match ID to query
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{api_host(region_tag)}/owl/v1/matches/{match_id}"
    params = {"locale": localize(locale)}
    return uri, params


@verify_region
def segment(
    region_tag: str,
    *,
    segment_id: Union[str, int],
    locale: Optional[str] = None
):
    """Returns match data

    Args:
       region_tag (str): region_tag abbreviation
       segment_id (str or int):  match ID to query
       locale (str): which locale to use for the request

    Returns:
       tuple: The URL (str) and parameters (dict)
    """
    uri = f"{api_host(region_tag)}/owl/v1/segments/{segment_id}"
    params = {"locale": localize(locale)}
    return uri, params


@verify_region
def team(
    region_tag: str,
    *,
    team_id: Union[str, int],
    locale: Optional[str] = None
):
    """Returns team data

    Args:
        region_tag (str): region_tag abbreviation
        team_id (str or int):  match ID to query
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{api_host(region_tag)}/owl/v1/teams/{team_id}"
    params = {"locale": localize(locale)}
    return uri, params
