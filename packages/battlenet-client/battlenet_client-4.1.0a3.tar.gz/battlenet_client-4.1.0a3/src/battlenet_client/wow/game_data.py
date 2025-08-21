"""Defines the functions that handle the community APIs for World of Warcraft

Functions:
    achievement(region_tag, achievement_id, release, locale)
    achievement_category(region_tag, category_id, release, locale)
    achievement_media(region_tag, achievement_id, release, locale)
    auction(region_tag, connected_realm_id, auction_house_id, release, locale)
    azerite_essence(region_tag, essence_id, release, locale)
    azerite_essence_media(region_tag, essence_id, release, locale)
    azerite_essence_search(region_tag, field_values, release, locale)
    conduit(region_tag, conduit_id, release, locale)
    connected_realm(region_tag, connected_realm_id, release, locale)
    connected_realm_search(region_tag, field_values, release, locale)
    covenant(region_tag, covenant_id, release, locale)
    covenant_media(region_tag, covenant_id, release, locale)
    creature(region_tag, creature_id, release, locale)
    creature_display_media(region_tag, display_id, release, locale)
    creature_family(region_tag, family_id, release, locale)
    creature_family_media(region_tag, family_id, release, locale)
    creature_search(region_tag, field_values, release, locale)
    creature_type(region_tag, type_id, release, locale)
    guild_crest_components_index(region_tag, release, locale)
    guild_crest_media(region_tag, emblem_id, release, locale)
    heirloom(region_tag, heirloom_id, release, locale)
    item(region_tag, item_id, release, locale)
    item_class(region_tag, class_id, release, locale)
    item_media(region_tag, item_id, release, locale)
    item_search(region_tag, field_values, release, locale)
    item_set(region_tag, set_id, release, locale)
    item_subclass(region_tag, class_id, subclass_id, release, locale)
    journal_encounter(region_tag, encounter_id, release, locale)
    journal_encounter_search(region_tag, field_values, release, locale)
    journal_expansion(region_tag, expansion_id, release, locale)
    journal_instance(region_tag, instance_id, release, locale)
    journal_instance_media(region_tag, instance_id, release, locale)
    media_search(region_tag, field_values, release, locale)
    modified_crafting(region_tag, release, locale)
    modified_crafting_category(region_tag, category_id, release, locale)
    modified_crafting_reagent_slot_type(region_tag, slot_type_id, release, locale)
    mount(region_tag, mount_id, release, locale)
    mount_search(region_tag, field_values, release, locale)
    mythic_keystone_affix(region_tag, affix_id, release, locale)
    mythic_keystone_affix_media(region_tag, affix_id, release, locale)
    mythic_keystone_dungeon(region_tag, dungeon_id, release, locale)
    mythic_keystone_index(region_tag, release, locale)
    mythic_keystone_leaderboard(region_tag, connected_realm_id, dungeon_id, period_id, release, locale)
    mythic_keystone_period(region_tag, period_id, release, locale)
    mythic_keystone_season(region_tag, season_id, release, locale)
    mythic_raid_leaderboard(region_tag, raid_name, faction, release, locale)
    pet(region_tag, pet_id, release, locale)
    pet_ability(region_tag, pet_ability_id, release, locale)
    pet_ability_media(region_tag, ability_id, release, locale)
    pet_media(region_tag, pet_id, release, locale)
    playable_class(region_tag, class_id, release, locale)
    playable_class_media(region_tag, class_id, release, locale)
    playable_race(region_tag, race_id, release, locale)
    playable_spec(region_tag, spec_id, release, locale)
    playable_spec_media(region_tag, spec_id, release, locale)
    power_type(region_tag, power_id, release, locale)
    profession(region_tag, profession_id, release, locale)
    profession_media(region_tag, profession_id, release, locale)
    profession_skill_tier(region_tag, profession_id, skill_tier_id, release, locale)
    pvp_leader_board(region_tag, season_id, pvp_bracket, release, locale)
    pvp_rewards_index(region_tag, season_id, release, locale)
    pvp_season(region_tag, season_id, release, locale)
    pvp_talent(region_tag, pvp_talent_id, release, locale)
    pvp_talent_slots(region_tag, class_id, release, locale)
    pvp_tier(region_tag, tier_id, release, locale)
    pvp_tier_media(region_tag, tier_id, release, locale)
    quest(region_tag, quest_id, release, locale)
    quest_area(region_tag, quest_area_id, release, locale)
    quest_category(region_tag, quest_category_id, release, locale)
    quest_type(region_tag, quest_type_id, release, locale)
    realm(region_tag, realm_slug, release, locale)
    realm_search(region_tag, field_values, release, locale)
    recipe(region_tag, recipe_id, release, locale)
    recipe_media(region_tag, recipe_id, release, locale)
    region(region_tag, region_req, release, locale)
    reputation_faction(region_tag, faction_id, release, locale)
    reputation_tier(region_tag, tier_id, release, locale)
    soulbind(region_tag, soulbind_id, release, locale)
    spell(region_tag, spell_id, release, locale)
    spell_media(region_tag, spell_id, release, locale)
    spell_search(region_tag, field_values, release, locale, )
    talent(region_tag, talent_id, release, locale)
    tech_talent(region_tag, talent_id, release, locale)
    tech_talent_media(region_tag, talent_id, release, locale)
    tech_talent_tree(region_tag, tree_id, release, locale)
    toy(region_tag, toy_id, release, locale)
    title(region_tag, title_id, release, locale)
    wow_token_index(region_tag, release, locale)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from typing import Optional, Any, Dict, Union, Tuple

from battlenet_client.wow import utils as wow_utils
from battlenet_client import utils
from battlenet_client import exceptions
from battlenet_client.decorators import verify_region

__version__ = '3.0.0'
__author__ = 'David \'Gahd\' Couples'


@verify_region
def achievement_category(region_tag: str, category_id: Optional[Union[int, str]] = "index", *,
                         release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of achievement categories, or an achievement category by ID

    Args:
        region_tag (str): region_tag abbreviation
        category_id (int, optional): the achievement's category ID or None (default).
            None will retrieve the entire list of achievement categories
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/achievement-category/{category_id}"

    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def achievement(region_tag: str, achievement_id: Optional[Union[int, str]] = "index", *,
                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of achievements, or an achievement by ID

    Args:
        region_tag (str): region_tag abbreviation
        achievement_id (int, optional): the achievement ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/achievement/{achievement_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    return uri, params


@verify_region
def achievement_media(region_tag: str, achievement_id: int, *,
                      release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for an achievement by ID.

    Args:
        region_tag (str): region_tag abbreviation
        achievement_id (int): the achievement ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/achievement/{achievement_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def auction(region_tag: str, connected_realm_id: int, *, auction_house_id: Optional[int] = None,
            release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns all active auctions for a connected realm.

    See the Connected Realm API for information about retrieving a list of connected realm IDs.
    Auction house data updates at a set interval. The value was initially set at 1 hour;
    however, it might change over time without notice.

    Depending on the number of active auctions on the specified connected realm, the response
    from this endpoint may be rather large, sometimes exceeding 10 MB.

    See the Connected Realm WoWUtils.api for information about retrieving a list of
    connected realm IDs.

    Auction house data updates at a set interval. The value was initially set
    at 1 hour; however, it might change over time without notice.

    Depending on the number of active auctions on the specified connected realm,
    the response from this game_data may be rather large, sometimes exceeding
    10 MB.

    Args:
        region_tag (str): region_tag abbreviation
        connected_realm_id (int): the id of the connected realm
        auction_house_id (int, optional): the ID of the auction house
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        exceptions.BNetReleaseError: when an AH ID is used for the retail

    Notes:
        Auction house functionality is not available for WoW 1.x (Vanilla Classic)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/connected-realm/{connected_realm_id}/"

    if release == "retail" and auction_house_id is None:
        uri += "auctions"

    if release != "retail" and not auction_house_id:
        uri += "auctions/index"

    if release != "retail" and auction_house_id:
        uri += f"auctions/{auction_house_id}"

    if release == "retail" and auction_house_id:
        raise exceptions.BNetReleaseError("Auction House ID not available for retail")

    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def azerite_essence(region_tag: str, essence_id: Optional[Union[int, str]] = "index", *,
                    release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of azerite essences, or an azerite essence by ID.

    Args:
        region_tag (str): region_tag abbreviation
        essence_id (int, optional): the Azerite essence ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/azerite-essence/{essence_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def azerite_essence_search(region_tag: str, field_values: Dict[str, Any], *,
                           release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Performs a search of azerite essences. For more detail see the search guide at:
    https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        field_values (dict): search criteria, as key/value pairs
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """

    uri = f"{utils.api_host(region_tag)}/data/wow/search/azerite-essence"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    params.update(field_values)

    return uri, params


