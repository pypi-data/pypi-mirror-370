"""
Base class for the World of Warcraft classes

WoWBase
"""
from battlenet_client.cache.cache import Cache
from battlenet_client.utils import localize, r_nth_occurrence
from battlenet_client.exceptions import BNetValueError

import json
from typing import Optional, Union, Any, Dict
from requests_oauthlib import OAuth2Session
from requests import Response
from oic import oic
import functools
from pathlib import Path
from urllib import parse
from PIL import Image
from datetime import datetime, timedelta
from abc import ABCMeta, abstractmethod
import urllib.request

__version__ = "v1.0.0"


class WoWBase(object):
    """Base class for classes that handle specific aspects of the game.

    Attributes:
        region_tag (str):  lowercase alphabetical representation for the region the class belongs
        release (str): release of the game
        locale (str):  the localization to use for the requests
    """

    def __init__(self, region_tag: str, object_id: int, *, release: Optional[str] = 'retail',
                 locale: Optional[str] = None):
        self.id = object_id
        self.region_tag = region_tag.lower()
        self.release = release.lower()
        self.locale = localize(locale)

    def __repr__(self):
        return f"{self.__class__.__name__} {__version__}"

    def __str__(self):
        return f"{self.__class__.__name__} {__version__}"

    def __eq__(self, other):
        return self.id == other.id

    def get(self, client: Union[OAuth2Session, oic.Client], release: str, category: str, url: str,
            params: Dict[str, Any], *, object_id: Optional[int] = None,
            cache: Optional[Cache] = None) -> Dict[str, Any]:
        """Returns the data from either the cache or the API

        Args:
            client (:obj:`OAuth2Session` or :obj:`oic.Client`): the client to communicate with the API
            release (str): the release of World of Warcraft
            category (str): category the API request
            url (str): the URL to the API endpoint
            params (dict of str,str): parameters to pass to the API
            object_id (int, optional): the ID to pass to the API endpoint
            cache (:obj:`Cache`, optional): cache to use
        """

        if cache:
            if cache.check(self.region_tag, release, category, object_id):
                return json.loads(cache.select(self.region_tag, release, category, object_id))

        api_data = client.get(url, params=params)

        if api_data.status_code == 404:
            raise BNetValueError(api_data.text)

        if cache:
            cache.submit(self.region_tag, release, category, api_data, object_id)

        return json.loads(api_data.content)

    def _localized_data(self, field_name: str, locale: Optional[str] = None):
        """Returns the data from `field_name` localized by the given `locale`

        Args:
            field_name (str): the member variable to localize
            locale (str, optional): locale to select.

        Returns:
            (str): the localized value for `field_name`
        """

        attrib = getattr(self, field_name)
        locale = localize(locale or self.locale or 'en_US')

        if localization in attrib.keys():
            return attrib[localization]

        if self.locale in attrib.keys():
            return attrib[self.locale]

        return attrib['en_US']

    def _gender_data(self, field_name: str, gender: str, locale: Optional[str] = None):
        """Returns the selected form of `field_name` based on the provided `gender` and `locale`

        Args:
            field_name (str): the member variable to select
            locale (str, optional): the locale to select

        Returns:
            (str): the selected result from `field_name`
        """
        localized_data = getattr(self, field_name)[gender]
        localization = localize(locale or self.locale or 'en_US')
        return localized_data[localization]


class WoWMedia(object):
    """Media Storage

    Attributes:
        image (:obj:`PIL.Image`):  File pointer for image
        object_id (int): ID for the object
        assets (list of dict):  the assets associated with the object
    """
    def __init__(self, media_info: Dict[str, Any], fs_path: Optional[str] = '.'):
        """Initializes the Media object

        Args:
            media_info (dict): the data from the media API endpoint
            fs_path (str): the filesystem path to store the files
        """
        self._image = None
        self._blizzard_url = media_info['assets'][0]['value']
        self._file_id = media_info['assets'][0]['file_data_id']

        self.url = r_nth_occurrence(self._blizzard_url, '/', 3)
        self._file = Path(fs_path).parent / self.url

        if not self._file.parent.exists():
            self._file.parent.mkdir(parents=True)

        if not self._file.exists():
            urllib.request.urlretrieve(self._blizzard_url, self._file)

        mod_time = datetime.fromtimestamp(self._file.stat().st_mtime)
        if mod_time + timedelta(weeks=1) < datetime.now():
            self._file.unlink(missing_ok=True)
            urllib.request.urlretrieve(self._blizzard_url, self._file)

    def __del__(self):
        if self._image:
            self._image.close()

    def open(self):
        """Opens the media file
        """
        if self._file.exists():
            self._image = Image.open(self._file)

    def show(self):
        if not self._image:
            self.open()

        self._image.show()

    @property
    def size(self):
        if self._image:
            return self._image.size
