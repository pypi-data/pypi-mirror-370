"""Playable Race, Class, and Specializations for World of Warcraft

A class in World of Warcraft, a job the character does.

Author:
David "Gahd" Couples <gahdania@gahd.online>
"""
from battlenet_client.wow.base import WoWBase, WoWMedia
from battlenet_client.cache.cache import Cache
from battlenet_client.exceptions import BNetValueError
from battlenet_client.wow.game_data import playable_race, playable_class, playable_class_media
from battlenet_client.wow.game_data import playable_spec, playable_spec_media, pvp_talent, power_type
from battlenet_client.utils import localize, slugify

import json
from oic import oic
from requests_oauthlib import OAuth2Session
from typing import Optional, Union, List, Dict


class PowerType(WoWBase):
    """Playable Specialization
    """
    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, power_type_id: int, *,
                 release: Optional[str] = 'retail', locale: Optional[str] = 'enus', cache: Optional[Cache] = None):
        """Initializes :obj:`PowerType`

        Args:
            client (:obj:`OAuth2Session` or :obj:`oic.Client`): the client to communicate to the API
            region_tag (str): the region abbreviation
            class_id (int): the ID of the class

        Keywords Args:
            release (str): release of the game
            locale (str): localization to use
            cache (:obj:`Cache`): the cache to use for storage
        """
        (url, params) = power_type(region_tag, power_type_id, release=release)
        api_data = self.get(client, release, 'power-type', url, params, object_id=power_type_id, cache=cache)

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)

        self._names = api_data['name']

    def __str__(self):
        return f"{self.get_name(self.locale) if self.locale else self.get_name('en_US')} ({self.region_tag.upper()})"

    def __repr__(self):
        return f"{self.get_name(self.locale) if self.locale else self.get_name('en_US')} ({self.region_tag.upper()})"

    def get_name(self, locale: Optional[str] = None):
        """Returns the name of the faction by `locale`

        Args:
            locale (str: optional): locale to reference.  Defaults to this :obj:`PlayableRace` locale

        Returns:
            str: the localized name

        Note:
            Some languages have nouns that have gender.
        """
        return self._localized_data('_names', locale)


class PlayableSpecialization(WoWBase):
    """Playable Specialization

    Attributes:
        icon (:obj:`Image`): stores info about the icon
        playable_class (:obj:`PlayableClass`): the playable class that uses this specialization
        talent_tree_url (str): URL for the talent tree
        pvp_talents (dict): the Person Versus Person (PvP) talents
        icon (:obj:`WoWMedia): icon of the spec
    """
    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, spec_id: int, *,
                 release: Optional[str] = 'retail', locale: Optional[str] = 'enus', cache: Optional[Cache] = None):
        """Initializes :obj:`PlayableSpecialization`

        Args:
            client (:obj:`OAuth2Session` or :obj:`oic.Client`): the client to communicate to the API
            region_tag (str): the region abbreviation
            class_id (int): the ID of the class

        Keywords Args:
            release (str): release of the game
            locale (str): localization to use
            cache (:obj:`Cache`): the cache to use for storage
        """
        (url, params) = playable_spec(region_tag, spec_id, release=release)
        api_data = self.get(client, release, 'playable-specialization', url, params, object_id=spec_id,
                            cache=cache)

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)

        self._names = api_data['name']
        self._descriptions = {key: value for key, value in api_data['gender_description'].items()}
        self._roles = api_data['role']['name']
        self._primary_stat = api_data['primary_stat_type']['name']

        if api_data['playable_class']['id'] > 0:
            self.playable_class = api_data['playable_class']['id']

        if 'spec_talent_tree' in api_data.keys():
            self.talent_tree_url = api_data['spec_talent_tree']['key']['href']

        if 'pvp_talents' in api_data.keys():
            self.pvp_talents = api_data['pvp_talents']

        (url, params) = playable_spec_media(region_tag, spec_id, release=release)
        api_data = self.get(client, release, 'playable-specialization-media', url, params, object_id=spec_id,
                            cache=cache)
        self.icon = WoWMedia(api_data)

    def __str__(self):
        return f"{self.get_name(self.locale) if self.locale else self.get_name('en_US')} ({self.region_tag.upper()})"

    def __repr__(self):
        return f"{self.get_name(self.locale) if self.locale else self.get_name('en_US')} ({self.region_tag.upper()})"

    def get_description(self, gender: Optional[str] = 'neutral', locale: Optional[str] = None):
        """Returns the description of the specialization by gender and locale.

        Args:
            gender (str: optional): gender to reference.  Defaults to `female`
            locale (str: optional): locale to reference.  Defaults to this :obj:`PlayableSpecialization` locale

        Returns:
            str: the localized name for the given gender

        Note:
            Some languages have nouns that have gender.
        """
        return self._gender_data('_descriptions', gender, locale)

    def get_name(self, locale: Optional[str] = None):
        """Returns the name of the faction by `locale`

        Args:
            locale (str: optional): locale to reference.  Defaults to this :obj:`PlayableRace` locale

        Returns:
            str: the localized name for the given gender

        Note:
            Some languages have nouns that have gender.
        """
        return self._localized_data('_names', locale)

    def get_role(self, locale: Optional[str] = None):
        """Returns the name of the faction by `locale`

        Args:
            locale (str: optional): locale to reference.  Defaults to this :obj:`PlayableRace` locale

        Returns:
            str: the localized name for the given gender

        Note:
            Some languages have nouns that have gender.
        """
        return self._localized_data('_roles', locale)

    def get_primary_stat(self, locale: Optional[str] = None):
        """Returns the name of the faction by `locale`

        Args:
            locale (str: optional): locale to reference.  Defaults to this :obj:`PlayableRace` locale

        Returns:
            str: the localized name for the given gender

        Note:
            Some languages have nouns that have gender.
        """
        return self._localized_data('_primary_stats', locale)


