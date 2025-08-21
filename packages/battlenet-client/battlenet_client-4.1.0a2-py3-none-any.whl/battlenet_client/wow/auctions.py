"""Auctions

Disclaimer:
All rights reserved, Blizzard is the intellectual property owner of WoW and WoW Classic
and any data pertaining thereto

moduleauthor: David "Gahd" Couples <gahdania@gahd.online>
"""

from battlenet_client import currency_convertor
from base import WoWBase
from battlenet_client.wow.game_data import auction_house



class AuctionHouse(WoWBaseObject):
    """Defines the auction house and organizes the endpoints

    Args:
        region_tag (str): region abbreviation for use with the APIs
        connected_realm_id (int): the ID of the connected realms (a collection of realms acting as one larger realm)

    Keyword Args:
        release (str, optional): the release to use.  Currently 'classic' only.  The default of None, indicates to use
            the retail data
        locale (str, optional): the localization to use from the API, The default of None means all localizations
        scope (list of str, optional): the scope or scopes to use during the endpoints that require the
            Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal
    """

    def __init__(self, client: region_tag, connected_realm_id, *, release=None, locale=None, client=None):
        super().__init__(region_tag, connected_realm_id, release, locale, client)

        self.connected_realm = None
        self.auctions = None

        if client:
            self.get()

    def __str__(self):
        return f"Auctions: {self.connected_realm.__str__()}"

    def get(self, client=client):
        (url, params) = auction_house(region_tag, self.object_id, release=self.release, locale=self.locale)

        api_data = client.get(url, params=params)

        self.connected_realm = api_data['connected_realm']
        self.auctions = [Auction(auction) for auction in api_data['auction']]


class Auction:
    """Defines the realm specifics

    Args:
        auction (dict): auction data for an item in the auction house

    Attributes:
        id (int): ID of the auction
        item (dict): item endpoints, including any specific endpoints for the item type
        quantity (int): number of the item being sold in this auction
        unit_price (int): cost per item for the auction
        time_left (str): qualitative description of how much time is left
        buyout_price (int): the amount to buyout the auction
    """

    def __init__(self, auction):

        self.object_id = int(auction['id'])
        self.item = auction['item']
        self.quantity = int(auction['quantity'])
        self.unit_price = currency_convertor(auction['unit_price'])
        self.time_left = auction['time_left']

        if 'buyout' in auction.keys():
            self.buyout_price = currency_convertor(auction['buyout'])
