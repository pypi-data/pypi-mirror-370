from suite_py.lib import logger
from suite_py.lib.handler import prompt_utils


def ask_for_release_description(message):
    if not prompt_utils.ask_confirm(
        "Do you want to edit the release description?", default=False
    ):
        return message

    description = prompt_utils.ask_questions_editor(
        question_text="Enter the release description: ", default_text=message
    )

    if description == "":
        logger.warning("The release description cannot be empty")
        return ask_for_release_description(message)

    return description
