"""Defines the Region for World of Warcraft

Classes:
    Region
    Release

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from ..constants import Region as BaseRegion


__version__ = '3.0.1'
__author__ = 'David \'Gahd\' Couples'

VALID_LOCALES = ('en_US', 'es_MX', 'pt_BR', 'ko_KR', 'en_GB', 'es_ES', 'fr_FR', 'ru_RU', 'de_DE', 'pt_PT', 'it_IT',
                 'zh_TW', 'zh_CN')


class Region(BaseRegion):
    class Id:
        """Defines the Region IDs for World of Warcraft"""

        #: Region ID for North America
        NORTH_AMERICA = 1

        #: Region ID for Taiwan
        TAIWAN = 4

        #: Region ID for Europe
        EUROPE = 3

        #: Region ID for Korea
        KOREA = 2

        #: Region ID for China
        CHINA = 5


class Release:
    """Defines the Release Names for World of Warcraft/World of Warcraft Classic"""

    #: Release name for the original World of Warcraft (v 1.0)
    VANILLA = "classic1x"

    #: Release name for re-release of Burning Crusade through latest classic expansion (v 2.0)
    CLASSIC = "classic"

    #: Release name for the current expansion
    RETAIL = "retail"

    @classmethod
    def all(cls) -> list:
        """Returns the list of all releases

        Returns:
            list: list of all releases
        """
        all_list = []
        for name in dir(cls):
            if name.startswith('__'):
                continue

            obj = getattr(cls, name)
            if isinstance(obj, str):
                all_list.append(obj)

        return all_list
