"""Defines the generic Region

Classes:
    Region

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""

__version__ = '1.0.0'
__author__ = 'David \'Gahd\' Couples'


VALID_REGIONS = ('us', 'kr', 'eu', 'tw', 'cn')


class Region:

    class Tag:
        """Defines the region's abbreviation (tag)"""

        #: Region abbreviation for North America
        NORTH_AMERICA = VALID_REGIONS[0]

        #: Region abbreviation for North Europe
        EUROPE = VALID_REGIONS[2]

        #: Region abbreviation for Taiwan
        TAIWAN = VALID_REGIONS[3]

        #: Region abbreviation for Korea
        KOREA = VALID_REGIONS[1]

        #: Region abbreviation for China
        CHINA = VALID_REGIONS[4]

    class Id:
        """Defines the Region IDs for Diablo III, Starcraft 2, and Hearthstone"""

        #: Region ID for North America
        NORTH_AMERICA = 1

        #: Region ID for Europe
        EUROPE = 2

        #: Region ID for Korea and Taiwan (APAC)
        APAC = 3

        #: Region ID for China
        CHINA = 5


class Release:
    class Tag:
        """Defines the release's abbreviation (tag)"""
        RETAIL = "retail"
        CLASSIC = "classic1x"
        CLASSIC_PROG = "classic"
        ALL = RETAIL, CLASSIC, CLASSIC_PROG
