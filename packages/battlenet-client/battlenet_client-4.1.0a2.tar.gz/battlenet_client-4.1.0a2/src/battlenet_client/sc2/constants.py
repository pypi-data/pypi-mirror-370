"""Defines the Region for Starcraft 2

Classes:
    Region
    QueueID
    TeamType
    LeagueID

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from battlenet_client.constants import Region as BaseRegion


__version__ = '1.0.0'
__author__ = 'David \'Gahd\' Couples'


class Region(BaseRegion):
    """Defines the Regions for Starcraft 2"""
    pass


class QueueID:
    """Defines the Queue IDs for Starcraft 2"""
    WoL_1v1 = 1
    WoL_2v2 = 2
    WoL_3v3 = 3
    WoL_4v4 = 4
    HotS_1v1 = 101
    HotS_2v2 = 102
    HotS_3v3 = 103
    HotS_4v4 = 104
    LotV_1v1 = 201
    LotV_2v2 = 202
    LotV_3v3 = 203
    LotV_4v4 = 204
    LotV_Archon = 206


class TeamType:
    """Defines the Team Types for Starcraft 2"""
    ARRANGED = 0
    RANDOM = 1


class LeagueID:
    """Defines the League IDs for Starcraft 2"""
    BRONZE = 0
    SILVER = 1
    GOLD = 2
    PLATINUM = 3
    DIAMOND = 4
    MASTER = 5
    GRANDMASTER = 6
