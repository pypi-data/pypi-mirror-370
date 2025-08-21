"""Defines the classes that handle the game data APIs for Starcraft 2

Functions:
    league_data(region_tag, season_id, queue_id, team_type, league_id, locale)

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
def league_data(
    region_tag: str,
    season_id: str,
    queue_id: str,
    team_type: str,
    league_id: str,
    locale: Optional[str] = None,
):
    """Returns data for the specified season, queue, team, and league.

    queueId: the standard available queueIds are: 1=WoL 1v1, 2=WoL 2v2, 3=WoL 3v3, 4=WoL 4v4, 101=HotS 1v1,
        102=HotS 2v2, 103=HotS 3v3, 104=HotS 4v4, 201=LotV 1v1, 202=LotV 2v2, 203=LotV 3v3, 204=LotV 4v4,
        206=LotV Archon. Note that other available queues may not be listed here.

    teamType: there are two available teamTypes: 0=arranged, 1=random.

    leagueId: available leagueIds are: 0=Bronze, 1=Silver, 2=Gold, 3=Platinum, 4=Diamond, 5=Master, 6=Grandmaster.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        season_id (str): The season ID of the data to retrieve.
        queue_id (str): The queue ID of the data to retrieve.
        team_type (str): The team type of the data to retrieve.
        league_id (str): The league ID of the data to retrieve.

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/sc2/league/{season_id}/{queue_id}/{team_type}/{league_id}"
    params = {"locale": utils.localize(locale)}
    return uri, params
