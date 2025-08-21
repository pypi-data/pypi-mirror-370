"""Defines the Mythic Keystone Classes

Disclaimer:
All rights reserved, Blizzard is the intellectual property owner of WoW and WoW Classic
and any data pertaining thereto

Author:
David "Gahd" Couples <gahdania@gahd.online>
"""
from datetime import datetime

from battlenet_client.wow.game_data import mythic_keystone_affix, mythic_keystone_dungeon, mythic_keystone_index
from battlenet_client.wow.game_data import mythic_keystone_season, mythic_keystone_leaderboard


class MythicKeystoneAffix:
    """Index of Mythic Keystone Affixes

    Args:
        region_tag (str): region desired for the request

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
        affixes (list): the list of the quest areas
    """

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, affix_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = mythic_keystone_affix(region_tag, affix_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        if not affix_id:
            self.affixes = api_data['affixes']
        else:
            self.affix_id = api_data['id']
            self.name = api_data['name']
            self.description = api_data['description']
            # media = self._client.mythic_keystone_affix_media(affix_id)
            # self.media = Image.open(self._client.get(media['assets'][0]['value']))


class MythicKeystoneDungeon:
    """Index of Mythic Keystone Dungeons

    Args:
        region_tag (str): region desired for the request

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
        dungeons (list): the list of the quest areas
    """
    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, dungeon_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = mythic_keystone_dungeon(region_tag, dungeon_id, release=release, locale=locale)
            
        api_data = client.get(url, params=params)

        if not dungeon_id:
            self.dungeons = api_data['dungeons']
        else:

            self.object_id = api_data['id']
            self.name = api_data['name']
            self.map = api_data['map']
            self.zone_slug = api_data['zone']['slug']
            self.breakpoints = {chest['upgrade_level']: chest['qualifying_duration']
                                for chest in api_data['keystone_upgrades']}
            self.dungeon = api_data['dungeon']


class MythicKeystoneIndex:
    """Index of Mythic Keystones

    Args:
        region_tag (str): region desired for the request

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
        seasons (list): the seasons for mythic keystones
        dungeons (list): the dungeons for the mythic keystones
    """
    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, *, release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = mythic_keystone_index(region_tag, release=release, locale=locale)

        api_data = client.get(url, params=params)
        seasons = client.get(api_data['seasons']['href'])
        dungeons = client.get(api_data['dungeons']['href'])

        for season in seasons['seasons']:
            api_data = client.get(season['key']['href'])
            self.seasons.append(MythicKeystoneSeason(client, region_tag, api_data['id'], release=release,
                                                     locale=locale))

        for dungeon in dungeons['dungeons']:
            api_data = client.get(dungeon['key']['href'])
            self.dungeons.append(MythicKeystoneDungeon(client, region_tag, api_data['id'], release=release,
                                                       locale=locale))


class MythicKeystonePeriod:
    """Index of Mythic Keystone Periods

    Args:
        region_tag (str): region desired for the request

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
        periods (list): the list of the dungeons for mythic keystones
    """

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, period_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = mythic_keystone_period(region_tag, period_id, release=release, locale=locale)

        api_data = client.get(url, params=params)

        if not period_id:
            self.periods = api_data['periods']
        else:
            self.object_id = api_data['id']
            self.start = daapi_data['start_timestamp']
            self.end = api_data['end_timestamp']


class MythicKeystoneSeason:
    """Index of Mythic Keystone Season

    Args:
        region_tag (str): region desired for the request

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
        seasons (list): the list of the seasons for mythic keystones
        current_season (dict): the
    """

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, season_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = mythic_keystone_season(region_tag, season_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        if not season_id:
            self.seasons = api_data['seasons']
            self.current_season = api_data['current_season']
        else:
            self.season_id = api_data['id']
            self.start = datetime.utcfromtimestamp(api_data['start_timestamp'] / 1000)
            self.end = datetime.utcfromtimestamp(api_data['end_timestamp'] / 1000)
            self.periods = api_data['periods']


class MythicKeystoneLeaderBoard:
    """Index of the Mythic Keystone Leaderboards

    Args:
        region_tag (str): region desired for the request

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
        leaderboards (list): the list of the quest areas

    """

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, connected_realm_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = mythic_keystone_leaderboard(region_tag, connected_realm_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        if not connected_realm_id:
            self.leaderboards = api_data['leaderboards']

        else:
            self.map = api_data['map']
            self.period = int(api_data['period'])
            self.period_start_timestamp = int(api_data['period_start_timestamp'])
            self.period_end_timestamp = int(api_data['period_end_timestamp'])
            self.connected_realm = api_data['connected_realm']['href']
            self.leading_groups = api_data['leading_groups']
