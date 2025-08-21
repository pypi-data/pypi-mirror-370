from .cache import Cache
from battlenet_client.utils import localize, next_update

from pymongo import MongoClient, ReturnDocument
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json
from os import path
from requests import Response


__version__ = 'v1.0.0'


class Mongo(Cache):

    def __init__(self, game: str, db_user: str, db_pass: str,  host: Optional[str] = '127.0.0.1',
                 port: Optional[int] = 27017, *, reset: Optional[bool] = False):
        super().__init__(game)

        db_url = f"mongodb://{db_user}:{db_pass}@{host}:{port}/cache"

        self._client = MongoClient(db_url)
        self._database = self._client['cache']
        self._cache = self._database[self.game]
        self._categories = self._database['categories']

        if reset:
            self._cache.drop()
            self._categories.drop()

            categories = list()
            current_dir = path.dirname(path.realpath(__file__))
            with open(f"{current_dir}/data.txt", "r") as config:
                for line in config.readlines():
                    categories.append(json.loads(line))

            self._categories.insert_many(categories)

    def __str__(self):
        return f"{self.__class__.__name__} {__version__}"

    def __repr__(self):
        return f"{self.__class__.__name__} {__version__}"

    def select(self, region: str, release: str, category: str, obj_id: Optional[int] = None):
        """Gathers data from the cache

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the category for the data
            obj_id (int, optional): the ID for the cached data

        Returns:
            (bytes): Returns the data from the cache
        """
        cache_data = self._cache.find_one({"region": region, "release": release, "category": category,
                                           "object_id": obj_id}, projection={'data': True, '_id': False})

        return cache_data['data']

    def select_all(self, region: str, release: str, category: str, obj_id: Optional[int] = None) -> List[bytes]:
        cache_data = self._cache.find({"region": region, "release": release, "category": category,
                                      "object_id": obj_id}, projection={'data': true, '_id': False})

        return [x['data'] for x in cache_data]

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
        deleted_data = self._cache.find_one_and_delete({'region': region, 'release': release, 'category': category,
                                                        'object_id': obj_id})
        if deleted_data:
            return 1

        return 0

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
        check_data = self._cache.find_one({"region": region, "release": release, "category": category,
                                           "object_id": obj_id,
                                           'next_update': {'$gte': datetime.datetime.now(datetime.UTC)}},
                                          projection={'next_update': True, '_id': False})

        return True if check_data else False

    def submit(self, region: str, release: str, category: str,  response: Response,
               obj_id: Optional[int] = None) -> int:
        """Adds or updates data to/in the cache

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the data's category
            response (:obj:`Response`): the response from the API endpoint
            obj_id (int, optional): the ID for the cached data

        Returns:
            (int): number of rows inserted or updated
        """
        submitted_document = self._cache.find_one_and_update(
            {"region": region, "release": release, "category": category, "object_id": obj_id},
            {
                "$set": {"data": data, "next_update": self.next_update(response.headers['last-modified'],
                                                                       category)},
                "$setOnInsert": {"region": region, "release": release, "category": category, "object_id": obj_id}},
            {"data": 1}, upsert=True,
            return_document=ReturnDocument.AFTER)

        return 1 if submitted_document else 0

    def category(self, name: str):
        """Returns the category data from the cache

        Args:
            name (str): name of the category

        Returns:
            (:obj:`pymongo.Row`): the row of for the provided category
        """
        return self._categories.find_one({"name": name})
