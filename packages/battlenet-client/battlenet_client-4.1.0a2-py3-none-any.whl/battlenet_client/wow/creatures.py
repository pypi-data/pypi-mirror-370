"""Defines the Achievement related classes for WoW and WoW Classic

Disclaimer:
All rights reserved, Blizzard is the intellectual property owner of WoW and WoW Classic
and any data pertaining thereto

Author:
David "Gahd" Couples <gahdania@gahd.online>
"""

from typing import Union, Optional
from battlenet_client.wow.game_data import creature_family, creature_type, creature_family_media
from battlenet_client.wow.game_data import creature_display_media, creature


class CreatureFamily:

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, family_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = creature_family(region_tag, family_id, release=release, locale=locale)

        api_data = client.get(url, params=params)

        if not family_id:
            self.creature_families = api_data['creature_families']
        else:
            self.object_id = api_data['id']
            self.name = api_data['name']
            self.spec = api_data['specialization']
            self.media = api_data['media']['key']['href']


class CreatureType:

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, type_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = creature_type(region_tag, type_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        if not type_id:
            self.creature_types = api_data['creature_types']
        else:
            self.object_id = api_data['id']
            self.name = api_data['name']


class Creature:

    def __init__(self, region_tag, creature_id, *, release=None, locale=None,  client=None):

        self.object_id = None
        self.name = None
        self.type = None
        self.family = None
        self.display_media = None
        self.is_tamable = None

        (url, params) = creature(region_tag, creature_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        self.object_id = api_data['id']
        self.name = api_data['name']
        self.type = CreatureType(client, api_data['type']['id'], release=release, locale=locale)
        self.family = CreatureFamily(client, api_data['family']['id'], release=release, locale=locale)
        self.display_media = api_data['creature_displays']['key']['href']
        self.is_tamable = bool(api_data['is_tamable'])