class PlayableClass(WoWBase):
    """Defines the playable class.


    Attributes:
        class_id (int): playable class ID
        names (dict of str): localized names of the class
        power_type (:obj:`PowerType`):  power type used for class, IE mana, rage, fury, focus
        icon (:obj:`WoWMedia`):  the class specific icon
        specializations (list of :obj:`PlayableSpecialization`): the available specializations for the class
        additional_power_type (:obj:`PowerType`): the additional power type used by the class, IE maelstrom stacks
        races (list of :obj:`PlayableRace`): the races that can be the class
    """
    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, class_id: int, *,
                 release: Optional[str] = 'retail', locale: Optional[str] = 'enus', cache: Optional[Cache] = None):
        """Initializes the :obj:`PlayableClass`

        Args:
            client (:obj:`OAuth2Session` or :obj:`oic.Client`): the client to communicate to the API
            region_tag (str): the region abbreviation
            class_id (int): the ID of the class

        Keywords Args:
            release (str): release of the game
            locale (str): localization to use
            cache (:obj:`Cache`): the cache to use for storage
        """
        (url, params) = playable_class(region_tag, class_id, release=release)
        api_data = self.get(client, release, 'playable-class', url, params, object_id=class_id,
                            cache=cache)

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)

        self._names = {'female': api_data['gender_name']['female'], 'male': api_data['gender_name']['male'],
                       'neutral': api_data['name']}
        self.power_type = api_data['power_type']['id']

        self._specializations = [spec['id'] for spec in api_data['specializations']]
        self._additional_power_types = [power['id'] for power in api_data['additional_power_types']]
        self._races = [race['id'] for race in api_data['playable_races']]

        (url, params) = playable_class_media(region_tag, self.id, release=release)
        api_data = self.get(client, release, 'playable-class-media', url, params, object_id=self.id,
                            cache=cache)

        self.icon = WoWMedia(api_data)

    def __str__(self):
        name = self.get_name(locale=self.locale) if self.locale else self.get_name(locale='en_US')
        return f"{name} ({self.region_tag.upper()})"

    def __repr__(self):
        name = self.get_name(locale=self.locale) if self.locale else self.get_name(locale='en_US')
        return f"{name} ({self.region_tag.upper()})"

    def get_name(self, gender: Optional[str] = 'neutral', locale: Optional[str] = None) -> str:
        """Returns the name of the race by gender and locale.

        Args:
            gender (str: optional): gender to reference.  Defaults to `female`
            locale (str: optional): locale to reference.  Defaults to this :obj:`PlayableRace` locale

        Returns:
            str: the localized name for the given gender

        Note:
            Some languages have nouns that have gender.
        """
        return self._gender_data('_names', gender, locale)

    def is_additional_power_type_usable(self, power_type_id: int) -> bool:
        """ Returns the power type of

        Args:
            power_type_id (int): ID of the power type

        Returns:
            :obj:`Realm`: realm identified by its ID or None if not found
        """
        return power_type_id in self._additional_power_types

    def is_race_usable(self, race_id: int) -> bool:
        """ Returns if the race identified by `race_id` is used by :obj:`PlayableClass`

        Args:
            race_id (int): ID of the power type

        Returns:
            :obj:`PlayableRace`: realm identified by its ID or None if not found
        """
        return race_id in self._races

    def is_spec_usable(self, spec_id: int) -> bool:
        """ Returns if the race identified by `race_id` is used by :obj:`PlayableClass`

       Args:
           spec_id (int): ID of the specialization

       Returns:
           :obj:`PlayableRace`: realm identified by its ID or None if not found
       """
        return spec_id in self._specializations


