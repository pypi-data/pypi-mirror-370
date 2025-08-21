# -*- encoding: utf-8 -*-
import logging

from rich.logging import RichHandler

# Rich handles color and formatting internally
# This format will make it so we print stuff like "[I] message"
LOG_FORMAT = "%(message)s"

LOGGER_NAME = "suite_py_logger"


def setup(verbose):
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=False, show_path=False)],
    )

    logger = logging.getLogger(LOGGER_NAME)
    logger.debug("Logging as %s", level)


def debug(message, *args, **kwargs):
    logging.getLogger(LOGGER_NAME).debug(message, *args, **kwargs)


def info(message, *args, **kwargs):
    logging.getLogger(LOGGER_NAME).info(message, *args, **kwargs)


def warning(message, *args, **kwargs):
    logging.getLogger(LOGGER_NAME).warning(message, *args, **kwargs)


def error(message, *args, **kwargs):
    logging.getLogger(LOGGER_NAME).error(message, *args, **kwargs)
