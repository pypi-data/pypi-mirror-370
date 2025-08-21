"""Defines the functions that handle the community APIs for Diablo III

Functions:
    act(region_tag, act_id, locale)
    artisan(region_tag, artisan_slug, locale)
    recipe(region_tag, artisan_slug, recipe_slug, locale)
    follower(region_tag, follower_slug, locale)
    character_class(region_tag, class_slug, locale)
    api_skill(region_tag, class_slug, skill_slug, locale)
    item_type(region_tag, item_type_slug, locale)
    item(region_tag, item_slug, locale)
    api_account(region_tag, bnet_tag, locale)
    api_hero(region_tag, bnet_tag, hero_id, category, locale)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from typing import Union, Optional
from urllib.parse import quote as urlquote

from ..decorators import verify_region
from ..exceptions import BNetValueError
from ..utils import slugify, localize, api_host


__version__ = "2.0.0"
__author__ = "David \"Gahd\" Couples"


@verify_region
def act(
    region_tag: str,
    *,
    act_id: Optional[Union[int, str]] = None,
    locale: Optional[str] = None
):
    """Returns the index of acts, or the act by ID

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        act_id (int, optional): the act's ID to retrieve its data

    Returns:
        tuple: The URL (str) and parameters (dict)
    """

    uri = f"{api_host(region_tag)}/d3/data/act"

    if act_id:
        uri += f"/{act_id}"

    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def artisan(
    region_tag: str, artisan_slug: str, locale: Optional[str] = None
):
    """Returns a single artisan by the slug

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        artisan_slug (str): the slug of the artisan

    Returns:
        tuple: The URL (str) and parameters (dict)
    """

    uri = f"{api_host(region_tag)}/d3/data/artisan/{slugify(artisan_slug)}"
    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def recipe(
    region_tag: str,
    artisan_slug: str,
    recipe_slug: str,
    locale: Optional[str] = None,
):
    """Returns a single recipe by slug for the specified artisan.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        artisan_slug (str): the slug of the artisan
        recipe_slug (str): the slug of the recipe

    Returns:
        tuple: The URL (str) and parameters (dict)
    """

    uri = f"{api_host(region_tag)}/d3/data/artisan/{slugify(artisan_slug)}/recipe"
    uri += f"/{slugify(recipe_slug)}"
    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def follower(
    region_tag: str, follower_slug: str, locale: Optional[str] = None
):
    """Returns a single follower by slug.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        follower_slug (str): the slug of a follower

    Returns:
        tuple: The URL (str) and parameters (dict)
    """

    uri = f"{api_host(region_tag)}/d3/data/follower/{slugify(follower_slug)}"
    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def character_class(
    region_tag: str, class_slug: str, locale: Optional[str] = None
):
    """Returns a single character class by slug.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        class_slug (str): the slug of a character class

    Returns:
        tuple: The URL (str) and parameters (dict)
    """

    uri = f"{api_host(region_tag)}/d3/data/hero/{slugify(class_slug)}"
    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def api_skill(
    region_tag: str,
    class_slug: str,
    skill_slug: str,
    locale: Optional[str] = None,
):
    """Returns a single skill by slug for a specific character class.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        class_slug (str): the slug of a character class
        skill_slug (str):

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{api_host(region_tag)}/d3/data/hero/{slugify(class_slug)}"
    uri += f"/skill/{slugify(skill_slug)}"
    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def item_type(
    region_tag: str,
    *,
    item_type_slug: Optional[str] = None,
    locale: Optional[str] = None,
):
    """Returns an index of item types, or a single item type by slug

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        item_type_slug (str, optional): the slug of an item type

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    uri = f"{api_host(region_tag)}/d3/data/item-type"

    if item_type_slug:
        uri += f"/{slugify(item_type_slug)}"

    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def item(region_tag: str, item_slug: str, locale: Optional[str] = None):
    """Returns a single item by item slug and ID.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        item_slug (str): the slug of the item

    Returns:
        tuple: The URL (str) and parameters (dict)
    """

    uri = f"{api_host(region_tag)}/d3/data/item/{item_slug}"
    print(uri)
    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def api_account(
    region_tag: str, bnet_tag: str, locale: Optional[str] = None
):
    """Returns the specified account profile.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        bnet_tag (str): bnet tag of the user

    Returns:
        tuple: The URL (str) and parameters (dict)
    """

    uri = f"{api_host(region_tag)}/d3/profile/{urlquote(bnet_tag)}/"

    params = {"locale": localize(locale)}

    return uri, params


@verify_region
def api_hero(
    region_tag: str,
    bnet_tag: str,
    hero_id: str,
    *,
    category: Optional[str] = None,
    locale: Optional[str] = None
):
    """Returns a single hero, a list of items for the specified hero, or
    list of items for the specified hero's followers.

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request
        bnet_tag (str): BNet tag for the account
        hero_id (str):  Hero's ID
        category (str): category to retrieve if specified ('items', 'follower-items')

    Returns:
        tuple: The URL (str) and parameters (dict)

    Raises:
        BNetValueError: category is not None and not 'items' or 'follower-items'
    """
    uri = f"{api_host(region_tag)}/d3/profile/{urlquote(bnet_tag)}/"
    uri += f'hero/{hero_id}'

    params = {"locale": localize(locale)}

    if category:

        if category not in ("items", "follower-items"):
            raise BNetValueError(
                "Invalid category;  Valid categories are 'items' and 'follower-items'"
            )

        uri += f"/{category.lower()}"

    return uri, params
