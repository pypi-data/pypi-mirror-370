"""Defines the Achievement related classes for WoW and WoW Classic

Disclaimer:
All rights reserved, Blizzard is the intellectual property owner of WoW and WoW Classic
and any data pertaining thereto

Author:
David "Gahd" Couples <gahdania@gahd.online>
"""
import json

from battlenet_client.wow.base import *
from battlenet_client.wow.game_data import quest, quest_category, quest_type, quest_area


class Quests(WoWBases):
    """Index of the Quests

    Args:
        region_tag (str): the region for the client

    Keyword Args:
        release (str, optional): the release to use.
        locale (str, optional): the localization to use from the API, The default of None means all localizations
        scope (list of str, optional): the scope or scopes to use during the endpoints that require the
            Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal

    Attributes:
        locale (str): the localization string
    """
    
    quests: List[Quest] = field(init=False)

    def __init__(self):

        (url, params) = quest(region_tag, quest_id, release=release, locale=locale)
        if self._cache.check(self.locale, self.release, 'quest'):
            results = self._cache.select(self.locale, self.release, 'quest')
            init_data = results['data']
        else:
            init_data = client.get(url, params=params)
            if init_data.status_code == 404:
                raise BNetValueError("Invalid object ID")
            
            self._cache.submit(self.locale, self.release, 'quest', init_data.content)
                
        api_data = json.loads(init_data)
                              
        self.quests = api_data['quests']
       

class Quest(WoWBase):
    """Index of the Quests

    Args:
        region_tag (str): the region for the client

    Keyword Args:
        release (str, optional): the release to use.
        locale (str, optional): the localization to use from the API, The default of None means all localizations
        scope (list of str, optional): the scope or scopes to use during the endpoints that require the
            Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal

    Attributes:
        locale (str): the localization string
    """
    title: str = field(init=False)
    required_level: int = field(init=False)
    area: QuestArea = field(init=False)
    description: str = field(init=False)
    recommended_levels: tuple = field(init=False)
    requirements: List = field(init=False)
    rewards: List = field(init=False)

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, quest_id: Union[str, int], *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = quest(region_tag, quest_id, release=release, locale=locale)
        
        if self._cache.check(self.locale, self.release, 'quest]', self.object_id):
            results = self._cache.select(self.locale, self.release, 'quest', self.object_id)
            init_data = results['data']
        else:
            init_data = client.get(url, params=params)
            if init_data.status_code == 404:
                raise BNetValueError("Invalid object ID")
            
            self._cache.submit(self.locale, self.release, 'quest', init_data, self.object_id.content)

        api_data = json.loads(init_data)

        self.object_id = api_data['id']
        self.title = api_data['title']
        self.required_level = int(api_data['reqLevel'])
        self.area = QuestArea(client, region_tag, api_data['area']['id'], release=release, locale=locale)
        self.description = api_data['description']
        self.recommended_levels = (int(api_data['recommended_minimum_level']),
                                   int(api_data['recommended_maximum_level']))
        self.requirements = api_data['requirements']
        self.rewards = api_data['rewards']


class QuestCategory:
    """Index of Quest Categories

     Args:
         region_tag (str): region desired for the request\

     Keyword Args:
         release (str, optional): the release to use.
         locale (str, optional): the localization to use from the API, The default of None means all localizations
         scope (list of str, optional): the scope or scopes to use during the endpoints that require the
             Web Application Flow
         redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
         client_id (str): the client ID from the developer portal
         client_secret (str): the client secret from the developer portal

    Attributes:
        locale (str): localization
        quest_categories (list): the list of the available quest categories
    """
    def __init__(self,  client: Union[OAuth2Session, OicClient], region_tag: str, category_id: Union[str, int], *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = quest_category(region_tag, category_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        if not category_id:
            self.quest_categories = data['quest_categories']
        else:
            self.object_id = api_data['id']
            self.name = api_data['category']
            self.quests = api_data['quests']


class QuestArea:
    """Index of Quest Areas

    Args:
        region_tag (str): region desired for the request\

    Keyword Args:
         release (str, optional): the release to use.
         locale (str, optional): the localization to use from the API, The default of None means all localizations
         scope (list of str, optional): the scope or scopes to use during the endpoints that require the
             Web Application Flow
         redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
         client_id (str): the client ID from the developer portal
         client_secret (str): the client secret from the developer portal

    Attributes:
        locale (str): localization
        quest_areas (list): the list of the quest areas
    """
    def __init__(self,  client: Union[OAuth2Session, OicClient], region_tag: str, area_id: Union[str, int], *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = quest_area(region_tag, area_id, release=release, locale=locale)
        if self._cache.check(self.locale, self.release, 'playable_race]', self.object_id):
            results = self._cache.select(self.locale, self.release, 'playable_race', self.object_id)
            init_data = results['data']
        else:

            init_data = client.get(url, params=params)
            if init_data.status_code == 404:
                raise BNetValueError("Invalid object ID")
            
            self._cache.submit(self.locale, self.release, 'playable_race', init_data, self.object_id.content)

        api_data = json.loads(init_data)
        if not area_id:
            self.quest_areas = data['quests']
        else:
            self.area_id = api_data['id']
            self.name = api_data['name']
            self.quests = api_data['quests']


class QuestType:
    """Index of Quest Types

    Args:
        region_tag (str or :obj:`Region`): region desired for the request\

    Keyword Args:
         release (str, optional): the release to use.
         locale (str, optional): the localization to use from the API, The default of None means all localizations
         scope (list of str, optional): the scope or scopes to use during the endpoints that require the
             Web Application Flow
         redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
         client_id (str): the client ID from the developer portal
         client_secret (str): the client secret from the developer portal

    Attributes:
        locale (str): localization
        quest_types (list): the list of the quest areas
    """
    def __init__(self,  client: Union[OAuth2Session, OicClient], region_tag: str, type_id: Union[str, int], *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = quest_type(region_tag, type_id, release=release, locale=locale)

        api_data = client.get(url, params=params)

        if not type_id:
            self.quest_types = data['types']
        else:
            self.type_id = api_data['id']
            self.name = api_data['type']
            self.quests = api_data['quests']
