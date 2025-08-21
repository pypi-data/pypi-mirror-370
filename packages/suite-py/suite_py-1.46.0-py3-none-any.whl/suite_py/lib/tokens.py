# -*- encoding: utf-8 -*-
import base64
import marshal
import os
import time
from sys import platform

import keyring
from InquirerPy import prompt

from suite_py.lib import logger

TOKENS = ["github", "youtrack"]


def platform_has_chmod():
    return platform != "win32"


def should_use_keyring():
    # Test that the OS' keyring provider actually works.
    # If it doesn't work, or the OS doesn't provide one, we can just fall back to using a file.
    try:
        test_str = str(round(time.time() * 1000))
        keyring.set_password("suite_py_test", "test", test_str)
        test_success = keyring.get_password("suite_py_test", "test") == test_str

        try:
            keyring.delete_password("suite_py_test", "test")
        except Exception:
            # We can safely ignore this if deleting the test keyring fails
            pass

        if not test_success:
            raise RuntimeError("Loaded keyring didn't match the saved test keyring")

        return True
    except Exception as error:
        logger.warning(
            f"suite-py was unable to store secrets using your OS' keyring provider; falling back to file-based tokens (less secure.) Error: {error}"
        )
        return False


USE_KEYRING = should_use_keyring()


class Tokens:
    def __init__(self, file_name=os.path.join(os.environ["HOME"], ".suite_py/tokens")):
        self._file_name = file_name

        try:
            self._tokens = self.load() or {}
        except Exception as error:
            self._tokens = {}
            logger.warning(f"Failed to load tokens! Error: {error}")

        self._changed = False
        self.check()
        if self._changed:
            self.save()

        self.chmod()

    def check(self):
        for token in TOKENS:
            if not self._tokens.get(token):
                self._tokens[token] = prompt(
                    [
                        {
                            "type": "input",
                            "name": token,
                            "message": f"Insert your {token.capitalize()} token:",
                        }
                    ]
                )[token]
                self._changed = True

    def load_from_keyring(self):
        decoded = keyring.get_password("suite_py", "tokens")
        if decoded is None:
            return None

        decoded = base64.b64decode(decoded)
        decoded = marshal.loads(decoded)
        return decoded

    def load_from_file(self):
        if os.path.exists(self._file_name):
            with open(self._file_name, "rb") as configfile:
                return marshal.load(configfile)
        else:
            return None

    def load(self):
        has_tokens_file = os.path.exists(self._file_name)

        if USE_KEYRING and not has_tokens_file:
            tokens = self.load_from_keyring()
        else:
            tokens = self.load_from_file()

            try:
                if USE_KEYRING and has_tokens_file and tokens is not None:
                    # If we are on a platform that uses keyring instead of a tokens file, attempt to migrate the tokens file to keyring.
                    # What we'll do is try to save the tokens to keyring, and then load them from the keyring.
                    # If the loaded tokens match the tokens in the file, we can safely delete the file, completing the migration.
                    self.save(tokens)

                    if tokens == self.load_from_keyring():
                        try:
                            os.remove(self._file_name)
                        except Exception as error:
                            logger.warning(
                                f"Could not delete old tokens file! Your tokens may be vulnerable to attackers. Please `rm {self._file_name}` manually. Error: {error}"
                            )
            except Exception as error:
                logger.warning(
                    f"Failed to migrate old tokens file to keyring! Your tokens may be vulnerable to attackers. Error: {error}"
                )

        return tokens

    def save(self, tokens=None):
        if tokens is None:
            # default `tokens` to `self._tokens`
            tokens = self._tokens

        if USE_KEYRING:
            encoded = marshal.dumps(tokens)
            encoded = base64.b64encode(encoded)
            encoded = encoded.decode("utf-8")
            keyring.set_password("suite_py", "tokens", encoded)
        else:
            with open(self._file_name, "wb") as configfile:
                marshal.dump(tokens, configfile)

    def chmod(self):
        if os.path.exists(self._file_name):
            try:
                if not platform_has_chmod():
                    raise RuntimeError("chmod is not supported on this OS")

                os.chmod(self._file_name, 0o600)
            except Exception as error:
                logger.warning(
                    f"Could not set permissions on tokens file! Your tokens may be vulnerable to attackers. Please `chmod 600 {self._file_name}` manually. Error: {error}"
                )

    def edit(self, service, token):
        self._tokens[service] = token
        self.save()

    def keys(self):
        return self._tokens.keys()

    @property
    def github(self):
        return self._tokens["github"]

    @property
    def youtrack(self):
        return self._tokens["youtrack"]

    def okta(self):
        return self._tokens.get("okta", {})
