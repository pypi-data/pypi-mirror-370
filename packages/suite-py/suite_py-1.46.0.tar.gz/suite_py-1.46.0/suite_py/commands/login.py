from suite_py.lib import metrics
from suite_py.lib.handler.okta_handler import Okta


class Login:
    def __init__(self, config, tokens):
        self._okta = Okta(config, tokens)

    @metrics.command("login")
    def run(self):
        self._okta.login()
