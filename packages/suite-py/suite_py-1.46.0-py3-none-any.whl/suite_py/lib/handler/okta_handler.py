import time
import typing

from suite_py.lib import logger, oauth
from suite_py.lib.config import Config
from suite_py.lib.tokens import Tokens

_SCOPE = "openid offline_access"


class OktaError(Exception):
    def __init__(self, message) -> None:
        message = f"{message}\nTry relogging with 'suite-py login'"
        super().__init__(message)


class Okta:
    def __init__(self, config: Config, tokens: Tokens) -> None:
        self._config = config
        self._tokens = tokens

    def login(self):
        res = oauth.authorization_code_flow(
            self._config.okta["client_id"],
            self._config.okta["base_url"],
            _SCOPE,
        )

        self._update_tokens(res)

    def get_id_token(self) -> str:
        """
        Returns an id_token, performing a token refresh if needed
        Raises on an invalid or missing refresh token
        """
        return self._get_id_token() or self._refresh()

    def _refresh(self) -> str:
        logger.debug("Refreshing id_token")

        refresh_token = self._get_refresh_token()
        if not isinstance(refresh_token, str):
            raise OktaError("Invalid okta refresh token")

        try:
            res = oauth.do_refresh_token(
                self._config.okta["client_id"],
                self._config.okta["base_url"],
                _SCOPE,
                refresh_token,
            )
        except oauth.OAuthError as e:
            raise OktaError(f"Error refreshing a token with okta: {e}") from e

        return self._update_tokens(res)

    def _update_tokens(self, tokens: oauth.OAuthTokenResponse) -> str:
        if not tokens.id_token:
            raise OktaError("Okta didn't return a new id_token. This shouldn't happen.")
        if not tokens.refresh_token:
            raise OktaError(
                "Okta didn't return a new refresh_token. This shouldn't happen."
            )

        self._set_refresh_token(tokens.refresh_token)

        expires_at = time.time() + tokens.expires_in
        self._set_id_token(tokens.id_token, expires_at)

        return tokens.id_token

    def _get_refresh_token(self) -> typing.Optional[str]:
        return self._tokens.okta().get("refresh_token", None)

    def _set_refresh_token(self, token: str):
        okta = self._tokens.okta()
        okta["refresh_token"] = token
        self._tokens.edit("okta", okta)

    def _get_id_token(self) -> typing.Optional[str]:
        (token, expiration) = self._tokens.okta().get("id_token", (None, None))
        if token is not None and time.time() < expiration:
            return token
        return None

    def _set_id_token(self, token: str, expiration: float):
        okta = self._tokens.okta()
        okta["id_token"] = (token, expiration)
        self._tokens.edit("okta", okta)
