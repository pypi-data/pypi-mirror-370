import sys

from suite_py.lib import logger, metrics
from suite_py.lib.handler import prompt_utils
from suite_py.lib.tokens import Tokens


class SetToken:
    def __init__(self, tokens: Tokens):
        self._tokens = tokens

    @metrics.command("set-token")
    def run(self):
        selected = self._select_token()
        if not selected or selected.lower() != selected or selected.strip() != selected:
            # We bail out here, rather than modifying the provided token name, to avoid confusion
            logger.info(
                f'"{selected}" is not a valid token name. Token names must be lowercase and have no trailing whitespace'
            )
            sys.exit(-1)
        new_value = prompt_utils.ask_questions_input(
            f"Insert the new value for {selected}:"
        )
        if not new_value:
            logger.info("Token value cannot be empty")
            sys.exit(-1)
        self._tokens.edit(selected, new_value)
        self._tokens.save()
        logger.info(f"Token {selected} updated")

    def _select_token(self):
        choices = list(self._tokens.keys()) + ["Other..."]
        selected = prompt_utils.ask_choices(
            "Which token do you want to set?", choices, choices[0]
        )

        return (
            self._prompt_custom_token()
            if selected == "Other..."
            else selected.split(" ")[0]
        )

    def _prompt_custom_token(self):
        return prompt_utils.ask_questions_input("Enter custom token name:")
