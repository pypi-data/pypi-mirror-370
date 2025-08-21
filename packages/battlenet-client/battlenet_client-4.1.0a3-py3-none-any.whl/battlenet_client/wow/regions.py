"""World of Warcraft Regions

Classes:
    Region

Author:
    David "Gahd" Couples (gahdania@gahd.io)

License:
    See LICENSE file
"""


__version__ = "1.0.1"


from battlenet_client.wow.base import WoWBase
from battlenet_client.cache.cache import Cache
from battlenet_client.exceptions import BNetValueError, BNetRegionError
from battlenet_client.wow.game_data import region

import json
from oic import oic
from requests_oauthlib import OAuth2Session
from typing import Optional, Union, List, Dict


class Region(WoWBase):
    """World of Warcraft Region

    Attributes:
        tag (str): abbreviation for the :obj:`Region`
        region_id (int): numeric representation for the :obj:`Region`
    """
    
    def __init__(self, client: Union[OAuth2Session, oic.Client], region_tag: str, region_id: Optional[int] = None, *,
                 release: Optional[str] = 'retail', locale: Optional[str] = None, cache: Optional[Cache] = None):
        """Initializes an instance of :obj:`Region`

        Args:
            client (:obj:`OAuth2Session`, :obj:`oic.Client`): used with communications to the API
            region_tag (str): region client is requesting data for
            region_id (int): region ID for the requested region (not to be confused with `region_tag`)

        Keyword Args:
            release (str, optional): the release of the game to lookup, defaults to `retail`
            locale (str, optional): localization to use, defaults to all localizations
            cache (:obj:`Cache`, optional): what cache to use

        Raises:
            BNetValueError: when the API returns a 404 error
        """

        if region_id:
            (url, params) = region(self.region_tag, region_id, release=self.release)
            api_data = self.get(client, release, 'region', url, params, object_id=region_id, cache=cache)

        else:
            # dynamically determine region for `region_tag`
            # api docs call this a `Region Index`
            (url, params) = region(self.region_tag, release=self.release)
            region_index = self.get(client, release, 'region', url, params, cache=cache)

            # bypassing self.get here since
            # URL retrieved above has additional query parameters included
            region_data = client.get(region_index['regions'][0]['href'])
            if region_data.status_code == 404:
                raise BNetValueError(raw_data.text)

            api_data = json.loads(region_data.content)

            if cache:
                cache.submit(self.region_tag, self.release, 'region', region_data, api_data['id'])

        super().__init__(region_tag, api_data['id'], release=release, locale=locale)

        self._names = api_data['name']
        self.tag = api_data['tag']

    def __str__(self):
        return f"{self.name(self.locale) if self.locale else self.name('enus')} ({self.region_tag.upper()})"

    def __repr__(self):
        return f"{self.name(self.locale) if self.locale else self.name('enus')} ({self.region_tag.upper()})"

    def get_name(self, locale: Optional[str] = None) -> str:
        """Retrieves the localized name of the :obj:`Region` instance

        Args:
            locale (str, optional): the localization to retrieve. Defaults to locale of instance

        Returns:
            (str) Localized name of the :obj:`Region`
        """
        return self._localized_data('_names', locale)
