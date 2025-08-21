# -*- encoding: utf-8 -*-
import inquirer
from InquirerPy import prompt


def ask_confirm(text, default=True):
    questions = [
        {"type": "confirm", "message": text, "name": "continue", "default": default}
    ]
    answer = prompt(questions)
    return bool(answer["continue"])


def ask_questions_input(question_text, default_text=""):
    questions = [
        {
            "type": "input",
            "name": "value",
            "message": question_text,
            "default": default_text,
        }
    ]

    answer = prompt(questions)
    return answer["value"]


def ask_questions_editor(question_text, default_text=""):
    questions = [
        inquirer.Editor(
            "value",
            message=question_text,
            default=default_text,
        )
    ]

    answer = inquirer.prompt(questions)
    return answer["value"]


def ask_choices(question_text, choices, default_text=""):
    questions = [
        {
            "type": "list",
            "name": "value",
            "message": question_text,
            "choices": choices,
            "default": default_text,
        }
    ]

    answer = prompt(questions)
    return answer["value"]


def ask_multiple_choices(question_text, choices):
    questions = [
        {
            "type": "checkbox",
            "name": "values",
            "message": question_text,
            "choices": [
                {"name": choice, "value": choice, "enabled": False}
                for choice in choices
            ],
        }
    ]

    answer = prompt(questions)
    return answer["values"]


def checkbox_with_manual_fallback(msg, choices, autocomplete=None):
    question = inquirer.Checkbox(
        "value",
        msg,
        choices,
        other=True,
        autocomplete=autocomplete,
    )
    answer = inquirer.prompt([question])["value"]
    if not answer:
        question = inquirer.Text(
            "value",
            msg,
            autocomplete=autocomplete,
        )
        answer = [inquirer.prompt([question])["value"]]

    return answer


def make_completer(comprehension):
    """
    Builds an inquirer completer for the given list generator. The generator
    should consume a string and return a list of strings for auto-complete suggestion
    """

    def _completer(text, state):
        options = comprehension(text)
        try:
            return options[state]
        except IndexError:
            return None

    return _completer
