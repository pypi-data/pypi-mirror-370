# -*- encoding: utf-8 -*-

import multiprocessing
import os
import platform
from typing import Optional

from suite_py.lib import logger
from suite_py.lib.config import Config
from suite_py.lib.handler.captainhook_handler import CaptainHook


# Collects metrics and sends them to datadog through captainhook
class Metrics:
    def __init__(self, captainhook: CaptainHook, config: Config):
        self._captainhook = captainhook
        self._config = config

    # Emits the command_executed metric
    def command_executed(self, command: str, success: Optional[bool] = True):
        metric_data = {
            "type": "command_executed",
            "os": platform.system(),
            "command": command,
            "success": success,
        }

        self._create_metric(metric_data)

    def _create_metric(self, metric):
        # Instead of trying to submit metrics all at once first we save them to a file first
        # That way we can batch metric submissions and retry them if they fail (eg. because the user isn't authenticated with okta)
        metrics = self._config.get_cookie("metrics", [])
        if not isinstance(metrics, list):
            logger.warning(
                f"Metrics cookie is not a list! Replacing {metrics} with an empty list"
            )
            metrics = []

        logger.debug(f"creating metric: {metric}")
        if self._config.user.get("disable_metrics_creation", False):
            logger.debug("skipping metric creation")
        else:
            metrics.append(metric)
            self._config.put_cookie("metrics", metrics)

    # Upload metrics in a detached background process
    def async_upload(self):
        # Double fork to detach the process
        def child():
            if (
                # Windows doesn't support forking.
                # There aren't any windows users that we know of so we can just block application exit
                # If windows users appear we should fix this
                os.name == "posix"
                and
                # Forking here is safe since we are running in a fresh process spawned by multiprocessing
                os.fork() != 0
            ):
                return

            self.upload()

        # Fall back to a sync upload if async fails
        try:
            p = multiprocessing.Process(target=child)
            p.start()
            p.join()
        except Exception:
            logger.debug(
                "Error uploading metrics asynchronously, trying sync:", exc_info=True
            )
            self.upload()

    def upload(self):
        metrics = self._config.get_cookie("metrics", [])
        # Prevent double uploads
        #
        # This isn't atomic and could still lead to the same metrics being uploaded twice
        # but this occuring is unlikely enough that it shouldn't significantly influence our stats
        self._config.put_cookie("metrics", [])
        try:
            if len(metrics) != 0:
                self._captainhook.send_metrics(metrics)
        except Exception:
            # Upload failed, try again later
            self._config.put_cookie("metrics", metrics)
