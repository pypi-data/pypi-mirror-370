from battlenet_client.cache.cache import Cache
from battlenet_client.utils import localize, next_update


import sqlite3
import datetime
from typing import Optional
import pathlib
import hashlib
from requests import Response
from abc import ABC, abstractmethod


__author__ = 'David "Gahd" Couples'
__version__ = "1.0.0"


class SQLite(Cache):
    """SQLite backend for cache

    Attributes:
        connection: connection of the database
        cursor: cursor of the database

    """

    @staticmethod
    def adapt_datetime_iso(val):
        """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
        return val.isoformat()

    @staticmethod
    def convert_datetime(val):
        return datetime.datetime.fromisoformat(val.decode())

    def __init__(self, game: str, *, reset: Optional[bool] = False):
        """ Initializes access to the database

        Args:
            filename (str): the filename for the sqlite database

        Keywords:
            reset (bool): flag to reset the database (drop then create empty tables)

        """
        super().__init__(game)

        sqlite3.register_adapter(datetime.datetime, SQLite.adapt_datetime_iso)
        sqlite3.register_converter("datetime", SQLite.convert_datetime)
        self.connection = sqlite3.connect(f"{self.game}_cache.db", 
                                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

        if reset:
            current_dir = pathlib.Path(__file__)
            with open(current_dir / 'cache_db.sql', "r") as config:
                self.cursor.executescript(config.read())

    def __str__(self):
        return f"{self.__class__.__name__} {__version__}"

    def __repr__(self):
        return f"{self.__class__.__name__} {c__version__}"

    def select(self, region: str, release: str, category: str, obj_id: Optional[int] = None) -> bytes:
        """Gathers data from the cache

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the category for the data
            obj_id (int, optional): the ID for the cached data

        Returns:
            (bytes): Returns the data from the cache
        """
        hash_value = hashlib.sha1(f"{game}:{region}:{category}:{release}:{obj_id}".encode()).hexdigest()
        return self.cursor.execute('''select data from cache where hash = ?;''', (hash_value,
                                                                                  )).fetchone()['data']

    def select_all(self, region: str, release: str, category: str, obj_id: Optional[int] = None):
        """Gathers data from the cache

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the category for the data
            obj_id (int, optional): the ID for the cached data

        Returns:
            (bytes): Returns the data from the cache
        """
        hash_value = hashlib.sha1(f"{game}:{region}:{category}:{release}:{obj_id}".encode()).hexdigest()
        results = self.cursor.execute('''select data from cache where hash = ?;''', (hash_value,
                                                                                  )).fetchall()
        return [result['data'] for result in results]

    def delete(self, region: str, release: str, category: str, obj_id: Optional[int] = None) -> int:
        """Removes a row from the cache

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the category for the data
            obj_id (int, optional): the ID for the cached data

        Returns:
            (int): number of rows deleted
        """
        hash_value = hashlib.sha1(f"{game}:{region}:{category}:{release}:{obj_id}".encode()).hexdigest()
        self.cursor.execute('''delete from cache
         where hash = ?;''', (hash_value,))

        self.connection.commit()
        return self.cursor.rowcount

    def submit(self, region: str, release: str, category: str, response: Response,
               obj_id: Optional[int] = None) -> int:
        """Gathers data from the cache

        Args:
            region (str): the game's region
            release (str): the game's release name
            category (str): the data's category
            response (:obj:`Response`): the response from the API
            obj_id (int, optional): the ID for the cached data

        Returns:
            (int): number of rows inserted or updated
        """
        hash_value = hashlib.sha1(f"{game}:{region}:{category}:{release}:{obj_id}".encode()).hexdigest()

        self.cursor.execute('''insert into cache (hash, category, data, next_update) 
                select ?, ?, ?, ?                
                on conflict (hash) do update
                  set data = excluded.data, next_update = excluded.next_update 
                  where next_update < datetime('now');''', (hash_value, cat['ROWID'], response.content,
                                                            self.next_update(response.headers['last-modified'],
                                                                             category)))
        self.connection.commit()
        return self.cursor.rowcount

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
        hash_value = hashlib.sha1(f"{game}:{region}:{category}:{release}:{obj_id}".encode()).hexdigest()
        results = self.cursor.execute('''select datetime('now') > next_update as expired from cache
        where hash = ?;''', (hash_value,)).fetchone()

        if not results or results['expired']:
            return False

        return True

    def category(self, name: str):
        """Returns the category data from the cache

        Args:
            name (str): name of the category

        Returns:
            (:obj:`sqlite3.Row`): the row of for the provided category
        """
        return self.cursor.execute('''select * from categories where name = ?''',
                                   (name,)).fetchone()

