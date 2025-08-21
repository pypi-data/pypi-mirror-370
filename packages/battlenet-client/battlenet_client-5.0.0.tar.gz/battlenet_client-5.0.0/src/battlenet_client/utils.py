"""Miscellaneous functions to support for Battle.net

Functions:
    currency_convertor(value)
    slugify(value)
    localize(locale)
    api_host(region_tag)
    auth_host(region_tag)
    render_host(region_tag)
    nth_occurrence(string, sep, count)
    r_nth_occurrence(string, sep, count)

Misc Variables:
    WOW_CLASSICS


Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from .exceptions import BNetValueError

from typing import Tuple, Optional, Union
from datetime import datetime, timedelta


__version__ = '1.0.0'
__author__ = 'David \'Gahd\' Couples'


def currency_convertor(value: int) -> Tuple[int, int, int]:
    """Returns the value into gold, silver and copper

    Args:
        value (int): the value to be converted

    Returns:
        tuple: gold (int), silver (int) and copper (int)
    """    
    if not isinstance(value, int):
        raise BNetValueError("Value must be an integer")

    if value < 0:
        raise BNetValueError("Value cannot be negative")

    print(value)

    return int(value) // 10000, (value % 10000) // 100, int(value) % 100
    

def slugify(value: Union[int, str]) -> str:
    """Returns value as a slug

    Args:
        value (str): the string to be converted into a slug

    Returns:
        str: the slug
    """
    if isinstance(value, int):
        return str(value)

    return value.lower().replace("'", "").replace(" ", "-")


def localize(locale: Optional[str] = None) -> Union[None, str]:
    """Returns the standardized locale

    Args:
        locale (str): the locality to be standardized

    Returns:
        str: the locale in the format of "<language>_<DIALECT>"

    Raise:
        TypeError: when locale is not a string
        ValueError: when the lang and country are not in the given lists
    """
    if not locale:
        return None

    languages = ("en", "es", "pt", "fr", "ru", "de", "it", "ko", "zh")
    if locale[:2].lower() not in languages:
        raise BNetValueError("Invalid language")

    dialects = ("us", "mx", "br", "gb", "es", "fr", "ru", "de", "pt", "it", "kr", "tw", "cn")
    if locale[-2:].lower() not in dialects:
        raise BNetValueError("Invalid country")

    return f"{locale[:2].lower()}_{locale[-2:].upper()}"


def api_host(region_tag: str) -> str:
    """Returns the API endpoint hostname and protocol

    Args:
        region_tag (str): the region abbreviation

    Returns:
        str: The API endpoint hostname and protocol
    """
    if region_tag.lower() == "cn":
        return "https://gateway.battlenet.com.cn"

    return f"https://{region_tag.lower()}.api.blizzard.com"


def auth_host(region_tag: str) -> str:
    """Returns the authorization endpoint hostname and protocol

    Args:
        region_tag (str): the region abbreviation

    Returns:
        str: The authorization endpoint hostname and protocol
    """
    if region_tag.lower() == "cn":
        return "https://www.battlenet.com.cn"

    if region_tag.lower() in ("kr", "tw"):
        return "https://apac.battle.net"

    return f"https://{region_tag.lower()}.battle.net"


def render_host(region_tag: str) -> str:
    """Returns the render endpoint hostname and protocol

    Args:
        region_tag (str): the region abbreviation

    Returns:
        str: The render endpoint hostname and protocol
    """
    if region_tag.lower() == "cn":
        return "https://render.worldofwarcraft.com.cn"

    return f"https://render-{region_tag.lower()}.worldofwarcraft.com"


def nth_occurrence(string: str, sep: str, count: int) -> str:
    """Returns `path` ending at the `count` occurrence of `sep`

    Args:
        string (str): the original string
        sep (str): the separator that needs to be counted
        count (int): the number of occurrences of `sep`
    """
    start_index = string.find(sep)

    while start_index >= 0 and count > 1:
        start_index = string.find(sep, start_index + 1)
        count -= 1

    return string[:start_index]


def r_nth_occurrence(string: str, sep: str, count: int) -> str:
    """Returns `path` ending at the `count` occurrence of `sep`

    Args:
        string (str): the original string
        sep (str): the separator that needs to be counted
        count (int): the number of occurrences of `sep`
    """
    end_index = string.rfind(sep)

    while end_index >= 0 and count > 1:
        end_index = string.rfind(sep, 0, end_index - 1)
        count -= 1

    return string[end_index + 1:]


def next_update(last_modified: str, duration: float) -> datetime:
    """Returns the datetime object representing the last modified of the API endpoint

    Args:
        last_modified (str): 'last modified' from the response header
        duration (float): the duration in weeks for the data

    Returns:
          datetime: datetime of the next
    """
    last_modified = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
    last_modified += timedelta(weeks=duration)
    return last_modified
