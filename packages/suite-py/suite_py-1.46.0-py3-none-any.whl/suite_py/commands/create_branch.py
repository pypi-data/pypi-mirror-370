# -*- coding: utf-8 -*-
import re
import sys

import requests

from suite_py.lib import logger, metrics
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.git_handler import GitHandler, is_branch_name_valid
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class CreateBranch:
    def __init__(self, project, card, config, tokens, autostash=False):
        self._project = project
        self._card = card
        self._config = config
        self._youtrack = YoutrackHandler(config, tokens)
        self._git = GitHandler(project, config)
        self._autostash = autostash

    @metrics.command("create-branch")
    def run(self):
        if not self._git.is_detached() and self._git.is_dirty() and not self._autostash:
            # Default behaviour is to pull when not detached.
            # Can't do that with uncommitted changes.
            logger.error("You have some uncommitted changes, I can't continue")
            sys.exit(-1)

        try:
            if self._card:
                issue = self._youtrack.get_issue(self._card)
            else:
                issue = self._youtrack.get_issue(self._ask_card())
        except Exception:
            logger.error(
                "There was a problem retrieving the issue from YouTrack. Check that the issue number is correct"
            )
            sys.exit(-1)

        self._checkout_branch(issue, self._autostash)

        user = self._youtrack.get_current_user()
        self._youtrack.assign_to(issue["id"], user["login"])

        try:
            self._youtrack.update_state(
                issue["id"], self._config.youtrack["picked_state"]
            )
        except requests.exceptions.HTTPError:
            logger.error(
                "There was a problem moving the issue to the 'picked state' on YouTrack"
            )
            logger.error(
                f"Does your YouTrack board have a state called '{self._config.youtrack['picked_state']}'?"
            )
            sys.exit(-1)

    def _select_card(self, suggestions):
        choices = ["Other..."] + [
            f"{s['idReadable']} {s['summary']}" for s in suggestions
        ]
        selected = prompt_utils.ask_choices(
            "What YouTrack issue do you want to work on?", choices, "Other..."
        )

        return (
            self._prompt_custom_card()
            if selected == "Other..."
            else selected.split(" ")[0]
        )

    def _prompt_custom_card(self):
        return prompt_utils.ask_questions_input(
            "Insert the YouTrack issue number:", self._config.user["default_slug"]
        )

    def _ask_card(self):
        suggestions = self._get_card_suggestions()
        user_choice = (
            self._select_card(suggestions)
            if suggestions
            else self._prompt_custom_card()
        )
        return user_choice

    def _get_card_suggestions(self):
        try:
            return self._youtrack.search_issues(
                self._config.user["card_suggest_query"], 5
            )
        except Exception:
            logger.warning(
                "No card suggestions (have you set card_suggest_query in your config? Query syntax: https://www.jetbrains.com/help/youtrack/server/Search-and-Command-Attributes.html)"
            )
            return []

    def _checkout_branch(self, issue, autostash=False):
        default_parent_branch_name = self._config.user.get(
            "default_parent_branch", self._git.current_branch_name()
        )

        parent_branch_name = prompt_utils.ask_questions_input(
            "Insert initial branch: ", default_parent_branch_name
        )

        full_branch_name = ""
        branch_name = _normalize_git_ref_segment(issue["summary"])
        branch_type = _normalize_git_ref_segment(issue["Type"])

        while True:
            branch_name = str(
                prompt_utils.ask_questions_input("Enter branch name: ", branch_name)
            )

            full_branch_name = f"{issue['idReadable']}/{branch_type}/{branch_name}"
            if is_branch_name_valid(full_branch_name):
                break

            logger.error(f"Invalid branch name: {full_branch_name}. Try again?")

        self._git.checkout(parent_branch_name, autostash=autostash)

        self._git.checkout(full_branch_name, new=True, autostash=autostash)


# Normalize a string into a valid segment(ie. the part of the branch name between the /)
def _normalize_git_ref_segment(summary):
    return re.sub(r"[^A-Za-z0-9]+", "-", summary).lower().strip("-")
