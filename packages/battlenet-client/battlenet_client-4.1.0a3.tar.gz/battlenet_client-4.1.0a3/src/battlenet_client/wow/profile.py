"""This module contains the classes for accessing profile related APIs

Functions:
    account_collections(region_tag, category, release, locale)
    account_profile_summary(region_tag, release, locale)
    achievement_statistics(region_tag, realm_name, character_name, release, locale)
    achievement_summary(region_tag, realm_name, character_name, release, locale)
    appearance_summary(region_tag, realm_name, character_name, release, locale)
    collections(region_tag, realm_name, character_name, category, release, locale)
    encounters(region_tag, realm_name, character_name, category, release, locale)
    equipment_summary(region_tag, realm_name, character_name, release, locale)
    guild(region_tag, realm_name, guild_name, category, release, locale)
    hunter_pets_summary(region_tag, realm_name, character_name, release, locale)
    media_summary(region_tag, realm_name, character_name, release, locale)
    mythic_keystone(region_tag, realm_name, character_name, season_id, release, locale)
    professions_summary(region_tag, realm_name, character_name, release, locale)
    profile(region_tag, realm_name, character_name, status, release, locale)
    protected_character_profile_summary(region_tag, realm_id, character_id, release, locale)
    pvp(region_tag, realm_name, character_name, pvp_bracket, release, locale)
    quests(region_tag, realm_name, character_name, completed, release, locale)
    reputations_summary(region_tag, realm_name, character_name, release, locale)
    soulbinds(region_tag, realm_name, character_name, release, locale)
    specializations_summary(region_tag, realm_name, character_name, release, locale)
    statistics_summary(region_tag, realm_name, character_name, release, locale)
    title_summary(region_tag, realm_name, character_name, release, locale)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from typing import Optional
from urllib.parse import quote as urlquote

from .utils import namespace
from .. import utils
from ..decorators import verify_region
from ..exceptions import BNetValueError


@verify_region
def account_profile_summary(
    region_tag: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a profile summary for an account.

    Because this endpoint provides data about the current logged-in user's World of Warcraft account,
    it requires an access token with the 'wow.profile' scope acquired via the Authorization Code Flow.
    https://develop.battle.net/documentation/guides/using-oauth/authorization-code-flow

    Args:
        region_tag (str): region_tag abbreviation
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/user/wow"
    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }

    return uri, params


@verify_region
def protected_character_profile_summary(
    region_tag: str,
    realm_id: int,
    character_id: int,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a protected profile summary for a character.

    Because this endpoint provides data about the current logged-in user's World of Warcraft account,
    it requires an access token with the 'wow.profile' scope acquired via the Authorization Code Flow.
    https://develop.battle.net/documentation/guides/using-oauth/authorization-code-flow

    Args:
        region_tag (str): region_tag abbreviation
        realm_id (int): the ID for the character's realm
        character_id (int): the ID of character
        release (str): release of the game (ie classi`c1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
            profile summary
    """
    uri = f"{utils.api_host(region_tag)}/profile/user/wow/protected-character/{realm_id}-{character_id}"
    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def account_collections(
    region_tag: str,
    *,
    category: Optional[str] = None,
    release: Optional[str] = "retail",
    locale: Optional[str] = None,
):
    """Returns an index of collection types for an account.

    Because this endpoint provides data about the current logged-in user's World of Warcraft account,
    it requires an access token with the 'wow.profile' scope acquired via the Authorization Code Flow.
    https://develop.battle.net/documentation/guides/using-oauth/authorization-code-flow

    Args:
        region_tag (str): region_tag abbreviation
        category (str): 'pets' to retrieve the pet collections, and
            'mounts' to retrieve the mount collection of the account or
            None for both pets and mounts
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    if category and category.lower() not in ('pets', 'mounts', 'toys', 'heirlooms'):
        raise BNetValueError('Invalid Category:  \'pets\' or \'mounts\'')

    uri = f"{utils.api_host(region_tag)}/profile/user/wow/collections"
    if category is not None:
        uri += f"/{category}"
    params = {

        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def achievement_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    statistics: Optional[bool] = False,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a summary of the achievements a character has completed.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        statistics (bool): Boolean to determine to display the statistics or not
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/achievements"

    if statistics:
        uri += '/statistics'

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def appearance_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a summary of a character's appearance settings.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/appearance"
    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def collections(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    category: Optional[str] = None,
    release: Optional[str] = "retail",
    locale: Optional[str] = None,
):
    """Returns an index of collection types for a character, a summary of the mounts
    a character has obtained, or a summary of the battle pets a character has obtained.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        category (str): category to retrieve. options are pets or mounts, or None (default).  None will
            provide both
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    if category and category not in ('pets', 'mounts'):
        raise BNetValueError("Category invalid: options are 'pets', 'mounts'")

    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += (
        f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/collections"
    )

    if category:
        if category.lower() not in ("pets", "mounts"):
            raise ValueError("Category needs to pets or mounts")
        uri += f"/{utils.slugify(category)}"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def encounters(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    category: Optional[str] = None,
    release: Optional[str] = "retail",
    locale: Optional[str] = None,
):
    """Returns a summary of all of a character's encounters, just dungeon encounters,
    or just raid encounters

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        category (str): category to retrieve.  options are 'dungeons',
            'raids', or None (default).  None will access both dungeons and raids
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/encounters"

    if category:
        if category.lower() not in ("dungeons", "raids"):
            raise ValueError("Available Categories: None, dungeons and raids")
        uri += f"/{utils.slugify(category)}"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def equipment_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a summary of the items equipped by a character.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/equipment"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def hunter_pets_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """If the character is a hunter, returns a summary of the character's hunter pets.
    Otherwise, returns an HTTP 404 Not Found error.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += (
        f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/hunter-pets"
    )

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def media_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a summary of the media assets available for a character (such as an avatar render).

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/character-media"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def mythic_keystone(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    season_id: Optional[int] = None,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns the Mythic Keystone profile index for a character,
    or the Mythic Keystone season details for a character.

    Returns a 404 Not Found for characters that have not yet completed
    a Mythic Keystone dungeon for the specified season.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        season_id (int or None): season id or None (default).  None
            accesses the list of seasons for the current expansion
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/mythic-keystone-profile"

    if season_id:
        uri += f"/season/{season_id}"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def professions_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a summary of professions for a character.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += (
        f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/professions"
    )

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def profile(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    status: bool = False,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a profile summary for a character, or the status and a unique ID for a character.

    A should delete information about a character from their application if
    any of the following conditions occur:

        1) an HTTP 404 Not Found error is returned
        2) the is_valid value is false
        3) the returned character ID doesn't match the previously recorded
            value for the character

    The following example illustrates how to use this endpoint:
        1) A requests and stores information about a character, including
        its unique character ID and the timestamp of the request.
        2) After 30 days, the makes a request to the status endpoint to
        verify if the character information is still valid.
        3) If character cannot be found, is not valid, or the characters IDs do
        not match, the removes the information from their application.
        4) If the character is valid and the character IDs match, the retains
        the data for another 30 days.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        status (bool): flag to request a profile summary (False default) or status (True)
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{urlquote(character_name.lower())}"

    if status:
        uri += "/status"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def pvp(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    pvp_bracket: Optional[str] = None,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns the PvP bracket statistics for a character, or a PvP summary for a character.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        pvp_bracket (str or None): '2v2', '3v3', 'rbg', None (default).
            None returns a summary of pvp activity
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    if pvp_bracket and pvp_bracket not in ('2v2', '3v3', '5v5', 'rbg'):
        raise BNetValueError("PvP Bracket not correct:  '2v2', '3v3', '5v5', 'rbg'")

    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}"

    if pvp_bracket:
        uri += f"/pvp-bracket/{utils.slugify(pvp_bracket)}"
    else:
        uri += "/pvp-summary"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def quests(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    completed: Optional[bool] = False,
    release: Optional[str] = "retail",
    locale: Optional[str] = None,
):
    """Returns a character's active quests as well as a link to the character's completed quests, or
    a list of quests that a character has completed.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        completed (bool):  To show all quests (False), or to show only
            completed quests (True)
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/quests"

    if completed:
        uri += f"/completed"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def reputations_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a summary of a character's reputations.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += (
        f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/reputations"
    )

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def soulbinds(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a character's soulbinds.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/soulbinds"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def specializations_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a summary of a character's specializations.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/specializations"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def statistics_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a statistics summary for a character.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/statistics"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def title_summary(
    region_tag: str,
    realm_name: str,
    character_name: str,
    *,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a summary of titles a character has obtained.

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the slug for the character's realm
        character_name (str): name of character
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/profile/wow/character/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(character_name)}/titles"

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag,  "profile", release)
    }
    return uri, params


@verify_region
def guild(
    region_tag: str,
    realm_name: str,
    guild_name: str,
    *,
    category: Optional[str] = None,
    release: Optional[str] = "retail",
    locale: Optional[str] = None
):
    """Returns a single guild by its name and realm, achievements, activity, or roster

    Args:
        region_tag (str): region_tag abbreviation
        realm_name (str): the name of the guild's realm
        guild_name (str): the name of the guild
        category (str): category of guild data to retrieve
        release (str): release of the game (ie classic1x, classic, retail)
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{utils.api_host(region_tag)}/data/wow/guild/"
    uri += f"{utils.slugify(realm_name)}/{utils.slugify(guild_name)}"

    if category:
        if category in ("activity", "achievements", "roster"):
            uri += f"/{category}"
        else:
            raise BNetValueError("Category Invalid: current choices activity, achievement and roster")

    params = {
        "locale": utils.localize(locale),
        "namespace": namespace(region_tag, "profile", release)
    }
    return uri, params
