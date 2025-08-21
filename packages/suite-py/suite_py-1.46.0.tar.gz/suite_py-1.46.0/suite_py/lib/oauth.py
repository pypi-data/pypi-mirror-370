import base64
import hashlib
import secrets
import typing
import urllib.parse
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path
from urllib.parse import parse_qs, urlparse

import requests

import suite_py
from suite_py.lib import logger


@dataclass
class OAuthTokenResponse:
    access_token: str
    id_token: typing.Optional[str]
    refresh_token: typing.Optional[str]
    expires_in: float


class OAuthError(Exception):
    pass


def retrieve_token(base_url, params) -> OAuthTokenResponse:
    url = f"{base_url}/token"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    data = requests.post(url, headers=headers, data=params, timeout=30).json()
    logger.debug(data)

    if error := data.get("error_description", data.get("errorSummary", None)):
        raise OAuthError(f"OAuth error: {error}")

    return OAuthTokenResponse(
        access_token=data["access_token"],
        expires_in=data["expires_in"],
        id_token=data.get("id_token", None),
        refresh_token=data.get("refresh_token", None),
    )


class OAuthCallbackServer(HTTPServer):
    received_state: typing.Optional[str] = None
    error_message: typing.Optional[str] = None
    code: typing.Optional[str] = None

    def __init__(self, server_address) -> None:
        super().__init__(server_address, OAuthCallbackRequestHandler)


class OAuthCallbackRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        assert isinstance(self.server, OAuthCallbackServer)

        server = self.server
        args = parse_qs(urlparse(self.path).query)

        server.received_state = args["state"][0]
        if "error" in args:
            error = args["error"][0]
            error_description = args["error_description"][0]
            server.error_message = f"{error}: {error_description}"
        else:
            server.code = args["code"][0]

        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()

        template = path.join(path.dirname(suite_py.__file__), "templates/login.html")
        with open(template, "rb") as f:
            self.wfile.write(f.read())


def _url_encode_no_padding(byte_data):
    """
    Safe encoding handles + and /, and also replace = with nothing
    """
    return base64.urlsafe_b64encode(byte_data).decode("utf-8").replace("=", "")


def _generate_challenge(a_verifier):
    return _url_encode_no_padding(hashlib.sha256(a_verifier.encode()).digest())


def authorization_code_flow(
    client_id,
    base_url,
    scope,
    redirect_uri="http://127.0.0.1:5000/callback",
    listen=("127.0.0.1", 5000),
):
    # From https://developer.okta.com/docs/guides/sign-into-web-app-redirect/python/main/
    # Step1: Create code verifier: Generate a code_verifier that will be sent to Okta to request tokens.
    verifier = _url_encode_no_padding(secrets.token_bytes(32))
    # Step2: Create code challenge: Generate a code_challenge from the code_verifier that will be sent to Okta to request an authorization_code.
    challenge = _generate_challenge(verifier)
    state = _url_encode_no_padding(secrets.token_bytes(32))

    # We generate a nonce (state) that is used to protect against attackers invoking the callback
    url = f"{base_url}/authorize?"
    url_parameters = {
        "scope": scope,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_challenge": challenge.replace("=", ""),
        "code_challenge_method": "S256",
        "state": state,
    }
    url = url + urllib.parse.urlencode(url_parameters)

    # Step3: Authorize user: Request the user's authorization and redirect back to your app with an authorization_code.
    # Open the browser window to the login url
    # Start the server
    logger.info("A browser tab should've opened. If not manually navigate to: " + url)
    webbrowser.open(url)

    server = OAuthCallbackServer(listen)
    server.handle_request()

    if state != server.received_state:
        raise OAuthError(
            "Error: session replay or similar attack in progress. Please log out of all connections."
        )

    if server.error_message:
        raise OAuthError(server.error_message)

    # Step4: Request tokens: Exchange your authorization_code and code_verifier for tokens.
    body = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code_verifier": verifier,
        "code": server.code,
        "redirect_uri": redirect_uri,
    }
    return retrieve_token(base_url, body)


def do_refresh_token(
    client_id: str, base_url: str, scope: str, refresh_token: str
) -> OAuthTokenResponse:
    # See https://developer.okta.com/docs/guides/refresh-tokens/main/
    params = {
        "scope": scope,
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    return retrieve_token(base_url, params)
