# -*- encoding: utf-8 -*-
import json
import os

import yaml

from suite_py.lib import logger


class Config:
    def __init__(self, home_path=os.environ["HOME"]):
        self.user = {}
        self.youtrack = {}
        self.vault = {}
        self.aws = {}
        self._config_path_file = os.path.join(home_path, ".suite_py/config.yml")
        self._base_cache_path = os.path.join(home_path, ".suite_py/cache")
        self._base_cookie_path = os.path.join(home_path, ".suite_py/cookies")

        if not os.path.exists(self._base_cache_path):
            os.makedirs(self._base_cache_path)
        if not os.path.exists(self._base_cookie_path):
            os.makedirs(self._base_cookie_path)
        self._load()

    def _load(self):
        with open(self._config_path_file, encoding="utf-8") as configfile:
            conf = yaml.safe_load(configfile)

        conf["user"]["projects_home"] = os.path.join(
            os.environ["HOME"], conf["user"]["projects_home"]
        )

        conf["user"].setdefault("review_channel", "#review")
        conf["user"].setdefault("deploy_channel", "#deploy")
        conf["user"].setdefault("default_slug", "PRIMA-XXX")
        default_search = f"in:{conf['user']['default_slug'].split('-')[0]} #{{To Do}}"
        conf["user"].setdefault("card_suggest_query", default_search)
        # This is in seconds
        conf["user"].setdefault("captainhook_timeout", 30)
        conf["user"].setdefault("captainhook_url", "https://captainhook.prima.it")
        conf["user"].setdefault("use_commits_in_pr_body", False)
        conf["user"].setdefault("frequent_reviewers_max_number", 5)

        conf["youtrack"].setdefault("add_reviewers_tags", True)
        conf["youtrack"].setdefault("default_issue_type", "Task")

        conf.setdefault("okta", {})
        conf["okta"].setdefault("base_url", "https://login.helloprima.com/oauth2/v1")
        conf["okta"].setdefault("client_id", "0oaao88cg7kKPJ4GF417")

        _load_local_config(conf)

        for k, v in conf.items():
            setattr(self, k, v)

        # AWS section
        try:
            self.aws = conf["aws"]
        except KeyError:
            pass

    def put_cache(self, key, data):
        key = encode_key_path_safe(key)

        with open(
            os.path.join(self._base_cache_path, key), "w", encoding="utf-8"
        ) as cache_file:
            json.dump(data, cache_file)

    def get_cache(self, key):
        key = encode_key_path_safe(key)

        try:
            with open(
                os.path.join(self._base_cache_path, key), encoding="utf-8"
            ) as cache_file:
                return json.load(cache_file)
        except Exception:
            logger.debug(f"I couldn't find any cached version for the key {key}.")
            return ""
            # sys.exit(-1)

    def put_cookie(self, key, data):
        with open(
            os.path.join(self._base_cookie_path, key), "w", encoding="utf-8"
        ) as cookie_file:
            json.dump(data, cookie_file)

    def get_cookie(self, key, default=None):
        try:
            with open(
                os.path.join(self._base_cookie_path, key), encoding="utf-8"
            ) as cookie_file:
                return json.load(cookie_file)
        except Exception:
            return default
            # sys.exit(-1)


def encode_key_path_safe(key):
    # This can cause conflicts but it shouldn't really happen in real use
    # and this is the easiest way to keep this backwards compatible, so who cares
    return key.replace("/", "_")


def _load_local_config(conf):
    local_conf_path = os.path.join(os.curdir, ".suite_py.yml")
    try:
        with open(local_conf_path, encoding="utf-8") as f:
            local_conf = yaml.safe_load(f)

            for key in conf.keys():
                conf[key].update(local_conf.get(key, {}))

    except FileNotFoundError:
        pass
