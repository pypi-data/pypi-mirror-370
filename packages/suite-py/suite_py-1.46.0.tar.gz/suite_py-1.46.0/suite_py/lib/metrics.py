# -*- encoding: utf-8 -*-
import functools

from suite_py.lib.config import Config
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.metrics_handler import Metrics

_metrics_handler = None


def _metrics() -> Metrics:
    if _metrics_handler:
        return _metrics_handler

    raise RuntimeError(
        "command_executed called before logger.setup(). This is a bug, please report it"
    )


def setup(config: Config, captainhook: CaptainHook):
    global _metrics_handler
    _metrics_handler = Metrics(config=config, captainhook=captainhook)


def command_executed(command):
    _metrics().command_executed(command)


def async_upload():
    _metrics().async_upload()


# Decorator that emits the command_executed metric with the given command name,
# and sets the success paramter to false if the function exited by throwing an error
def command(command: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                _metrics().command_executed(command, success=True)
                return res
            except Exception as e:
                _metrics().command_executed(command, success=False)
                raise e
            # We use sys.exit everywhere, report those
            except SystemExit as e:
                # Report sys.exit(0) and sys.exit() as successes
                success = e.code in (0, None)
                _metrics().command_executed(command, success=success)

                raise e

        return wrapper

    return decorator
