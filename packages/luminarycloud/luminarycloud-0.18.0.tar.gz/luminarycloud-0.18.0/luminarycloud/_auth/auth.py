# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import json
import logging
import webbrowser
from typing import cast, Optional
from urllib.parse import urljoin, urlencode
from werkzeug.datastructures import MultiDict

import requests

from .callback_listener import CallbackListener
from .config import (
    LC_AUTH_DOMAIN,
    LC_AUTH_CLIENT_ID,
    LC_AUTH_SERVICE_ID,
    LC_REFRESH_ROTATION,
    TIMEOUT,
    ALLOWED_CALLBACK_PORTS,
)
from .credentials_store import CredentialsStore
from .exceptions import AuthException, InteractiveAuthException, SecurityAlertException
from .util import generate_nonce, sha256_challenge, decode_jwt, unix_timestamp_now

logger = logging.getLogger(__name__)

CREDENTIALS_DB_NAME = "tokens2"


class Auth0Client:
    """
    Manages Auth0 authentication and credentials.

    Parameters
    ----------
    domain : str
        (Optional) Auth0 tenant domain.
    client_id : str
        (Optional) Auth0 client ID
    audience : str
        (Optional) Auth0 audience (i.e. target service ID)
    noninteractive : bool
        (Optional) If True, prevents client from ever attempting an interactive login (i.e.
        launching an http server and opening the login page in a web browser). In cases where user
        interaction is required, an error will be raised. Default: False
    access_token : str
        (Optional) Auth0 access token.
    refresh_token : str
        (Optional) Auth0 refresh token.
    refresh_rotation : bool
        (Optional) If True, refresh token rotation will be enabled. This must
        match the setting for the tenant in Auth0.
    """

    def __init__(
        self,
        domain: Optional[str] = None,
        client_id: Optional[str] = None,
        audience: Optional[str] = None,
        noninteractive: bool = False,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        refresh_rotation: Optional[bool] = None,
    ):
        self.domain = domain or LC_AUTH_DOMAIN  # Auth0 tenant domain
        self.client_id = client_id or LC_AUTH_CLIENT_ID  # Auth0 ID for client
        self.audience = audience or LC_AUTH_SERVICE_ID  # Auth0 ID for service
        self.noninteractive = noninteractive  # True to prevent interactive login
        self.refresh_rotation = (
            refresh_rotation or LC_REFRESH_ROTATION
        )  # True if refresh token rotation is enabled on Auth0
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.credentials_store = CredentialsStore(CREDENTIALS_DB_NAME)

    @property
    def base_url(self) -> str:
        return f"https://{self.domain}"

    def _save_refresh_token(self) -> None:
        logger.info("Saving refresh token.")
        self.credentials_store.save("refresh_token", self.refresh_token)

    def _recall_refresh_token(self) -> None:
        logger.info("Attempting to load refresh token.")
        self.refresh_token = self.credentials_store.recall("refresh_token")

    @property
    def access_token(self) -> Optional[str]:
        if self.is_token_expired():
            return None
        return self._access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        self._access_token: Optional[str] = None
        self._access_token_exp: Optional[int] = None
        if value is not None:
            logger.debug("Setting access token.")
            payload = decode_jwt(value)  # raises an error if invalid JWT
            self._access_token = value
            self._access_token_exp = int(payload["exp"])

    def is_token_expired(self) -> bool:
        return (
            self._access_token is None
            or self._access_token_exp is None
            or self._access_token_exp < unix_timestamp_now()
        )

    # This is not part of the @property getter due to potential side-effects.
    # If token does not exist, tries to grab a new one and throws an error if it
    # cannot.
    def fetch_refresh_token(self) -> str:
        if self.refresh_token is None:
            self._recall_refresh_token()
        if self.refresh_token is None:
            self.user_login()
        return cast(str, self.refresh_token)

    # This is not a @property due to potential side-effects.
    # If token does not exist or is expired, tries to grab a new one and throws
    # an error if it cannot.
    def fetch_access_token(self) -> str:
        if self.access_token is None:
            logger.info("No valid access token. Fetching new access token.")
            try:
                self.silently_renew_access_token()
            except (requests.HTTPError, AuthException):
                self.user_login()
        return cast(str, self.access_token)

    # Attempt to fetch a new access token via refresh token without user interaction.
    def silently_renew_access_token(self) -> str:
        if self.refresh_token is None:
            self._recall_refresh_token()
        if self.refresh_token is None:
            raise InteractiveAuthException(
                "Cannot silently renew access token without refresh token."
            )

        logger.info("Attempting to silently renew access token.")

        # Send token refresh request.
        url = urljoin(self.base_url, "oauth/token")
        headers = {"Content-Type": "application/json"}
        body = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.refresh_token,
        }
        response = requests.post(url, headers=headers, data=json.dumps(body), timeout=TIMEOUT)

        # raise an error if we get a 40X status code
        try:
            response.raise_for_status()
        # TODO: handle other specific error cases
        except:
            logger.info("Failed to silently authenticate.")
            raise

        logger.info("Received successful response. Extracting token.")

        # Extract tokens and return new access token
        data = response.json()
        self.access_token = data["access_token"]
        assert self.access_token
        if self.refresh_rotation:
            self.refresh_token = data["refresh_token"]
            self._save_refresh_token()
        return self.access_token

    def user_login(self) -> str:
        """
        Initiates the Auth0 authorization code flow w/ PKCE.

        Overview of steps:
            - We generate a key pair: verifier and challenge
            - We sends the user (via browser) to Auth0 with the challenge and the desired scopes
            - Auth0 redirects the user to a log in page
            - After the user logs in and consents, Auth0 redirects the browser to a localhost URL
            - We receive the redirect (via a local HTTP server) and extract the auth code
            - We send the auth code along with verifier to Auth0 to exchange for an access token

        Returns
        -------
        access_token : str

        Raises
        ------
        InteractiveAuthException
            If user interaction is required, and self.noninteractive is True.
        SecurityAlertException
            If the callback server receives a request from a potential attacker.
        AuthException
            If the tokens received from the Auth0 exchange are not found in the response.
        """
        if self.noninteractive:
            raise InteractiveAuthException(
                "User interaction disabled, cannot initiate browser login."
            )

        logger.info("Initiating user login.")

        logger.debug("Generating PKCE code challenge.")
        verifier = generate_nonce()
        challenge = sha256_challenge(verifier)

        logger.debug("Generating URL for auth request.")
        session_nonce = generate_nonce()  # To protect against attackers invoking the callback
        scopes = [
            "openid",  # Prerequisite scope for profile and email
            "profile",  # To include user metadata (e.g. full name)
            "email",  # To include user email
            "offline_access",  # To include refresh token
        ]
        url_parameters = {
            "audience": self.audience,
            "client_id": self.client_id,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": session_nonce,
        }

        logger.debug("Starting callback server")
        with CallbackListener(allowed_ports=ALLOWED_CALLBACK_PORTS) as listener:

            # Write redirect_uri depending on the actual port the listener is running on.
            redirect_uri = f"http://127.0.0.1:{listener.port}/callback"
            url_parameters["redirect_uri"] = redirect_uri
            authorize_url = urljoin(self.base_url, "authorize?" + urlencode(url_parameters))

            logger.info("Prompting interactive login via browser.")
            if webbrowser.open_new(authorize_url):
                interaction_detail = "Your browser has been opened to visit the following URL"
            else:
                interaction_detail = "Please visit the following URL in your browser"
            print(
                f"Interactive login required. {interaction_detail}:\n\n",
                authorize_url,
                "\n",
            )
            logger.debug("Waiting for redirect callback.")
            callback_args = listener.block_until_callback()

        if "error" in callback_args:
            raise AuthException(callback_args["error"] + ": " + callback_args["error_description"])
        if session_nonce != callback_args["state"]:
            raise SecurityAlertException(
                "Session replay or similar attack in progress. Please log out of all connections."
            )

        # Extract auth code
        logger.info("Received response. Extracting auth code.")
        auth_code = callback_args["code"]

        logger.info("Exchanging auth code for access token.")
        url = urljoin(self.base_url, "oauth/token")
        headers = {"Content-Type": "application/json"}
        body = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "audience": self.audience,
            "code_verifier": verifier,
            "code": auth_code,
        }
        response = requests.post(url, headers=headers, data=json.dumps(body), timeout=TIMEOUT)

        # raise an error if we get a 40X status code
        try:
            response.raise_for_status()
        # TODO: handle other specific error cases
        except:
            logger.exception("Failed to exchange auth code.")
            raise

        logger.info("Received successful response. Extracting tokens.")
        data = response.json()
        try:
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
        except KeyError:
            raise AuthException("Invalid response")
        assert self.access_token

        self._save_refresh_token()
        return self.access_token
