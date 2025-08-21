from battlenet_client.cache.cache import Cache
from battlenet_client.wow.base import WoWBase, WoWMedia
from battlenet_client.wow.game_data import pvp_season, pvp_leaderboard, pvp_rewards_index
from battlenet_client.wow.game_data import pvp_tier, pvp_tier_media

import json
from typing import Optional, Union
from requests_oauthlib import OAuth2Session
from oic import oic


class PvPSeason(WoWBase):
    pass


class PvPLeaderboard(WoWBase):
    pass


class PvPRewards(WoWBase):
    pass


class PvPTier(WoWBase):
    pass