@verify_region
def azerite_essence_media(region_tag: str, essence_id: int, *,
                          release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for an azerite essence by ID.

    Args:
        region_tag (str): region_tag abbreviation
        essence_id (int): the azerite essence ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = (
        f"{utils.api_host(region_tag)}/data/wow/media/azerite-essence/{essence_id}"
    )
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def connected_realm(region_tag: str, connected_realm_id: Optional[Union[int, str]] = "index", *,
                    release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of connected realms, or a connected realm by ID.

    A connected realm is a collection of realms operating as one larger realm

    Args:
        region_tag (str): region_tag abbreviation
        connected_realm_id (int, optional): the ID of the connected realm
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/connected-realm/{connected_realm_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def connected_realm_search(region_tag: str, field_values: Dict[str, Any], *,
                           release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Performs a search of connected realms. For more detail see the search guide:
    https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        field_values (dict): field/value pairs
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/search/connected-realm"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }
    params.update(field_values)
    return uri, params


# noinspection DuplicatedCode
@verify_region
def covenant(region_tag: str, covenant_id: Optional[Union[int, str]] = "index", *,
             release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of covenants, or a covenant by ID.

    Args:
        region_tag (str): region_tag abbreviation
        covenant_id (int, optional): the ID of the covenant or the default 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/covenant/{covenant_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def covenant_media(region_tag: str, covenant_id: int, *,
                   release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a covenant by ID.

    Args:
        region_tag (str): region_tag abbreviation
        covenant_id (int, optional): the covenant ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/covenant/{covenant_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def soulbind(region_tag: str, soulbind_id: Optional[Union[int, str]] = "index", *,
             release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of soulbinds, or a soulbind by ID.

    Args:
        region_tag (str): region_tag abbreviation
        soulbind_id (int, optional): the ID of the soulbind or the word of 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/covenant/soulbind/{soulbind_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def conduit(region_tag: str, conduit_id: Optional[Union[int, str]] = "index", *,
            release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of conduits, or a conduit by ID.

    Args:
        region_tag (str): region_tag abbreviation
        conduit_id (int, optional): the ID of the conduit or the word of 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/covenant/conduit/{conduit_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def creature_family(region_tag: str, family_id: Optional[Union[int, str]] = "index", *,
                    release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of creature families, or a creature family by ID.

    Args:
        region_tag (str): region_tag abbreviation
        family_id (int, optional): the creature family ID or the default 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/creature-family/{family_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def creature_type(region_tag: str, type_id: Optional[Union[int, str]] = "index", *,
                  release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of creature types, or a creature type by ID.

    Args:
        region_tag (str): region_tag abbreviation
        type_id (int, optional): the creature type ID or the default 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/creature-type/{type_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def creature(region_tag: str, creature_id: int, *,
             release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns a creature by ID.

    Args:
        region_tag (str): region_tag abbreviation
        creature_id (int, optional): the creature ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/creature/{creature_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def creature_search(region_tag: str, field_values: Dict[str, Any], *,
                    release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Performs a search of creatures. For more detail see the search guide
     https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        field_values (dict): matching criteria in key/value pairs
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/search/creature"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    params.update(field_values)
    return uri, params


@verify_region
def creature_display_media(region_tag: str, display_id: int, *,
                           release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a creature display by ID.

    Args:
        region_tag (str): region_tag abbreviation
        display_id (int, optional): the creature display ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = (
        f"{utils.api_host(region_tag)}/data/wow/media/creature-display/{display_id}"
    )
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def creature_family_media(region_tag: str, family_id: int, *,
                          release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a creature family by ID.

    Args:
        region_tag (str): region_tag abbreviation
        family_id (int, optional): the creature family ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = (
        f"{utils.api_host(region_tag)}/data/wow/media/creature-family/{family_id}"
    )
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def guild_crest_components_index(region_tag: str, release: Optional[str] = "retail", *,
                                 locale: Optional[str] = 'enus') -> Tuple:
    """Returns an index of guild crest media.

    Args:
        region_tag (str): region_tag abbreviation
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/guild-crest/index"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def guild_crest_media(region_tag: str, category: str, icon_id: int, *,
                      release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a guild crest border by ID.

    Args:
        region_tag (str): region_tag abbreviation
        category (str): either 'border' or 'emblem'
        icon_id (int): the border ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    if category and category not in ('border', 'emblem'):
        raise exceptions.BNetValueError("Improper category")

    uri = f"{utils.api_host(region_tag)}/data/wow/media/guild-crest/{category}/{icon_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def heirloom(region_tag: str, heirloom_id: Optional[Union[str, int]] = "index", *,
             release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:

    uri = f"{utils.api_host(region_tag)}/data/wow/heirloom/{heirloom_id}"

    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    return uri, params


@verify_region
def item_class(region_tag: str, class_id: Optional[Union[int, str]] = "index", *,
               release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of item classes, or an item class by ID.

    Args:
        region_tag (str): region_tag abbreviation
        class_id (int, optional): item class ID or the default 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/item-class/{class_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def item_set(region_tag: str, set_id: Optional[Union[int, str]] = "index", *,
             release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:

    """Returns an index of item sets, or an item set by ID.

    Args:
        region_tag (str): region_tag abbreviation
        set_id (int, optional): the item class ID or the default 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/item-set/{set_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def item_subclass(region_tag: str, class_id: int, subclass_id: int, *,
                  release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an item subclass by ID.

    Args:
        region_tag (str): region_tag abbreviation
        class_id (int): the item class ID
        subclass_id (int, optional): the item's subclass ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/item-class/{class_id}/item-subclass/{subclass_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def item(region_tag: str, item_id: int, *,
         release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an item by ID.

    Args:
        region_tag (str): region_tag abbreviation
        item_id (int, optional): the item class ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/item/{item_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def item_media(region_tag: str, item_id: int, *,
               release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an item by ID.

    Args:
        region_tag (str): region_tag abbreviation
        item_id (int): the creature family ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/item/{item_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def item_search(region_tag: str, field_values: Dict[str, Any], *,
                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Performs a search of items. For more detail see the search guide.
    https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        field_values (dict): search criteria as key/value pairs
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
         tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/search/item"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    #  adding locale and namespace key/values pairs to field_values to make a complete params list
    params.update(field_values)

    return uri, params


@verify_region
def item_appearance(region_tag: str, appearance_id: int, *, release: Optional[str] = None,
                    locale: Optional[str] = None) -> Tuple:
    """Returns an item appearance by ID.

    Args:
        region_tag (str): region_tag abbreviation
        appearance_id (int): the appearance ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
         tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/item-appearance/{appearance_id}"

    params = {
        locale: utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def item_appearance_search(region_tag: str, field_values: Dict[str, Any], *,
                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Performs a search of item appearances. For more detail see the search guide.
    https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        field_values (dict): search criteria as key/value pairs
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
         tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/search/item-appearance"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    #  adding locale and namespace key/values pairs to field_values to make a complete params list
    params.update(field_values)

    return uri, params


@verify_region
def item_appearance_set(region_tag: str, appearance_id: Optional[Union[int, str]] = "index", *,
                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of appearances, or an appearance by ID

    Args:
        region_tag (str): region_tag abbreviation
        appearance_id (int, optional): the appearance ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/item-appearance/{appearance_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    return uri, params


@verify_region
def item_appearance_slot(region_tag: str, slot_type: Optional[str] = "index", *,
                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of appearances, or an appearance by ID

    Args:
        region_tag (str): region_tag abbreviation
        slot_type: (str, optional): the appearance ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """

    if slot_type.upper() in ["HEAD", "NECK", "SHOULDER", "BODY", "CHEST", "WAIST", "LEGS", "FEET", "WRIST",
                             "HAND", "RING", "WEAPON", "SHIELD", "RANGED", "CLOAK", "TWOHWEAPON", "TABARD",
                             "ROBE", "WEAPONMAINHAND", "WEAPONOFFHAND", "HOLDABLE", "AMMO", "RANGEDRIGHT",
                             "PROFESSION_TOOL", "PROFESSION_GEAR", "EQUIPABLESPELL_WEAPON"]:
        uri = f"{utils.api_host(region_tag)}/data/wow/item-appearance/{slot_type.upper()}"
    else:
        uri = f"{utils.api_host(region_tag)}/data/wow/item-appearance/index"

    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    return uri, params


@verify_region
def journal_expansion(region_tag: str, expansion_id: Optional[Union[int, str]] = "index", *,
                      release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of journal expansions, or a journal expansion by ID.

    Args:
        region_tag (str): region_tag abbreviation
        expansion_id (int, optional): the encounter ID or 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/journal-expansion/{expansion_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def journal_encounter(region_tag: str, encounter_id: Optional[Union[int, str]] = 'index', *,
                      release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of journal encounters, or a journal encounter by ID.

    Notes:
        This replaced the Boss endpoint of the community REST API

    Args:
        region_tag (str): region_tag abbreviation
        encounter_id (int, optional): the encounter ID or 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/journal-encounter/{encounter_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def journal_encounter_search(region_tag: str, field_values: Dict[str, Any], *,
                             release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Performs a search of journal encounters.  For more detail see the Search Guide.
    https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        field_values (dict): search criteria, as key/value pairs
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/search/journal-encounter"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    params.update(field_values)
    return uri, params


@verify_region
def journal_instance(region_tag: str, instance_id: Optional[Union[int, str]] = "index", *,
                     release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of journal instances, or a journal instance.

    Args:
        region_tag (str): region_tag abbreviation
        instance_id (int, optional): the encounter ID or 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/journal-instance/{instance_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def journal_instance_media(region_tag: str, instance_id: int, *,
                           release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a journal instance by ID.

    Args:
        region_tag (str): region_tag abbreviation
        instance_id (int): the creature family ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/journal-instance/{instance_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def media_search(region_tag: str, category: str,  field_values: Dict[str, Any], *,
                 release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Performs a search of all types of media documents. For more detail see the Search Guide.
    https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        category (str): media category
        field_values (dict): fields and values for the search criteria
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/search/media"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    #  adding locale and namespace key/values pairs to field_values to make a complete params list
    params.update({'tags': category})
    params.update(field_values)

    return uri, params


@verify_region
def modified_crafting(region_tag: str, release: Optional[str] = "retail", *,
                      locale: Optional[str] = 'enus') -> Tuple:
    """Returns the parent index for Modified Crafting.

    Args:
        region_tag (str): region_tag abbreviation
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/modified-crafting"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def modified_crafting_category(region_tag: str, category_id: Optional[Union[int, str]] = "index", *,
                               release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns the index of Modified Crafting categories, or a Modified Crafting category by ID.

    Args:
        region_tag (str): region_tag abbreviation
        category_id (int, optional): the encounter ID or 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/modified-crafting/category/{category_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def modified_crafting_reagent_slot_type(region_tag: str, slot_type_id: Optional[Union[int, str]] = 'index', *,
                                        release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns the index of Modified Crafting reagent slot types, or a Modified Crafting reagent slot type by ID

    Args:
        region_tag (str): region_tag abbreviation
        slot_type_id (int, optional): the encounter ID or 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/modified-crafting/reagent-slot-type/{slot_type_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def mount(region_tag: str, mount_id: Optional[Union[int, str]] = "index", *,
          release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of mounts, or a mount by ID.

    Args:
        region_tag (str): region_tag abbreviation
        mount_id (int, optional): the mount ID or 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/mount/{mount_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def mount_search(region_tag: str, field_values: Dict[str, Any], *,
                 release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Performs a search of mounts. For more detail see the Search Guide.
    https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        field_values (dict): fields and values for the search criteria
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/search/mount"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    #  adding locale and namespace key/values pairs to field_values to make a complete params list
    params.update(field_values)
    return uri, params


@verify_region
def mythic_keystone_affix(region_tag: str, affix_id: Optional[Union[int, str]] = "index", *,
                          release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of mythic keystone affixes. or a mythic keystone affix by ID

    Args:
        region_tag (str): region_tag abbreviation
        affix_id (int, optional): the affix's ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/keystone-affix/{affix_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def mythic_keystone_affix_media(region_tag: str, affix_id: int, *,
                                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a mythic keystone affix by ID.

    Args:
        region_tag (str): region_tag abbreviation
        affix_id (int): the affix's ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/keystone-affix/{affix_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def mythic_keystone_dungeon(region_tag: str, dungeon_id: Optional[Union[int, str]] = "index", *,
                            release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of Mythic Keystone dungeons, or a Mythic Keystone dungeon by ID.

    Args:
        region_tag (str): region_tag abbreviation
        dungeon_id (int, optional): the dungeon's ID or 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/mythic-keystone/dungeon/{dungeon_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def mythic_keystone_index(region_tag: str, *,
                          release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of links to other documents related to Mythic Keystone dungeons.

    Args:
        region_tag (str): region_tag abbreviation
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/mythic-keystone/index"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def mythic_keystone_period(region_tag: str, period_id: Optional[Union[int, str]] = "index", *,
                           release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of Mythic Keystone periods, or a Mythic Keystone period by ID.

    Args:
        region_tag (str): region_tag abbreviation
        period_id (int, optional): the keystone's period ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = (
        f"{utils.api_host(region_tag)}/data/wow/mythic-keystone/period/{period_id}"
    )
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def mythic_keystone_season(region_tag: str, season_id: Optional[Union[int, str]] = "index", *,
                           release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of Mythic Keystone seasons, or a Mythic Keystone season by ID.

    Args:
        region_tag (str): region_tag abbreviation
        season_id (int, optional): the keystone's season ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = (
        f"{utils.api_host(region_tag)}/data/wow/mythic-keystone/season/{season_id}"
    )
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def mythic_keystone_leaderboard(region_tag: str, connected_realm_id: int, dungeon_id: Optional[Union[int, str]] = None,
                                period_id: Optional[Union[int, str]] = None, *,
                                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of Mythic Keystone Leaderboard dungeon instances for a connected realm,
    or a weekly Mythic Keystone Leaderboard by period.

    Args:
        release (str): release of the game (ie classic1x, classic, retail)
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        connected_realm_id (int): the connected realm's id
        dungeon_id (int, optional): the particular dungeon's ID or the word 'index'
        period_id (int, optional): the particular period to search or None when looking for the index

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/connected-realm/{connected_realm_id}/mythic-leaderboard/"

    if dungeon_id and period_id:
        uri += f"{dungeon_id}/period/{period_id}"
    else:
        uri += "index"

    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def mythic_raid_leaderboard(region_tag: str, raid_name: str, faction: str, *,
                            release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns the leaderboard for a given raid and faction.

    Args:
        region_tag (str): region_tag abbreviation
        raid_name (str): name of the raid
        faction (str): horde or alliance, defaults to alliance
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/leaderboard/hall-of-fame/"
    uri += f"{utils.slugify(raid_name)}/{utils.slugify(faction)}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def pet(region_tag: str, pet_id: Optional[Union[int, str]] = "index", *,
        release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of battle pets, or a battle pet by ID.

    Args:
        release (str): release of the game (ie classic1x, classic, retail)
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        pet_id (int, optional): the pet ID or the word 'index'

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/pet/{pet_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def pet_media(region_tag: str, pet_id: int, *,
              release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a battle pet by ID.

    Args:
        region_tag (str): region_tag abbreviation
        pet_id (int): the azerite pet ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/pet/{pet_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def pet_ability(region_tag: str, pet_ability_id: Optional[Union[int, str]] = "index", *,
                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of pet abilities, or a pet ability by ID.

    Args:
        region_tag (str): region_tag abbreviation
        pet_ability_id (int, optional): the pet ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/pet-ability/{pet_ability_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def pet_ability_media(region_tag: str, ability_id: int, *,
                      release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a pet ability by ID.

    Args:
        region_tag (str): region_tag abbreviation
        ability_id (int): the azerite ability ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/pet-ability/{ability_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def playable_class(region_tag: str, class_id: Optional[Union[int, str]] = "index", *,
                   release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of playable classes, or a playable class by ID.

    Args:
        region_tag (str): region_tag abbreviation
        class_id (int, optional): the class ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/playable-class/{class_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def playable_class_media(region_tag: str, class_id: int, *,
                         release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a playable class by ID.

    Args:
        region_tag (str): region_tag abbreviation
        class_id (int ): class id
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/playable-class/{class_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def pvp_talent_slots(region_tag: str, class_id: int, *,
                     release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns the PvP talent slots for a playable class by ID.

    Args:
        region_tag (str): region_tag abbreviation
        class_id (int): class id
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/playable-class/{class_id}/pvp-talent-slots"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def playable_race(region_tag: str, race_id: Optional[Union[int, str]] = "index", *,
                  release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of playable races, or a playable race by ID.

    Args:
        region_tag (str): region_tag abbreviation
        race_id (int, optional): the playable race's ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/playable-race/{race_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def playable_spec(region_tag: str, spec_id: Optional[Union[int, str]] = "index", *,
                  release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:

    """Returns an index of playable specializations, or a playable specialization by ID.

    Args:
        region_tag (str): region_tag abbreviation
        spec_id (int, optional): the playable specialization's ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/playable-specialization/{spec_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def playable_spec_media(region_tag: str, spec_id: int, *,
                        release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a playable specialization by ID.

    Args:
        region_tag (str): region_tag abbreviation
        spec_id (int): specialization id
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/playable-specialization/{spec_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def power_type(region_tag: str, power_id: Optional[Union[int, str]] = "index", *,
               release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of power types, or a power type by ID.

    Args:
        region_tag (str): region_tag abbreviation
        power_id (int, optional): the power type's ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/power-type/{power_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def profession(region_tag: str, profession_id: Optional[Union[int, str]] = "index", *,
               release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """RReturns an index of professions, or a profession by ID.

    Args:
        region_tag (str): region_tag abbreviation
        profession_id (int, optional): the profession ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/profession/{profession_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def profession_media(region_tag: str, profession_id: int, *,
                     release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a profession by ID.

    Args:
        region_tag (str): region_tag abbreviation
        profession_id (str):  profession ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/profession/{profession_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def profession_skill_tier(region_tag: str, profession_id: int, skill_tier_id: int, *,
                          release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns a skill tier for a profession by ID.

    Args:
        region_tag (str): region_tag abbreviation
        profession_id (int): the profession ID
        skill_tier_id (int): the skill tier ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/profession/{profession_id}/skill-tier/{skill_tier_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def recipe(region_tag: str, recipe_id: int, *,
           release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns a recipe by ID.

    Args:
        region_tag (str): region_tag abbreviation
        recipe_id (str): the recipe ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/recipe/{recipe_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def recipe_media(region_tag: str, recipe_id: int, *,
                 release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a recipe by ID.

    Args:
        region_tag (str): region_tag abbreviation
        recipe_id (int): the profession ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/recipe/{recipe_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def pvp_season(region_tag: str, season_id: Optional[Union[int, str]] = "index", *,
               release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of PvP seasons, or a PvP season by ID.

    Args:
        region_tag (str): region_tag abbreviation
        season_id (int, optional): the power type's ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/pvp-season/{season_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def pvp_regions(region_tag: str, *, release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of PvP regions

    Args:
        region_tag (str): region_tag abbreviation
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/pvp-region/index"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def pvp_regional_season(region_tag: str, pvp_region_id: int, pvp_season_id: Optional[Union[int, str]] = 'index', *,
                        release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of PvP regions

    Args:
        region_tag (str): region_tag abbreviation
        pvp_region_id (int): the regional PVP ID (use pvp_regions)
        pvp_season_id (int): the pvp season ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/pvp-region/{pvp_region_id}/pvp-season/{pvp_season_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def pvp_leaderboard(region_tag: str, pvp_region_id: int, season_id: int, pvp_bracket: Optional[str] = "index", *,
                    release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of PvP leaderboards for a PvP season, or
    the PvP leaderboard of a specific PvP bracket for a PvP season.

    Args:
        region_tag (str): region_tag abbreviation
        pvp_region_id (int): the regional PVP ID (use pvp_regions)
        season_id (int): pvp season's ID
        pvp_bracket (int, optional): the PvP bracket to view ('2v2', '3v3', '5v5', 'rbg') or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/pvp-region/{pvp_region_id}/pvp-season/"
    uri += f"{season_id}/pvp-leaderboard/{pvp_bracket}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def pvp_rewards_index(region_tag: str, pvp_region_id: int, season_id: int, *,
                      release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of PvP rewards for a PvP season.

    Args:
        region_tag (str): region_tag abbreviation
        pvp_region_id (int): the regional PVP ID (use pvp_regions)
        season_id (int): the season ID for the rewards or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/pvp-region/{pvp_region_id}/pvp-season/{season_id}/pvp-reward/index"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def pvp_tier(region_tag: str, tier_id: Optional[Union[int, str]] = "index", *,
             release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of PvP tiers, or a PvP tier by ID.

    Args:
        region_tag (str): region_tag abbreviation
        tier_id (int, optional): the pvp tier ID or the default 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/pvp-tier/{tier_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def pvp_tier_media(region_tag: str, tier_id: int, *,
                   release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a PvP tier by ID.

    Args:
        region_tag (str): region_tag abbreviation
        tier_id (int): pvp tier id
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/pvp-tier/{tier_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def quest(region_tag: str, quest_id: Optional[Union[int, str]] = "index", *,
          release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns the parent index for quests, or a quest by ID.

    Args:
        region_tag (str): region_tag abbreviation
        quest_id (int, optional): the quest ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/quest/{quest_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def quest_category(region_tag: str, quest_category_id: Optional[Union[int, str]] = "index", *,
                   release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of quest categories (such as quests for a specific class, profession, or storyline),
    or a quest category by ID.

    Args:
        region_tag (str): region_tag abbreviation
        quest_category_id (int, optional): the quest category ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = (
        f"{utils.api_host(region_tag)}/data/wow/quest/category/{quest_category_id}"
    )
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def quest_area(region_tag: str, quest_area_id: Optional[Union[int, str]] = "index", *,
               release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of quest areas, or a quest area by ID.

    Args:
        region_tag (str): region_tag abbreviation
        quest_area_id (int, optional): the quest area ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/quest/area/{quest_area_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def quest_type(region_tag: str, quest_type_id: Optional[Union[int, str]] = "index", *,
               release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of quest types (such as PvP quests, raid quests, or account quests),
    or a quest type by ID.

    Args:
        release (str): release of the game (ie classic1x, classic, retail)
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        quest_type_id (int, optional): the quest type ID or the word 'index'

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/quest/type/{quest_type_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def realm(region_tag: str, realm_slug: Optional[Union[str, int]] = "index", *,
          release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of realms, or a single realm by slug or ID.

    Args:
        region_tag (str): region_tag abbreviation
        realm_slug (str/int, optional): the pvp tier ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/realm/{utils.slugify(realm_slug)}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def realm_search(region_tag: str, field_values: Dict[str, Any], *,
                 release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:

    """Performs a search of realms. For more detail see the Search Guide.
    https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        field_values (dict): search criteria, as key/value pairs
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/search/realm"
    params = {
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }
    params.update(field_values)
    return uri, params


@verify_region
def region(region_tag: str, region_req: Optional[Union[str, int]] = "index", *,
           release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of regions, or a region by ID.

    Args:
        region_tag (str): region_tag abbreviation
        region_req (int, optional): the region_tag ID or the word 'index'
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/region/{region_req}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params


@verify_region
def reputation_faction(region_tag: str, faction_id: Optional[Union[int, str]] = "index", *,
                       release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:

    """Returns an index of reputation factions, or a single reputation faction by ID.

    Args:
        region_tag (str): region_tag abbreviation
        faction_id (int, optional): the slug or ID of the region_tag requested
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/reputation-faction/{faction_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def reputation_tier(region_tag: str, tier_id: Optional[Union[int, str]] = "index", *,
                    release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of reputation tiers, or a single set of reputation tiers by ID.

    Args:
        region_tag (str): region_tag abbreviation
        tier_id (int, optional): the slug or ID of the region_tag requested
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/reputation-tiers/{tier_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def spell(region_tag: str, spell_id: int, *, release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns a spell by ID.

    Args:
        region_tag (str): region_tag abbreviation
        spell_id (int): the slug or ID of the region_tag requested
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/spell/{spell_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def spell_media(region_tag: str, spell_id: int, *,
                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a spell by ID.

    Args:
        release (str): release of the game (ie classic1x, classic, retail)
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        spell_id (int): pvp tier id

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/spell/{spell_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def spell_search(region_tag: str, field_values: Dict[str, Any] = None, *,
                 release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Performs a search of spells. For more detail see the Search Guide.
    https://develop.battle.net/documentation/world-of-warcraft/guides/search

    Args:
        region_tag (str): region_tag abbreviation
        field_values (dict): search criteria, as key/value pairs
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/search/spell"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    #  adding locale and namespace key/values pairs to field_values to make a complete params list
    params.update(field_values)
    return uri, params


@verify_region
def talent_tree(region_tag: str, tree_id: Optional[int] = 'index', spec_id: Optional[int] = None,
                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns the URL and parameters requried by the talent tree API

    Args:
        region_tag (str): region_tag abbreviation
        tree_id (int, optional): the tree ID
        spec_id (int, optional): the specialization ID
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/talent-tree/{tree_id}"

    if spec_id:
        uri = f"{uri}/playable-specialization/{spec_id}"

    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def talent(region_tag: str, talent_id: Optional[Union[int, str]] = "index", *,
           release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of talents, or a talent by ID.

    Args:
        region_tag (str): region_tag abbreviation
        talent_id (int, optional): the slug or ID of the region_tag requested
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/talent/{talent_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def pvp_talent(region_tag: str, pvp_talent_id: Optional[Union[int, str]] = "index", *,
               release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:

    """Returns an index of PvP talents, or a PvP talent by ID.

    Args:
        region_tag (str): region_tag abbreviation
        pvp_talent_id (int, optional): the slug or ID of the region_tag requested
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/pvp-talent/{pvp_talent_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def tech_talent_tree(region_tag: str, tree_id: Optional[Union[int, str]] = "index", *,
                     release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of tech talent trees, or a tech talent tree by ID.

    Args:
        region_tag (str): region_tag abbreviation
        tree_id (int, optional): the slug or ID of the region_tag requested
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/tech-talent-tree/{tree_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def tech_talent(region_tag: str, talent_id: Optional[Union[int, str]] = "index", *,
                release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns an index of tech talents, or a tech talent by ID.

    Args:
        region_tag (str): region_tag abbreviation
        talent_id (int, optional): the slug or ID of the region_tag requested
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/tech-talent/{talent_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def tech_talent_media(region_tag: str, talent_id: int, *,
                      release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns media for a tech talent by ID.

    Args:
        region_tag (str): region_tag abbreviation
        talent_id (int): pvp tier id
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/media/tech-talent/{talent_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def title(region_tag: str, title_id: Optional[Union[int, str]] = "index", *,
          release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    # noinspection GrazieInspection
    """Returns an index of titles, or a title by ID.

        Args:
            region_tag (str): region_tag abbreviation
            title_id (int, optional): the slug or ID of the region_tag requested
            release (str): release of the game (ie classic1x, classic, retail)
            locale (str): which locale to use for the request

        Returns:
            tuple: The URL (str) and parameters (dict)
        """
    uri = f"{utils.api_host(region_tag)}/data/wow/title/{title_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }

    return uri, params


@verify_region
def toy(region_tag: str, toy_id: Optional[Union[str, int]] = "index", *,
        release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:

    uri = f"{utils.api_host(region_tag)}/data/wow/toy/{toy_id}"

    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "static", release)
    }
    return uri, params


@verify_region
def wow_token_index(region_tag: str, *,
                    release: Optional[str] = None, locale: Optional[str] = None) -> Tuple:
    """Returns the WoW Token index.

    Args:
        release (str): release of the game (ie classic1x, classic, retail)
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/token/index"
    params = {
        "locale": utils.localize(locale),
        "namespace": wow_utils.namespace(region_tag, "dynamic", release)
    }

    return uri, params
