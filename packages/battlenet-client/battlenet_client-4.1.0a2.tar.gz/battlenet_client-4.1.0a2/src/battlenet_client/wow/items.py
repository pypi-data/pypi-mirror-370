"""World of Warcraft Azerite Essences, Item class, Item subclass, item sets, and related indices

Disclaimer:
All rights reserved, Blizzard is the intellectual property owner of WoW and WoW Classic
and any data pertaining thereto

Author:
David "Gahd" Couples <gahdania@gahd.io>
"""
from battlenet_client.wow.game_data import azerite_essence, item_class, item_set, item_subclass, item
from battlenet_client.wow.playables import PlayableSpecialization


class AzeriteEssence:
    """Index of Azerite Essences

    Args:
        client (object): OIDC/OAuth compliant client
        region_tag (str): region abbreviation for use with the APIs
        release (str, optional): the release to use.
        locale (str, optional): the localization to use from the API, The default of None means all localizations


    Attributes:
        locale (str): the localization
        azerite_essences (list of dict): the index of essences
        name (str): name of a single azerite essence
        essence_id (int): single essence ID
        allowed_specs (list):  the specializations that are able to use the azerite essence
        powers (list):  powers granted by the azerite essence
        media (str): URL to the media for the essence
    """

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, essence_id: Optional[int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = azerite_essence(region_tag, essence_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        if not essence_id:
            self.azerite_essences = api_data['azerite_essences']
        else:
            self.essence_id = api_data['id']
            self.name = api_data['name']
            self.allowed_specs = [PlayableSpecialization(client, region_tag, spec['id'], release=release, locale=locale)
                                  for spec in api_data['allowed_specializations']]
            self.powers = api_data['powers']
            self.media = api_data['media']['key']['href']


class ItemClass:
    """Index of Item Classes

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
        item_classes (list of dict): the index of item classes
    """

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, item_class_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = item_class(region_tag, item_class_id, release=release, locale=locale)
        client.get(url, params=params)

        if not item_class_id:
            self.item_classes = api_data['item_classes']
        else:
            self.item_class_id = api_data['id']
            self.name = api_data['name']
            self.subclasses = api_data['item_subclasses']


class ItemSet:
    """Index of Item Sets

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
        item_sets (list of dict): the index of item sets
    """

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, set_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = item_set(region_tag, set_id, release=release, locale=locale)
        api_data = client.get(url, params=params)

        if not set_id:
            self.item_sets = api_data['item_sets']
        else:
            self.object_id = api_data['id']
            self.name = api_data['name']
            self.items = api_data['items']


class ItemSubClass:
    """Index of the Item Subclasses.

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
        subclasses (list of dict): the index of races
    """

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, subclass_id: Optional[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = item_subclass(region_tag, subclass_id, release=release, locale=locale)

        api_data = client.get(url, params)

        if not subclass_id:
            self.subclasses = api_data['item_subclasses']
        else:
            self.class_id = api_data['class_id']
            self.subclass_id = api_data['subclass_id']
            self.name = api_data['display_name']
            self.hide = bool(api_data['hide_subclass_in_tooltips'])


class Item:
    """Playable Race

    Args:
        region_tag (str): region abbreviation for use with the APIs
        item_id (int): race ID

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
        id (int): the playable race's ID
        name (str): item's name
        quality (str): the quality level
        required_level (int): the minimum level to use the item
        item_class (dict): the item's class
        item_subclass (dict): the item's subclass
        inventory_type (str): item's inventory type
        purchase_price (dict): purchase price in gold, silver, and copper
        sell_price (dict): selling price in gold, silver, and copper
        max_count (int): the max number of the item allowed to owned by a character
        is_equippable (bool): can the item be equipped
        is_stackable (bool): can the item be stacked
        media (str): URL of the media
    """

    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, item_id: Union[str, int] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None):

        (url, params) = item(region_tag, item_id, release=release, locale=locale)
        
        api_data = client.get(url, params=params)

        self.object_id = api_data['id']
        self.name = api_data['name']
        self.quality = api_data['quality']['name']
        self.level = api_data['level']
        self.required_level = api_data['required_level']
        self.item_class = api_data['item_class']
        self.item_subclass = api_data['item_subclass']
        self.inventory_type = api_data['inventory_type']['name']
        self.purchase_price = self._client.currency_convertor(api_data['purchase_price'])
        self.sell_price = self._client.currency_convertor(api_data['sell_price'])
        self.max_count = api_data['max_count']
        self.is_equippable = bool(api_data['is_equippable'])
        self.is_stackable = bool(api_data['is_stackable'])
        self.media = api_data['media']['key']['href']
