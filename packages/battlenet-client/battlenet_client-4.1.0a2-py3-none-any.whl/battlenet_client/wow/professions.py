"""Defines the Achievement related classes for WoW and WoW Classic

This module contains the client class definitions for accessing World of Warcraft API endpoints.
There are two flavors of clients, one implements the client credential workflow, which happens
to be the most common.  The other implements the user authorization workflow

Examples:
    > from wow_api import WoWCredentialClient
    > client = WoWCredentialClient(<region>, <locale>, client_id='<client ID>', client_secret='<client secret>')
    > achievement_category = AchievementCategory(client, <locale>, category_id=3)

Defines the various game data API requests for World of Warcraft and
World of Warcraft Classic

Disclaimer:
All rights reserved, Blizzard is the intellectual property owner of WoW and WoW Classic
and any data pertaining thereto

Author:
David "Gahd" Couples <gahdania@gahd.io>
"""
# TODO: v4.2.0 add professions