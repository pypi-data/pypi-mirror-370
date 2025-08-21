""" Cache interface

"""
import datetime

from typing import Optional, Union
from requests_oauthlib import OAuth2Session
from oic import oic
from requests import Response
from abc import ABC, abstractmethod

__version__ = '1.0.0'
__author__ = 'David "Gahd" Couples'


class Cache(ABC):
    """Base Cache Object"""

    def __init__(self, game: str):
        """Initializes the :obj:`Cache`"""
        self.game = game.lower()

    def __str__(self):
        return f"{__class__.__name__} {__version__}"

    def __repr__(self):
        return f"{__class__.__name__} {__version__}"

    @abstractmethod
    def select(self, region: str, release: str, category: str, obj_id: Optional[int] = None) -> bytes:
        """Gathers one row of data from the cache

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the category for the data
            obj_id (int, optional): the ID for the cached data

        Returns:
            (bytes): Returns the data from the cache
        """
        pass

    @abstractmethod
    def select_all(self, region: str, release: str, category: str, obj_id: Optional[int] = None):
        """Gathers all rows of data from the cache

                Args:
                    region (str): the game's region
                    release (str): the game's release name
                    category (str): the category for the data
                    obj_id (int, optional): the ID for the cached data

                Returns:
                    (bytes): Returns the data from the cache
                """
        pass

    @abstractmethod
    def delete(self, region: str, release: str, category: str, obj_id: Optional[int] = None) -> int:
        """Removed items from the cache

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the category for the data
            obj_id (int, optional): the ID for the cached data

        Returns:
            (int): number of rows deleted
        """
        pass

    @abstractmethod
    def check(self, region: str, release: str, category: str, obj_id: Optional[int] = None) -> bool:
        """Returns if the data is found and if it is expired

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the data's category
            obj_id (int, optional): the ID for the cached data

        Returns:
            (bool): True if the object is found and has not expired. False otherwise
        """
        pass

    @abstractmethod
    def submit(self, region: str, release: str, category: str,  response: Response,
               obj_id: Optional[int] = None) -> int:
        """Adds or updates data to/in the cache

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the data's category
            response (:obj:`Response`): the response object from the API
            obj_id (int, optional): the ID for the cached data

        Returns:
            (int): number of rows inserted or updated
        """
        pass

    @abstractmethod
    def category(self, name: str):
        """Returns the category data from the cache

        Args:
            name (str): name of the category

        Returns:
            (cache dependant): the row of for the provided category
        """
        pass

    def next_update(self, last_modified: str, category_name: str):
        """Returns the next update value

        Args:
            last_modified (str): string of the last modified value from the API
            category_name (str): name of the category

        Returns:
            :obj:`datetime`: the datetime of the next update
        """
        last_modified = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        last_modified += timedelta(weeks=self.category(category_name)['duration'])
        return last_modified
