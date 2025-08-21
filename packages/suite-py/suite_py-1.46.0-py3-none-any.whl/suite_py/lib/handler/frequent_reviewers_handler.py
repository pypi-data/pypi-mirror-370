from operator import itemgetter

from suite_py.lib import logger
from suite_py.lib.handler.prompt_utils import checkbox_with_manual_fallback


class FrequentReviewersHandler:
    """
    A handler for auto-suggesting reviewers for a PR. It uses a "cookie" to store a set of
    reviewers, and how frequently the user chooses them, and then suggests the most
    frequently chosen ones. Needs a handle to the config to store and load it's cookie.
    """

    def __init__(self, config):
        self._config = config
        self._frequent_reviewers = self._load_cookie()
        self._max_reviewers = config.user["frequent_reviewers_max_number"]

    def _load_cookie(self):
        try:
            return dict(self._config.get_cookie("frequent_reviewers", {}))
        except Exception:
            return {}

    def _save_cookie(self):
        try:
            self._config.put_cookie("frequent_reviewers", self._frequent_reviewers)
        except Exception as error:
            logger.warning(f"Failed to save frequent reviewers: {error}")

    def _get(self, amount):
        if not self._frequent_reviewers:
            return []

        sorted_reviewers = dict(
            sorted(self._frequent_reviewers.items(), key=itemgetter(1), reverse=True)
        )
        return list(sorted_reviewers.keys())[:amount]

    def _update_cookie(self, selected):
        for reviewer in selected:
            if reviewer not in self._frequent_reviewers:
                self._frequent_reviewers[reviewer] = 1
            else:
                self._frequent_reviewers[reviewer] += 1
        self._save_cookie()

    def select_reviewers(self, users, autocomplete=None):
        reviewers = self._get(self._max_reviewers)

        msg = "Choose a reviewer (name.surname - press TAB for autocomplete)"
        reviewers = checkbox_with_manual_fallback(msg, reviewers, autocomplete)

        # If they don't choose any, just return an empty list
        if not reviewers:
            return []

        # Update the frequent reviewers list
        nicknames = [n["youtrack"] for n in users]
        self._update_cookie([r for r in reviewers if r in nicknames])

        return reviewers
