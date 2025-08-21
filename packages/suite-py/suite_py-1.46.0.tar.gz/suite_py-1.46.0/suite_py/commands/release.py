# -*- coding: utf-8 -*-
import re
import sys

from suite_py.commands import common
from suite_py.lib import logger, metrics
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.changelog_handler import ChangelogHandler
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.version_handler import DEFAULT_VERSION, VersionHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class Release:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-positional-arguments
    def __init__(self, action, project, captainhook, config, tokens):
        self._action = action
        self._project = project
        self._config = config
        self._tokens = tokens
        self._changelog_handler = ChangelogHandler()
        self._youtrack = YoutrackHandler(config, tokens)
        self._captainhook = captainhook
        self._github = GithubHandler(tokens)
        self._repo = self._github.get_repo(project)
        self._git = GitHandler(project, config)
        self._version = VersionHandler(self._repo, self._git, self._github)

    @metrics.command("release")
    def run(self):
        self._stop_if_prod_locked()
        self._git.fetch()

        if self._action == "create":
            self._create()

    def _stop_if_prod_locked(self):
        request = self._captainhook.status(self._project, "production")
        if request.status_code != 200:
            logger.error("Unable to determine lock status on master.")
            sys.exit(-1)

        request_object = request.json()
        if request_object["locked"]:
            logger.error(
                f"The project is locked in production by {request_object['by']}. Unable to continue."
            )
            sys.exit(-1)

    def _create(self):
        latest = self._version.get_latest_version()

        commits = []
        if latest != "":
            logger.info(f"The current release is {latest}")
            commits = self._github.get_commits_since_release(self._repo, latest)

            _check_migrations_deploy(commits)

            message = "\n".join(
                [
                    "* "
                    + c.commit.message.splitlines()[0]
                    + " by "
                    + c.commit.author.name
                    for c in commits
                ]
            )

            logger.info(f"\nCommits list:\n{message}\n")

            if not prompt_utils.ask_confirm("Do you want to continue?"):
                return

            new_version = self._version.select_new_version(
                latest, allow_prerelease=True
            )

        else:
            # Se non viene trovata la release e non ci sono tag, viene saltato il check delle migrations e l'update delle card su youtrack
            logger.warning(
                f"No tags found, I'm about to push the tag {DEFAULT_VERSION}"
            )
            if not prompt_utils.ask_confirm(
                "Are you sure you want to continue?", default=False
            ):
                sys.exit()
            new_version = DEFAULT_VERSION
            message = f"First release with tag {new_version}"

        if self._changelog_handler.changelog_exists():
            (
                latest_tag,
                latest_entry,
            ) = self._changelog_handler.get_latest_entry_with_tag()

            if latest_tag != new_version:
                if not prompt_utils.ask_confirm(
                    "You didn't update your changelog, are you sure you want to proceed?"
                ):
                    sys.exit()
            else:
                message = f"{latest_entry}\n\n# Commits\n\n{message}"

        message = common.ask_for_release_description(message)
        sha = commits[0].commit.sha if len(commits) > 0 else ""
        self._create_release(new_version, message, sha)

    def _create_release(self, new_version, message, commit):
        new_release = self._repo.create_git_release(
            new_version,
            new_version,
            self._youtrack.replace_card_names_with_md_links(message),
            target_commitish=commit,
        )
        if new_release:
            logger.info(f"The release has been created! Link: {new_release.html_url}")

    def _manage_youtrack_card(self, version, countries):
        release_state = self._config.youtrack["release_state"]

        release_body = self._repo.get_release(version).body

        issue_ids = self._youtrack.get_ids_from_release_body(release_body)

        if len(issue_ids) > 0:
            update_youtrack_state = prompt_utils.ask_confirm(
                f"Do you want to move the associated cards to {release_state} state?",
                default=False,
            )

            for issue_id in issue_ids:
                try:
                    self._youtrack.comment(
                        issue_id,
                        f"Deploy in production of {self._project} in countries {countries} done with the release {version}",
                    )
                    if update_youtrack_state:
                        self._youtrack.update_state(issue_id, release_state)
                        logger.info(f"{issue_id} moved to {release_state}")
                except Exception:
                    logger.warning(
                        f"An error occurred while moving the card {issue_id} to {release_state}"
                    )
                repos_status = self._get_repos_status_from_issue(issue_id)
                if all(r["deployed"] for r in repos_status.values()):
                    try:
                        self._youtrack.update_deployed_field(issue_id)
                        logger.info("Custom field Deployed updated on YouTrack")
                    except Exception:
                        logger.warning(
                            "An error occurred while updating the custom field Deployed"
                        )

    def _get_repos_status_from_issue(self, issue_id):
        regex_pr = r"^PR .* -> https:\/\/github\.com\/primait\/(.*)\/pull\/([0-9]*)$"
        regex_deploy = r"^Deploy in production of (.*) in countries"
        comments = self._youtrack.get_comments(issue_id)
        repos_status = {}

        for c in comments:
            m = re.match(regex_pr, c["text"])
            if m:
                project = m.group(1)
                pr_number = int(m.group(2))
                repos_status[project] = {}
                repos_status[project]["pr"] = pr_number
                repos_status[project]["deployed"] = False
            m = re.match(regex_deploy, c["text"])
            if m:
                project = m.group(1)
                try:
                    repos_status[project]["deployed"] = True
                except Exception:
                    pass
        return repos_status

    def _tags_drifted(self, versions):
        for country, version in versions.items():
            for c, v in versions.items():
                if country == c:
                    continue
                if version is None or v is None or version.compare(v) != 0:
                    return True
        return False


def _check_migrations_deploy(commits):
    if not commits:
        logger.error("ERROR: no commit found")
        sys.exit(-1)
    elif len(commits) == 1:
        files_changed = git.files_changed_between_commits("--raw", f"{commits[0].sha}~")
    else:
        files_changed = git.files_changed_between_commits(
            f"{commits[-1].sha}~", commits[0].sha
        )
    if git.migrations_found(files_changed):
        logger.warning("WARNING: migrations detected in the code")
        if not prompt_utils.ask_confirm(
            "Are you sure you want to continue?", default=False
        ):
            sys.exit()
