"""Defines exceptions related to the Battle.net OAuth API wrappers

Disclaimer:
    All rights reserved, Blizzard is the intellectual property owner of Battle.net and any data
    retrieved from this API.
"""


class BNetError(Exception):
    """Base Error class for BattleNet Client"""

    pass


class BNetRegionNotFoundError(BNetError):
    """Error raised when an invalid region bnet is detected"""

    pass


class BNetClientError(BNetError):
    """Error raised if there is a mismatch with the client and API endpoints"""

    pass
