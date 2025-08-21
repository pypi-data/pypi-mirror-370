"""World of Warcraft Mounts and related index

Disclaimer:
All rights reserved, Blizzard is the intellectual property owner of WoW and WoW Classic
and any data pertaining thereto

Author:


David "Gahd" Couples <gahdania@gahd.io>
"""

from battlenet_client.wow.game_data import mount


class Mount:
    """Defines the Playable Race Index.

    Args:
        region_tag (str): region abbreviation for use with the APIs

    Keyword Args:
        release (str, optional): the release to use.
        locale (str, optional): the localization to use from the API, The default of None means all localizations
        scope (list of str, optional): the scope or scopes to use during the endpoints that require the
            Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal

    Attributes:
        locale (str): the localization
        mounts (list): the index of the mounts
    """
    def __init__(self, client: Union[OAuth2Session, OicClient],  region_tag: str, mount_id: Optional[str, int] = None, *,
                 release=None, locale=None):

        (url, params) = mount(region_tag, mount_id, release=release, locale=locale)

        api_data = client.get(url, params=parms)

        if not mount_id:
            self.mounts = api_data['mounts']

        else:
            self.mount_id = api_data['id']
            self.name = api_data['name']
            self.creature_displays = api_data['creature_displays']
            self.description = api_data['description']
            self.source = api_data['source']['name']
            self.faction = api_data['faction']['name']
            self.requirements = api_data['requirements']
