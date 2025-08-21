"""Defines the functions that handle the game data APIs for Hearthstone

Functions:
    card_search(region_tag, field_values, locale)
    card(region_tag, card_id, game_mode, locale)
    metadata(region_tag, meta_data, locale)
    card_back_search(region_tag, field_values, locale)
    card_back(region_tag, card_back_id, locale)
    card_deck(region_tag, field_values, locale)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""

from typing import Optional, Any, Dict

from .. import utils
from ..decorators import verify_region
from ..exceptions import BNetValueError


__version__ = '2.0.0'
__author__ = 'David \'Gahd\' Couples'


@verify_region
def card_search(
    region_tag: str,
    field_values: Dict[str, Any],
    locale: Optional[str] = None,
):
    """Returns an up-to-date list of all cards matching the search criteria.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        field_values (dict): search criteria, as key/value pairs
            For more information for the field names and options:
            https://develop.battle.net/documentation/hearthstone/game-data-apis

    Returns:
        dict: json decoded search results that match `field_values`

    """
    params = {"locale": utils.localize(locale)}

    if "gameMode" not in field_values.keys():
        params["gameMode"] = "constructed"

    uri = f"{utils.api_host(region_tag)}/hearthstone/cards"

    if field_values:
        params.update(field_values)

    return uri, params


@verify_region
def card(
    region_tag: str,
    card_id: str,
    *,
    game_mode: Optional[str] = "constructed",
    locale: Optional[str] = None,
):
    """Returns the card with an ID or slug that matches the one you specify.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        card_id (int, str): the ID or full slug of the card
        game_mode (str, optional): the game mode
            See for more information:
            https://develop.battle.net/documentation/hearthstone/guides/game-modes

    Returns:
        dict: json decoded data for the index/individual azerite essence(s)
    """
    uri = f"{utils.api_host(region_tag)}/hearthstone/cards/{card_id}"
    params = {"locale": utils.localize(locale), "gameMode": game_mode}

    return uri, params


@verify_region
def metadata(
    region_tag: str,
    *,
    meta_data: Optional[str] = None,
    locale: Optional[str] = None,
):
    """Returns information about the categorization of cards. Metadata
    includes the card set, set group (for example, Standard or Year of
    the Dragon), rarity, class, card type, minion type, and keywords, or
    information about just one type of metadata.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        meta_data (str, optional): what metadata to filter
            Please see below for more information
            https://develop.battle.net/documentation/hearthstone/guides/metadata
            valid options: `sets`, `setGroups`, `types`, `rarities`, `classes`,
            `minionTypes`, `keywords`

    Returns:
        dict: json decoded list of metadata or a specific set of metadata
    """
    categories = ('sets', 'setGroups', 'types', 'rarities', 'classes', 'minionTypes', 'keywords')

    if meta_data and meta_data not in categories:
        raise BNetValueError("Metadata category not valid")

    uri = f"{utils.api_host(region_tag)}/hearthstone/metadata"

    if meta_data:
        uri += f"/{meta_data}"

    params = {"locale": utils.localize(locale)}

    return uri, params


@verify_region
def card_back_search(
    region_tag: str,
    field_values: Dict[str, Any],
    locale: Optional[str] = None,
):
    """Returns an up-to-date list of all card backs matching the search criteria.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        field_values (dict): search criteria, as key/value pairs
            For more information for the field names and options:
            https://develop.battle.net/documentation/hearthstone/guides/card-backs

    Returns:
        dict: json decoded search results that match `field_values`
    """
    uri = f"{utils.api_host(region_tag)}/hearthstone/cardbacks"

    if 'textFilter' in field_values and not locale:
        raise BNetValueError('textFilter requires a locale')

    params = {"locale": utils.localize(locale)}

    if field_values:
        params.update(field_values)

    return uri, params


@verify_region
def card_back(
    region_tag: str, card_back_id: str, locale: Optional[str] = None
):
    """Returns a specific card back by using card back ID or slug.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        card_back_id (int, str): the ID or full slug of the card back

    Returns:
        dict: json decoded data for the card back identified by `card_back_id`
    """
    uri = f"{utils.api_host(region_tag)}/hearthstone/cardbacks/{utils.slugify(card_back_id)}"

    params = {"locale": utils.localize(locale)}

    return uri, params


@verify_region
def card_deck(
    region_tag: str,
    field_values: Dict[str, Any],
    locale: Optional[str] = None,
):
    """Finds a deck by list of cards, including the hero.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        field_values (dict): search criteria, as key/value pairs
            For more information for the field names and options:
            https://develop.battle.net/documentation/hearthstone/guides/decks

    Returns:
        dict: json decoded search results that match `field_values`
    """
    uri = f"{utils.api_host(region_tag)}/hearthstone/deck"

    params = {"locale": utils.localize(locale)}

    if field_values:
        params.update(field_values)

    return uri, params
