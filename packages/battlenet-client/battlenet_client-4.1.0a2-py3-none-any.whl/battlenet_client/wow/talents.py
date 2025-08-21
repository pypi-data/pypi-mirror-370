

from battlenet_client.cache.cache import Cache
from battlenet_client.wow.base import WoWBase, WoWMedia
from battlenet_client.wow.game_data import talent_tree, talent, pvp_talent, tech_talent_tree, tech_talent
from battlenet_client.wow.game_data import tech_talent_media

import json
from typing import Optional, Union
from requests_oauthlib import OAuth2Session
from oic import oic


class TalentTree(WoWBase):
    # TODO: to be added in v4.2.0
    pass


class TalentTreeNode(WoWBase):
    # TODO: to be added in v4.2.0
    pass


class Talent(WoWBase):
    """Talents

    Attributes:
        spell (int):  spell ID related to this talent
        playable_class (int): playable class ID that can use this talent
    """
    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, talent_id: int, *,
                 release: Optional[str] = 'retail', locale: Optional[str] = 'enus', cache: Optional[Cache] = None):

        (url, params) = talent(region_tag, talent_id, release=release)

        api_data = self.get(client, release, 'talent', url, params, object_id=talent_id, cache=cache)

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)

        self.spell = api_data['spell']['id']
        self._rank_descriptions = {rank['id']: rank['description'] for rank in api_data['rank_descriptions']}
        self.playable_class = api_data['playable_class']['id']

    def get_rank_description(self, rank: int, locale: Optional[str] = None) -> str:
        """returns the rank description

        Parameters:
            rank (int): rank ID related to this talent
            locale (str, optional): the locale

        Returns:
            str: the rank int given locale
        """
        locale = locale or self.locale or 'en_US'
        return self.rank_descriptions[rank][locale]


class PvpTalent(WoWBase):
    """PvP Talent

    Attributes:
        spell (int): the spell ID associated with this talent
        playable_spec (int): the playable specialization that can use this talent
        level_unlock (int): the player's level that unlocks this talent
        slots (list of int): the slots that this talent can occupy
    """
    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, talent_id: int, *,
                 release: Optional[str] = 'retail', locale: Optional[str] = 'enus', cache: Optional[Cache] = None):

        (url, params) = pvp_talent(region_tag, talent_id, release=release)

        api_data = self.get(client, release, 'pvp_talent', url, params, object_id=talent_id, cache=cache)

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)

        self.spell = api_data['spell']['id']
        self.playable_spec = api_data['playable_spec']['id']

        self._descriptions = api_data['description']

        self.level_unlock = api_data['unlock_player_level']
        self.slots = api_data['compatible_slots']

    def get_description(self, locale: Optional[str] = None) -> str:
        """Returns the rank description

        Parameters:
            locale (str, optional): the locale

        Returns:
            str: the rank int given locale
        """
        return self._localized_data('_descriptions', locale)


class TechTalentTree(WoWBase):
    # TODO: to be added in v4.2.0
    pass


class TechTalent(WoWBase):
    """Tech Talents

    Tech talents cover talents that are embedded in equipment during the Battle For Azeroth and Shadowlands expansions

    Attributes:
        talent_tree (int): the talent that the talent is part
        tier (int): the tier of the talent
        display_order (int): the order to display the talent
        prerequisite (int): ID of the prerequisite talent
        icon (:obj:`WoWMedia`): the icon of the talent
    """
    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, talent_id: int, *,
                 release: Optional[str] = 'retail', locale: Optional[str] = 'enus', cache: Optional[Cache] = None):

        (url, params) = tech_talent(region_tag, talent_id, release=release)
        api_data = self.get(client, release, 'tech-talent', url, params, object_id=talent_id, cache=cache)

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)

        self.talent_tree = api_data['talent_tree']['id']
        self.tier = api_data['tier']
        self.display_order = api_data['display_order']
        self.prerequisite = api_data['prerequisite_talent']['id']
        self._names = api_data['name']
        self._descriptions = api_data['description']
        self._spell_tooltips = api_data['spell_tooltip']

        (url, params) = tech_talent(region_tag, talent_id, release=release)
        api_data = self.get(client, release, 'tech-talent-media', url, params, object_id=talent_id, cache=cache)
        self.icon = WoWMedia(api_data)

    def get_name(self, locale: Optional[str] = None) -> str:
        return self._localized_data('_names', locale)

    def get_description(self, locale: Optional[str] = None) -> str:
        return self._localized_data('_descriptions', locale)

    def get_spell_tooltip(self, locale: Optional[str] = None) -> Dict[str, str]:
        locale = locale or self.locale or 'en_US'
        return {'name': self._spell_tooltips['spell']['name'][locale],
                'description': self._spell_tooltips['spell']['description'][locale],
                'cast_name': self._spell_tooltips['spell']['cast_time'][locale]}

