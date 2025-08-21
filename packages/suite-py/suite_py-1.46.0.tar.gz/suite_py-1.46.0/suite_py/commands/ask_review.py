# -*- coding: utf-8 -*-
import sys

from suite_py.lib import logger, metrics
from suite_py.lib.handler.frequent_reviewers_handler import FrequentReviewersHandler
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.prompt_utils import make_completer
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class AskReview:
    def __init__(self, project, captainhook, config, tokens):
        self._project = project
        self._config = config
        self._youtrack = YoutrackHandler(config, tokens)
        self._captainhook = captainhook
        self._git = GitHandler(project, config)
        self._github = GithubHandler(tokens)
        self._frequent_reviewers = FrequentReviewersHandler(config)

    @metrics.command("ask-review")
    def run(self):

        users = self._maybe_get_users_list()
        pr = self._get_pr()
        youtrack_reviewers = self._ask_reviewer(users)
        github_reviewers = _find_github_nicks(youtrack_reviewers, users)
        pr.create_review_request(github_reviewers)
        logger.info("Adding reviewers on GitHub")
        self._maybe_adjust_youtrack_card(pr.title, youtrack_reviewers)

    def _maybe_get_users_list(self):
        try:
            users = self._captainhook.get_users_list().json()
            self._config.put_cache("users", users)
            return users
        except Exception:
            logger.warning(
                "Can't get users list from Captainhook. Using cached version."
            )
            return self._config.get_cache("users")

    def _get_pr(self):
        branch_name = self._git.current_branch_name()
        pull = self._github.get_pr_from_branch(self._project, branch_name)

        if pull.totalCount:
            pr = pull[0]
            logger.info(
                f"I found pull request number {pr.number} for branch {branch_name} on repo {self._project}"
            )
        else:
            logger.error(f"No open pull requests found for branch {branch_name}")
            sys.exit(-1)

        return pr

    def _maybe_adjust_youtrack_card(self, title, youtrack_reviewers):
        youtrack_id = self._youtrack.get_card_from_name(title)
        if not youtrack_id:
            logger.warning(
                "Reviewers added ONLY on GitHub. No linked card on YouTrack or missing card number in the branch name."
            )
            return

        logger.info(f"Moving the {youtrack_id} card for review on youtrack")
        self._youtrack.update_state(youtrack_id, self._config.youtrack["review_state"])

        if not self._config.youtrack["add_reviewers_tags"]:
            return
        logger.info("Adding reviewer tags on youtrack")
        for rev in youtrack_reviewers:
            try:
                self._youtrack.add_tag(youtrack_id, f"review:{rev}")
            except BaseException as e:
                logger.warning(f"I was unable to add the review tags: {e}")
                sys.exit(-1)

    def _ask_reviewer(self, users):
        completer = make_completer(
            lambda text: [
                x["youtrack"] for x in users if text.lower() in x["youtrack"].lower()
            ]
        )
        reviewers = self._frequent_reviewers.select_reviewers(
            users, autocomplete=completer
        )

        if not reviewers:
            logger.warning("You must enter at least one reviewer")
            return self._ask_reviewer(users)

        return reviewers


def _find_github_nicks(youtrack_reviewers, users):
    github_reviewers = []
    for rev in youtrack_reviewers:
        for user in users:
            if user["youtrack"] == rev:
                github_reviewers.append(user["github"])

    return github_reviewers
