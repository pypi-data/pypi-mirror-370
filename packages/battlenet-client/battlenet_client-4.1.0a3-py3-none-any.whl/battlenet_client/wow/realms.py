"""World of Warcraft Connected Realms and Realm


Classes:
    ConnectedRealm
    Realm
"""

from battlenet_client.wow.base import WoWBase
from battlenet_client.cache.cache import Cache
from battlenet_client.wow.regions import Region
from battlenet_client.wow.game_data import connected_realm, realm
from battlenet_client.utils import slugify

import json
from oic import oic
from requests_oauthlib import OAuth2Session
from typing import Optional, Union, List, Dict


class ConnectedRealm(WoWBase):
    """World of Warcraft Connected Realm

    Connected Realms are multiple instances of :obj:`Realm` where the players can interact with one another,
    as if they are on the same realm.

    Attributes:
        region (:obj:`Region`): The region of the connected realm
        status (str): status of the connected realms
        has_queue (bool):  indication that the connected realms have a queue or not
        population (str): population of the server
        realms (list of :obj:`Realm`): list of :obj:`Realms` that make up this connected realm
        connected_realm_id (int): ID for the connected realm
    """

    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, conn_realm_id: int, *,
                 release: Optional[str] = 'retail', locale: Optional[str] = None, cache: Optional[Cache] = None):
        """Initializes an instance of :obj:`ConnectedRealm`

        Args:
            client (:obj:`OAuth2Session`, :obj:`oic.Client`): used with communications to the API
            region_tag (str): region client is requesting data for
            connected_realm_id (int): requested connected realm ID

        Keyword Args:
            release (str, optional): the release of the game to lookup, defaults to `retail`
            locale (str, optional): the localization to use for the responses, defaults to all
            cache (:obj:`Cache`, optional):

        Raises
            BNetValueError: when the API returns HTTP 404
        """
        (url, params) = connected_realm(region_tag, conn_realm_id, release=release)
        api_data = self.get(client, release, 'connected_realm', url, params, object_id=conn_realm_id,
                            cache=cache)

        super().__init__(region_tag,  api_data['id'], release=release, locale=locale)
        self._status = api_data['status']['name']
        self.has_queue = api_data['has_queue']
        self._population = api_data['population']['name']
        self._realms = [Realm(client, region_tag, obj['id'], release=release, locale=locale, cache=cache)
                        for obj in api_data['realms']]

    def __str__(self):
        return f"{self.__class__.__name__} ({self.realms[0][1][self.locale]} {self.region_tag.upper()})"
    
    def __repr__(self):
        return f"{self.__class__.__name__} ({self.realms[0][1][self.locale]} {self.region_tag.upper()})"

    def __len__(self):
        return len(self.realms)

    @property
    def get_region(self) -> Region:
        """Retrieves the :obj:`Region` of the :obj:`ConnectedRealm`

        Returns:
            (:obj:`Region`): returns the :obj:`Region` for this :obj:`ConnectedRealm`
        """
        return self.realms[0].region

    def get_status(self, locale: Optional[str] = None) -> str:
        """Retrieves the localized status of the :obj:`ConnectedRealm`

        Args:
            locale (str, optional): the localization to retrieve. Defaults to locale of instance

        Returns:
            (str) Localized name of the :obj:`ConnectedRealm`
        """
        return self._localized_data('_status', locale)

    def get_population(self, locale: Optional[str] = None) -> str:
        """Retrieves the localized population of the :obj:`ConnectedRealm`

        Args:
            locale (str, optional): the localization to retrieve. Defaults to locale of instance

        Returns:
            (str) Localized population of the :obj:`ConnectedRealm`
        """
        return self._localized_data('_population', locale)

    def get_realm(self, realm_id: int) -> Realm:
        """Returns if the specified realm IDs is part of this :obj:`ConnectedRealm`

        Args:
            realm_id (int): ID of the realm

        Returns:
            :obj:`Realm`: realm identified by its ID or None if not found
        """
        return self.get_object('_realms', realm_id)


class Realm(WoWBase):
    """Realm of WoW

    Attributes:
        realm_id: (int):  realm's actual id number
        slug (str): simplified string representing the realm
        names (dict of str: str): all the localized names of the realm
        timezone (str): timezone for the realm
        realm_types (str): realm type
        realm_locale (str): realm preferred locale
        category (str): realm's physical country
        is_tournament (bool):  realm used in tournament play
        region (:obj:`Region`): region the realm occupies
    """

    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, realm_id: Union[str, int], *,
                 release: Optional[str] = 'retail', locale: Optional[str] = None, cache: Optional[Cache] = None):
        """Initializes an instance of :obj:`Realm`

        Args:
            client (:obj:`OAuth2Session`, :obj:`oic.Client`): used with communications to the API
            region_tag (str): region client is requesting data for
            realm_id (int, str): realm's ID or slug (simplified name)

        Keyword Args:
            release (str, optional): the release of the game to lookup, defaults to `retail`
            locale (str, optional): the localization to use for the responses, defaults to all
            cache (:obj:`Cache`, optional):

        Raises
            BNetValueError: when the API returns HTTP 404
        """

        if isinstance(realm_id, str):
            realm_id = slugify(realm_id)

        (url, params) = realm(region_tag, realm_id, release=release)
        api_data = self.get(client, self.release, 'realm', url, params, object_id=realm_id, cache=cache)

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)
        self._name = api_data['name']
        self.slug = api_data['slug']
        self.timezone = api_data['timezone']
        self._realm_type = api_data['type']['name']
        self.realm_locale = api_data['locale']
        self._category = api_data['category']
        self.is_tournament = api_data['is_tournament']
        self.region_id = Region(client, region_tag, api_data['region']['id'], release=release, locale=locale,
                                cache=cache)

    def __str__(self):
        return f"{self.name(self.locale) if self.locale else self.name('enus')} ({self.region_tag.upper()})"

    def __repr__(self):
        return f"{self.name(self.locale) if self.locale else self.name('enus')} ({self.region_tag.upper()})"

    def get_name(self, locale: Optional[str] = None) -> str:
        """Retrieves the localized name of the :obj:`Realm` instance

        Args:
            locale (str, optional): the localization to retrieve. Defaults to locale of instance

        Returns:
            (str) Localized name of the :obj:`Realm`
        """
        return self._localized_data('_name', locale)

    def get_realm_type(self, locale: Optional[str] = None) -> str:
        """Retrieves the localized type of the :obj:`Realm` instance

        Args:
            locale (str, optional): the localization to retrieve. Defaults to locale of instance

        Returns:
            (str) Localized type of the :obj:`Realm`
        """
        return self._localized_data('_realm_type', locale)

    def get_category(self, locale: Optional[str] = None) -> str:
        """Retrieves the localized category of the :obj:`Realm` instance

        Args:
            locale (str, optional): the localization to retrieve. Defaults to locale of instance

        Returns:
            (str) Localized category of the :obj:`Realm`
        """
        return self._localized_data('_category', locale)
