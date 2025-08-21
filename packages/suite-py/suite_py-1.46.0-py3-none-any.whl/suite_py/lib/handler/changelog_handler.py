# -*- coding: utf-8 -*-
import re
from datetime import datetime
from pathlib import Path
from typing import Iterator, Match, Optional, Tuple

DEFAULT_CHANGELOG_PATH = "CHANGELOG.md"


class ChangelogHandler:
    """
    Manages changelog-related stuff across different commands.
    """

    TAG_REGEX = r"^## \[([0-9]+\.[0-9]+\.[0-9]+)\]( - \d+-\d+-\d+)?"
    UNRELEASED_HEADER_REGEX = r"^## \[Unreleased\]\s*"
    UNRELEASED_VERSION_LINK_REGEX = r"^\[Unreleased\]:\s*.+"

    def __init__(self, changelog_path=DEFAULT_CHANGELOG_PATH) -> None:
        self.changelog_path = Path(changelog_path)

    def bump_changelog(self, repo_html_url, current_version, next_version):
        """
        Updates the changelog by adding the new version header at the top and related link at the bottom.

        Args:
            `repo_html_url`: Url of the repo "for humans" i.e. no the API one
            `current_version`: Version before bump
            `next_version`: Version after bump
        """
        changelog_text = self.changelog_path.read_text("utf-8")
        changelog_text = self._update_version_header(changelog_text, next_version)
        changelog_text = self._update_version_links(
            changelog_text, repo_html_url, current_version, next_version
        )
        self.changelog_path.write_text(changelog_text, "utf-8")

    def get_latest_entry_with_tag(self):
        """
        Gets the latest changelog entry with the respective tag.

        Returns:
            A tuple with `(latest_tag, changelog)`.
        """
        changelog_text = self.changelog_path.read_text("utf-8")
        try:
            tag, content = next(self.get_sections(changelog_text))
            return tag, self._replace_h3_with_h1(content)
        except ValueError:
            return None, None

    def get_sections(self, changelog_text: str) -> Iterator[Tuple[str, str]]:
        """
        Returns an iterator over sections i.e. (tag, content) pairs.
        """
        if not re.search(self.TAG_REGEX, changelog_text, flags=re.MULTILINE):
            raise ValueError("No entries available in the CHANGELOG")

        tags = list(re.finditer(self.TAG_REGEX, changelog_text, flags=re.MULTILINE))
        tags = tags if len(tags) > 1 else [tags[0], None]

        yield from (
            self._extract_tags_and_content(prev_tag, next_tag, changelog_text)
            for prev_tag, next_tag in self._pairwise(tags)
        )

    def changelog_exists(self) -> bool:
        """
        Checks whether the CHANGELOG exists or not.
        """
        return self.changelog_path.exists()

    def _extract_tags_and_content(
        self, prev_tag: Match[str], next_tag: Optional[Match[str]], changelog_text: str
    ):
        tag = prev_tag.group(1)
        content_end = -1

        if next_tag is None:
            start_of_version_links = re.search(
                self.UNRELEASED_VERSION_LINK_REGEX, changelog_text, flags=re.MULTILINE
            )
            content_end = start_of_version_links.start()
        else:
            content_end = next_tag.start()

        content = changelog_text[prev_tag.end() : content_end].strip()
        return tag, content

    def _pairwise(self, l: list):
        yield from zip(l, l[1:])

    def _replace_h3_with_h1(self, line: str) -> str:
        return re.sub("^###", "#", line, flags=re.MULTILINE)

    def _update_version_header(self, changelog_text: str, next_version: str) -> str:
        today = datetime.today().strftime("%Y-%m-%d")
        new_version_header = (
            "## [Unreleased]\n\n" "---\n\n" f"## [{next_version}] - {today}\n\n"
        )
        return re.sub(
            self.UNRELEASED_HEADER_REGEX,
            new_version_header,
            changelog_text,
            flags=re.MULTILINE,
        )

    def _update_version_links(
        self,
        changelog_text: str,
        repo_html_url: str,
        current_version: str,
        next_version: str,
    ) -> str:
        if (
            re.search(
                self.UNRELEASED_VERSION_LINK_REGEX, changelog_text, flags=re.MULTILINE
            )
            is not None
        ):
            new_version_links = (
                f"\n[Unreleased]: {repo_html_url}/compare/{next_version}...HEAD"
                f"\n[{next_version}]: {repo_html_url}/compare/{current_version}...{next_version}"
            )

            return re.sub(
                self.UNRELEASED_VERSION_LINK_REGEX,
                new_version_links,
                changelog_text,
                flags=re.MULTILINE,
            )

        starting_version_links = (
            f"\n[Unreleased]: {repo_html_url}/compare/{next_version}...HEAD"
            f"\n[{next_version}]: {repo_html_url}/releases/tag/{next_version}\n"
        )
        return changelog_text + starting_version_links
