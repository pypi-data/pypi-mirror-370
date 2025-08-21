import dataclasses
from typing import Dict, List, Literal, Optional

import semver
from halo import Halo

from suite_py.lib import logger
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.github_handler import GithubHandler, GitRelease, Repository

VersionPart = Literal["major", "minor", "patch", "prerelease", "build"]
DEFAULT_VERSION = "0.1.0"
PRERELEASE_OPTIONS = sorted(["rc", "dev", "pre", "alpha", "beta"])


@dataclasses.dataclass
class VersionHandler:
    """
    Manages version-related stuff across different commands.
    """

    _repo: Repository
    _git: git.GitHandler
    _github: GithubHandler

    def select_new_version(
        self,
        current_version: str,
        allow_prerelease: bool = False,
        allow_custom_version: bool = False,
    ) -> str:
        """
        Asks the user for a new semantic version.

        Args:
            current_version: The current project version (for static bumping options)
            allow_prerelease: Whether to give the user the option customize prerelease and build.

        Returns:
            A tuple in the form (selected_part, selected_version).
        """
        bump_options = self.get_bump_options(
            current_version, allow_prerelease, allow_custom_version
        )
        selected_version = prompt_utils.ask_choices("Select version:", bump_options)

        if allow_prerelease and selected_version == "prerelease":
            return self.prompt_prerelease_version(current_version)
        if allow_custom_version and selected_version == "custom":
            return self.prompt_custom_version()
        return selected_version

    def prompt_prerelease_version(self, current_version: str) -> str:
        """
        Asks the user to specify a release token to be used.
        """
        pre_token = prompt_utils.ask_choices(
            "Select prerelease token:", self.get_prerelease_token_options()
        )
        choices = {
            "Major-pre": Bumper.bump_prerelease(
                Bumper.bump_major(current_version), token=pre_token
            ),
            "Minor-pre": Bumper.bump_prerelease(
                Bumper.bump_minor(current_version), token=pre_token
            ),
            "Patch-pre": Bumper.bump_prerelease(
                Bumper.bump_patch(current_version), token=pre_token
            ),
            "Only pre ": Bumper.bump_prerelease(current_version, token=pre_token),
        }

        return prompt_utils.ask_choices(
            "Select next version token:",
            [
                {"name": f"{key} - {value}", "value": value}
                for key, value in choices.items()
            ],
        )

    def prompt_custom_version(self) -> str:
        """
        Asks the user to input a custom semantic version.
        """
        version = prompt_utils.ask_questions_input("Please type a semantic version:")
        while not self.is_valid_semver(version):
            version = prompt_utils.ask_questions_input(
                "Please type a semantic version:"
            )
        return version

    @staticmethod
    def is_valid_semver(version: str) -> bool:
        try:
            semver.VersionInfo.parse(version)
            return True
        except ValueError:
            logger.error(f"The string {version} is not a valid semantic version.")
            return False

    def get_bump_options(
        self, current_version: str, allow_prerelease: bool, allow_custom_version: bool
    ) -> List[Dict[str, str]]:
        """
        Returns a dict of bump alternatives from `current_version`.

        Args:
            current_version: The current project version.

        Returns:
            The mapping between the version part to be bumped and the resulting version.
        """
        options = [
            ("Patch", Bumper.bump_patch(current_version), None),
            ("Minor", Bumper.bump_minor(current_version), None),
            ("Major", Bumper.bump_major(current_version), None),
        ]
        if allow_prerelease:
            options.append(
                ("Prerelease", "prerelease", f"({', '.join(PRERELEASE_OPTIONS)})")
            )
        if allow_custom_version:
            options.append(("Custom", "custom", "(input a semantic version)"))
        return [
            {"name": f"{name} {desc or value}", "value": value}
            for name, value, desc in options
        ]

    def get_prerelease_token_options(self) -> List[Dict[str, str]]:
        return [{"name": token, "value": token} for token in PRERELEASE_OPTIONS]

    def get_latest_version(self) -> str:
        """
        Retrieves the latest project version using GitHub.

        Returns:
            The latest project version.
        """
        tags = self._repo.get_tags()
        tag = git.get_last_tag_number(tags)
        latest_release = self.get_release(tag)
        current_version = latest_release.tag_name if latest_release else tag
        return current_version or ""

    def get_release(self, tag: str) -> Optional[GitRelease]:
        """
        Retrieves the latest release from GitHub.
        """
        with Halo(text="Loading...", spinner="dots", color="magenta"):
            latest_release = self._github.get_latest_release_if_exists(self._repo)
            if latest_release and latest_release.title == tag:
                return latest_release
        return None


class Bumper:
    """
    Wraps SemVer to bump versions in various ways.
    """

    @staticmethod
    def bump_major(version: str) -> str:
        version_info = Bumper._parse_version(version)
        return str(version_info.bump_major())

    @staticmethod
    def bump_minor(version: str) -> str:
        version_info = Bumper._parse_version(version)
        return str(version_info.bump_minor())

    @staticmethod
    def bump_patch(version: str) -> str:
        version_info = Bumper._parse_version(version)
        return str(version_info.bump_patch())

    @staticmethod
    def bump_prerelease(version: str, token: str = "rc") -> str:
        version_info = Bumper._parse_version(version)
        new_version = str(version_info.bump_prerelease(token=token))
        if version_info.prerelease is None or f"{token}" not in version_info.prerelease:
            # Makes the first prerelease start from .0 instead of .1
            return new_version[:-2] + ".0"
        return new_version

    @staticmethod
    def bump_build(version: str, token: str = "build") -> str:
        version_info = Bumper._parse_version(version)
        return str(version_info.bump_build(token=token))

    @staticmethod
    def _parse_version(version: str) -> semver.VersionInfo:
        return semver.VersionInfo.parse(version)
