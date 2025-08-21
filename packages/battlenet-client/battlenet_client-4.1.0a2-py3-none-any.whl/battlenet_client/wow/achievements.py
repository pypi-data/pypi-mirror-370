"""Defines the Achievement related classes for WoW and WoW Classic


Disclaimer:
All rights reserved, Blizzard is the intellectual property owner of WoW and WoW Classic
and any data pertaining thereto

Author:
David "Gahd" Couples <gahdania@gahd.online>
"""
from battlenet_client.wow.base import *
from battlenet_client.wow.game_data import achievement, achievement_category, achievement_media

from typing import Union, Optional
from requests_oauthlib import OAuth2Session
from oic import oic


class AchievementCategory(WoWBase):
    """Defines the index achievement categories within World of Warcraft

    Args:
        region_tag (str): region abbreviation for use with the APIs

    Keyword Args:
        release (str, optional): the release to use.
        locale (str, optional): the localization to use from the API, The default of None means all localizations
        scope (list of str, optional): the scope or scopes to use during the endpoints that require the
            Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal

    Attributes:
        general (list of dict): the entire index of the categories
        root (list of dict): the index of the root categories
        guild (list of dict): the index of the guild categories

    Notes:
        This class no longer functions as it was when originally created. Blizzard changed the Index into a list of
            IDs and URLs, vice a list of the actual achievement categories (including the data)
    """

    def __init__(self, client: Union[OAuth2Session, oic.Client], category_id: Optional[int] = None, *,
                 release: Optional[str] = None, locale: Optoinal[str] = None):
        (url, params) = achievement_category(region_tag, category_id=category_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)

        self.category_id = api_data['id']
        self.name = api_data['name']
        self.achievements = api_data['achievements']
        self.alliance = api_data['aggregates_by_faction']['alliance']
        self.horde = api_data['aggregates_by_faction']['horde']
        self.is_guild_category = bool(api_data['is_guild_category'])
        self.icon = api_data['media']['key']

    def __str__(self):
        return self.__class__.__name__


class Achievement:
    """Defines the index achievements within World of Warcraft

    Args:
        region_tag (str): region abbreviation for use with the APIs

    Keyword Args:
        release (str, optional): the release to use.
        locale (str, optional): the localization to use from the API, The default of None means all localizations
        scope (list of str, optional): the scope or scopes to use during the endpoints that require the
            Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal

    Attributes:
        achievements (list of dict): the list of the achievements

    Notes:
        This class no longer functions as it was when originally created. Blizzard changed the Index into a list of
            IDs and URLs, vice a list of the achievements (including the data)
    """

    def __init__(self, client: Union[OAuth2Session, OicClient], achievement_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = achievement(region_tag, achievement_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        if not achievement_id:
            self.achievements = api_data['achievements']
        else:
            self.achievement_id = api_data['id']
            self.name = api_data['name']
            self.description = api_data['description']
            self.points = int(api_data['points'])
            self.is_account_wide = bool(api_data['is_account_wide'])
            self.criteria = api_data['criteria']
            self.icon = api_data['media']['key']['href']

    def __str__(self):
        return self.__class__.__name__
