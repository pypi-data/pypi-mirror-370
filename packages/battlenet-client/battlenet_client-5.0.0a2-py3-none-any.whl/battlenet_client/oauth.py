"""Defines the functions that generate the URLs, parameter lists, and headers
for the OAuth API Endpoints

Functions:
    user_info(region_tag, locale)
    validate_token(region_tag, token, locale)

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""

from typing import Optional

from .utils import *
from .decorators import verify_region


__version__ = "1.0.3"
__author__ = "David \"Gahd\" Couples"


@verify_region
def user_info(region_tag: str, locale: Optional[str] = None) -> tuple:
    """Returns the user info

    Args:
        region_tag (str): region_tag abbreviation
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    url = f"{auth_host(region_tag)}/oauth/userinfo"

    params = {"locale": localize(locale)}

    return url, params


@verify_region
def token_validation(region_tag: str,  token: str, locale: Optional[str] = None) -> tuple:
    """Returns if the token is still valid or not

    Args:
        region_tag (str): region_tag abbreviation
        token (str): token string to validate
        locale (str): which locale to use for the request

    Returns:
        tuple: The URL (str) and parameters (dict)
    """
    url = f"{auth_host(region_tag)}/oauth/check_token"

    params = {"locale": localize(locale), 'token': token}

    return url, params