class PlayableRace(WoWBase):
    """Playable Race

    Attributes:
        id (int): the playable race's ID
        faction (str): the faction the playable race is
        female_name (str): the feminine version of the name in localizations that support noun gender (romance lang)
        male_name (str): the masculine version of the name in localizations that support noun gender (romance lang)
        name (str): the neuter form
        is_selectable (bool): flag where the playable race selectable on the character select screen
        is_allied_race (bool): flag where the playable race is an allied race
    """
    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, race_id: int, *,
                 release: Optional[str] = 'retail', locale: Optional[str] = None, cache: Optional[Cache] = None):
        """Initializes this instance of :obj:`PlayableRace`

        Args:
            client (object: `Requests`): OIDC/OAuth v2 compatible client
            region_tag (str): region abbreviation for use with the APIs
            race_id (str, int, optional):  race id to use
            release (str, optional): the release to use. Defaults to "retail"
            locale (str, optional): the localization to use from the API.  None uses region_tag's default locale

        Note:
            Playable Race does not have a media type. See :obj:`Character`
        """
        (url, params) = playable_race(region_tag, race_id, release=release)
        api_data = self.get(client, release, 'playable-race', url, params, object_id=race_id, cache=cache)

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)
        self._factions = api_data['faction']['name']
        self._names = {key: value for key, value in api_data['gender_name'].items()}
        self._names.update({'neutral': api_data['name']})
        self.is_selectable = bool(api_data['is_selectable'])
        self.is_allied_race = bool(api_data['is_allied_race'])
        self._available_classes = [cls['id'] for cls in api_data['playable_classes']]

    def __str__(self) -> str:
        name = self.get_name(locale=self.locale) if self.locale else self.get_name(locale='en_US')
        return f"{name} ({self.region_tag.upper()})"

    def __repr__(self) -> str:
        name = self.get_name(locale=self.locale) if self.locale else self.get_name(locale='en_US')
        return f"{name} ({self.region_tag.upper()})"

    def get_name(self, gender: Optional[str] = 'neutral', locale: Optional[str] = None) -> str:
        """Returns the name of the race by gender and locale.

        Args:
            gender (str: optional): gender to reference.  Defaults to `female`
            locale (str: optional): locale to reference.  Defaults to this :obj:`PlayableRace` locale

        Returns:
            str: the localized name for the given gender

        Note:
            Some languages have nouns that have gender.
        """
        return self._gender_data('_names', gender, locale)

    def get_faction(self, locale: Optional[str] = None) -> str:
        """Returns the name of the faction by `locale`

        Args:
            locale (str: optional): locale to reference.  Defaults to this :obj:`PlayableRace` locale

        Returns:
            str: the localized name for the given gender

        Note:
            Some languages have nouns that have gender.
        """
        return self._localized_data('_factions', locale)

    def is_playable_class_available_to_race(self, class_id: int) -> bool:
        """ Returns if the playable class identified by `class_id` available to :obj:`PlayableRace`

        Args:
            class_id (int): ID of the player class

        Returns:
            :obj:`Realm`: realm identified by its ID or None if not found
        """
        return class_id in self._available_classes
