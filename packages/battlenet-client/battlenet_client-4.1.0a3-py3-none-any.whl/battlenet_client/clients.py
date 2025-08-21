"""Defines the base class "BNetClient"

Classes:
    BNetClient
    CredentialClient


Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
from typing import Optional, List

from oic import rndstr

from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import RegistrationResponse, AuthorizationResponse
from oic.oauth2 import REQUEST2ENDPOINT
from oic.oauth2.message import CCAccessTokenRequest, ASConfigurationResponse

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from decouple import config

from battlenet_client import utils
from battlenet_client import constants as bnet_constants
from battlenet_client import exceptions as bnet_exceptions


class BNetClient(Client):
    """Defines the base OAuth v2 Authorization code flow/OpenID Connect
    client class for the battlenet_client package

    Args:
        region (str): region abbreviation for use with the APIs

    Keyword Args:
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal
        scope (list, optional): the scope or scopes to use during the
            endpoints that require the Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful
            authentication between the user and Blizzard

    Attributes:
        tag (str): the region tag (abbreviation) of the client
    """

    __author__ = 'David "Gahd" Couples'
    __version__ = "3.0.0"

    def __init__(self, region: str, *, client_id: Optional[str] = None, client_secret: Optional[str] = None,
                 scope: Optional[List[str]] = None, redirect_uri: Optional[str] = None) -> None:

        if not client_id:
            client_id = config("CLIENT_ID")

        super().__init__(client_id=client_id, client_authn_method=CLIENT_AUTHN_METHOD)

        if not client_secret:

            client_secret = config("CLIENT_SECRET")

        self.client_secret = client_secret

        self.nonce = rndstr()
        self.state = rndstr()

        try:
            self.tag = getattr(bnet_constants, region)
        except AttributeError:
            if region.strip().lower() in ("us", "eu", "kr", "tw", "cn"):
                self.tag = region.strip().lower()
            else:
                raise bnet_exceptions.BNetRegionNotFoundError("Region not available")

        op_data = {"version": "3.0", "issuer": f"{utils.auth_host(region)}/oauth",
                   "token_endpoint": f"{utils.auth_host(region)}/oauth/token", "redirect_uri": redirect_uri}

        if scope:
            op_data.update({"authorization_endpoint": f"{utils.auth_host(region)}/oauth/authorize",
                            "userinfo_endpoint": f"{utils.auth_host(region)}/oauth/userinfo",
                            "jwks_uri": f"{utils.auth_host(region)}/oauth/jwks/certs",
                            'scope': scope})

        else:
            REQUEST2ENDPOINT["CCAccessTokenRequest"] = f"{utils.auth_host(region)}/oauth/token"

        op_info = ASConfigurationResponse(**op_data)
        self.handle_provider_config(op_info, op_info["issuer"])

        info = {
            "client_id": client_id,
            "client_secret": client_secret,
        }
        client_reg = RegistrationResponse(**info)
        self.store_registration_info(client_reg)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.__version__}"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.__version__}"

    def authorization_url(self, **kwargs):
        """Prepares and returns the authorization URL to the Battle.net
        authorization servers

        Returns:
            str: the URL to the Battle.net authorization server
        """
        args = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": self.provider_info['scope'],
            "nonce": self.nonce,
            "redirect_uri": self.provider_info["redirect_uri"],
            "state": self.state
        }

        auth_req = self.construct_AuthorizationRequest(request_args=args, **kwargs)
        return auth_req.request(self.authorization_endpoint)

    def authorization_response(self, response: str):
        """Processes the authorization response from the Battle.net
        authorization servers

        Args:
            response (str): the query string from the callback

        Returns:
            Nothing
        """
        auth_resp = self.parse_response(AuthorizationResponse, info=response, sformat="urlencoded")
        assert auth_resp["state"] == self.state

        args = {"code": auth_resp["code"]}

        self.do_access_token_request(
            state=auth_resp["state"], request_args=args, authn_method="client_secret_basic"
        )


class CredentialClient(OAuth2Session):
    """Defines the child OAuth v2 Authorization code flow/OpenID Connect client for handling
    Hearthstone API endpoints

    Args:
        region (str): region abbreviation for use with the APIs

    Keyword Args:
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal

    Attributes:
        tag (str): the region tag (abbreviation) of the client
        api_host (str): the host to use for accessing the API endpoints
        auth_host (str): the host to use for authentication
        render_host (str): the hose to use for images
    """

    __author__ = 'David "Gahd" Couples'
    __version__ = "2.1.1"

    def __init__(self, region: str, *, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> None:

        self._state = None

        if not client_id:
            client_id = config("CLIENT_ID")

        if not client_secret:
            client_secret = config("CLIENT_SECRET")

        try:
            self.tag = getattr(bnet_constants, region)
        except AttributeError:
            if region.strip().lower() in ("us", "eu", "kr", "tw", "cn"):
                self.tag = region.strip().lower()
            else:
                raise bnet_exceptions.BNetRegionNotFoundError("Region not available")

        self._client_secret = client_secret

        if self.tag == "cn":
            self.api_host = "https://gateway.battlenet.com.cn"
            self.auth_host = "https://oauth.battlenet.com.cn"
            self.render_host = "https://render.worldofwarcraft.com.cn"
        elif self.tag in ("kr", "tw"):
            self.api_host = f"https://{self.tag}.api.blizzard.com"
            self.auth_host = "https://oauth.battle.net"
            self.render_host = f"https://render-{self.tag}.worldofwarcraft.com"
        else:
            self.api_host = f"https://{self.tag}.api.blizzard.com"
            self.auth_host = f"https://oauth.battle.net"
            self.render_host = f"https://render-{self.tag}.worldofwarcraft.com"

        super().__init__(client=BackendApplicationClient(client_id=client_id))
        self.fetch_token(token_url=f"{self.auth_host}/oauth/token", client_id=client_id, client_secret=client_secret)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.__version__} ({self.tag.upper()})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.__version__} ({self.tag.upper()})"
