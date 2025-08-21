import os

import yaml

from suite_py.lib import logger
from suite_py.lib.config import Config
from suite_py.lib.handler.git_handler import GitHandler


class PreCommit:
    """
    Handler checking whether the user has the prima pre-commit hooks setup and print a warning if they are missing
    """

    def __init__(self, project: str, config: Config):
        self._git = GitHandler(project, config)

    def check_and_warn(self):
        if self.is_enabled() and not self.is_pre_commit_hooks_installed():
            self.warn_missing_pre_commit_hook()

    def is_pre_commit_hooks_installed(self):
        """
        Apply some heuteristics to check whether the gitleaks pre-commit hook is installed.
        This is extremely imperfect, and only supports direct calls in shell scripts.
        More hooks, like husky should be added later
        """
        return self.is_vanilla_hook_setup() or self.is_pre_commit_py_hook_setup()

    def warn_missing_pre_commit_hook(self):
        logger.warning(
            """
Looks like the current repo is missing the gitleaks pre-commit hook!
Please install it per the security guide:
https://www.notion.so/helloprima/Install-Gitleaks-pre-commit-hook-aaaa6beafafa4c298b537afcb52bb25a

If you have installed them already you can report the false positive to team-platform-shared-services (on Slack) and run:
    git config suite-py.disable-pre-commit-warning true
to disable the check for this repo, or
    git config --global suite-py.disable-pre-commit-warning true
to disable it globally
        """
        )

    def is_vanilla_hook_setup(self):
        """
        Check whether the gitleaks hook is setup as a regular bash script
        """
        pre_commit_file = self.read_pre_commit_hook()

        # Assume everything is a shell script.
        # Technically you could use a binary, or even python code,
        # But those are out of scope for us, and the user should just disable the warning themselves
        lines = pre_commit_file.splitlines()

        # Filter out lines that start with '#' since those are probably just comments.
        without_comments = filter(lambda l: not l.strip().startswith("#"), lines)

        return any("gitleaks" in line for line in without_comments)

    def is_pre_commit_py_hook_setup(self):
        """
        Check whether the gitleaks hook is setup with the pre-commit python framework
        """
        # If the framework is not setup skip
        if "pre-commit" not in self.read_pre_commit_hook():
            logger.debug("pre-commit.com not installed, skipping config check")
            return False

        config_path = os.path.join(self._git.get_path(), ".pre-commit-config.yaml")
        try:
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.debug("pre-commit config file(%s) not found", config_path)
            return False
        except yaml.YAMLError:
            logger.warning(".pre-commit-config.yaml file is invalid!", exc_info=True)
            return False

        return any(
            repo.get("repo", "") == "git@github.com:primait/security-hooks.git"
            for repo in config.get("repos", [])
        )

    def read_pre_commit_hook(self):
        pre_commit_file_path = os.path.join(self._git.hooks_path(), "pre-commit")
        logger.debug("Reading pre-commit script from %s", pre_commit_file_path)
        try:
            with open(pre_commit_file_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def is_enabled(self):
        return self._git.get_git_config("suite-py.disable-pre-commit-warning") != "true"
