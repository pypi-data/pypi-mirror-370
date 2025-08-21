#! -*- encoding: utf-8 -*-

# We import command modules inside their respective function bodies
# for performance reasons, so turn off the lint warning
# pylint: disable=import-outside-toplevel

# We need to inject truststore code before we do any libraries
# that might end up creating an ssl.SSlContext object
# pylint: disable=wrong-import-position

import sys


def maybe_inject_truststore() -> None:
    """
    Injects the truststore package into the system ssl store, to fix verficiation certificate issues when using warp.
    """
    if sys.version_info >= (3, 10):
        import truststore

        truststore.inject_into_ssl()
    else:
        # pylint: disable-next=reimported
        from suite_py.lib import logger

        logger.warning(
            "Your python version is older than 3.10 and doesn't support the truststore package. You might experience issues with certificate verification when connected to the warp VPN.\nPlease update to python 3.10 or newer"
        )


# Needs to be done before any other imports
maybe_inject_truststore()

import os
from functools import wraps
from importlib.metadata import PackageNotFoundError, version
from typing import Optional

import click
import requests
from click.exceptions import ClickException

from suite_py.__version__ import __version__
from suite_py.commands.context import Context
from suite_py.lib import logger, metrics
from suite_py.lib.config import Config
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.okta_handler import Okta
from suite_py.lib.handler.pre_commit_handler import PreCommit
from suite_py.lib.tokens import Tokens

# pylint: enable=wrong-import-position

ALLOW_NO_GIT_SUBCOMMAND = ["check", "set-token", "login"]
ALLOW_NO_HOME_SUBCOMMAND = ["check", "set-token", "login"]


def fetch_latest_version() -> Optional[str]:
    """
    Fetches the latest version of suite-py as a str
    Returns None on error
    """
    try:
        # pylint: disable-next=missing-timeout
        pkg_info = requests.get("https://pypi.org/pypi/suite-py/json").json()
        return pkg_info["info"]["version"]
    except Exception:
        logger.warning("Failed to fetch latest version of suite-py!")
        return None


def upgrade_suite_py_if_needed(break_on_missing_package: bool = False) -> None:
    """
    Sometimes, when `suite-py` is launched with a virtual environment active, autoupgrade
    cannot see the package as installed (as the command is used from the "global" user environment)
    and raises an exception.
    """

    try:
        installed_version = version("suite_py")
    except PackageNotFoundError as error:
        # We are in a virtual environment where suite-py is not installed, don't bother trying to upgrade
        if break_on_missing_package:
            raise error

        logger.warning(
            "Skipping Suite-Py autoupgrade because the package was not found in the current environment."
        )
        return

    try:
        # If available, upgrade (if needed)
        latest_version = fetch_latest_version()
        if latest_version is None or latest_version > installed_version:
            from autoupgrade import Package

            # If we fail to fetch the latest version, fallback to attempting the upgrade anyway
            Package("suite_py").upgrade()
    except Exception as error:
        logger.warning(f"An error occurred whilst trying to upgrade suite-py: {error}")


# Catches any exceptions thrown and turns them into a ClickException
# So they don't print a stacktrace
def catch_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Ignore all exception classes from the click module
            if type(e).__module__.startswith("click."):
                raise e

            logger.debug("An error occured:", exc_info=True)
            raise ClickException(f"{str(e)}. rerun with -v for more details") from e

    return wrapper


@click.group()
@click.option(
    "--project",
    type=click.Path(exists=True),
    default=os.getcwd(),
    help="Path of the project to run the command on (the default is current directory)",
)
@click.option(
    "--timeout",
    type=click.INT,
    help="Timeout in seconds for Captainhook operations",
)
@click.option("-v", "--verbose", count=True)
@click.pass_context
@catch_exceptions
def main(ctx, project, timeout, verbose):
    config = Config()

    logger.setup(verbose)

    logger.debug(f"v{__version__}")
    maybe_inject_truststore()
    upgrade_suite_py_if_needed(break_on_missing_package=False)

    if ctx.invoked_subcommand not in ALLOW_NO_GIT_SUBCOMMAND:
        project = git.get_root_folder(project)

    if ctx.invoked_subcommand not in ALLOW_NO_GIT_SUBCOMMAND and not git.is_repo(
        project
    ):
        raise ClickException(f"the folder {project} is not a git repo")

    if ctx.invoked_subcommand not in ALLOW_NO_HOME_SUBCOMMAND and not os.path.basename(
        project
    ) in os.listdir(config.user["projects_home"]):
        raise ClickException(
            f"the folder {project} is not in {config.user['projects_home']}"
        )

    skip_confirmation = False
    if type(config.user.get("skip_confirmation")).__name__ == "bool":
        skip_confirmation = config.user.get("skip_confirmation")
    elif type(
        config.user.get("skip_confirmation")
    ).__name__ == "list" and ctx.invoked_subcommand in config.user.get(
        "skip_confirmation"
    ):
        skip_confirmation = True

    if not skip_confirmation and not prompt_utils.ask_confirm(
        f"Do you want to continue on project {os.path.basename(project)}?"
    ):
        ctx.exit()
    if timeout:
        config.user["captainhook_timeout"] = timeout

    project = os.path.basename(project)
    tokens = Tokens()
    okta = Okta(config, tokens)
    captainhook = CaptainHook(config, okta, tokens)

    ctx.obj = Context(
        project=project,
        tokens=tokens,
        okta=okta,
        config=config,
        captainhook=captainhook,
    )

    ctx.obj.call(metrics.setup)

    # Skip chdir if not needed
    if (
        ctx.invoked_subcommand not in ALLOW_NO_GIT_SUBCOMMAND
        or ctx.invoked_subcommand not in ALLOW_NO_HOME_SUBCOMMAND
    ):
        os.chdir(os.path.join(config.user["projects_home"], ctx.obj.project))
    # Warn on missing pre_commit hook
    if ctx.invoked_subcommand not in ALLOW_NO_GIT_SUBCOMMAND:
        ctx.obj.call(PreCommit).check_and_warn()


@main.result_callback()
@click.pass_obj
def cleanup(_obj, _, **_kwargs):
    metrics.async_upload()


@main.command("bump", help="Bumps the project version based on the .versions.yml file")
@click.option("--project", required=False, type=str)
@click.option(
    "--version",
    required=False,
    type=str,
    help="Version to apply. If not passed, you will be prompted to insert or select one from a predefined list",
)
@click.pass_obj
@catch_exceptions
def bump(obj: Context, project: Optional[str] = None, version: Optional[str] = None):
    from suite_py.commands.bump import Bump

    obj.call(Bump).run(project=project, version=version)


@main.command(
    "create-branch", help="Create local branch and set the YouTrack card in progress"
)
@click.option("--card", type=click.STRING, help="YouTrack card number (ex. PRIMA-123)")
@click.option(
    "--autostash",
    is_flag=True,
    help="Stash uncommitted changes before creating the branch and reapply them afterward",
)
@click.pass_obj
@catch_exceptions
def cli_create_branch(obj, card, autostash):
    from suite_py.commands.create_branch import CreateBranch

    obj.call(CreateBranch, card=card, autostash=autostash).run()


@main.command("lock", help="Lock project on staging or prod")
@click.argument(
    "environment", type=click.Choice(("staging", "production", "deploy", "merge"))
)
@click.pass_obj
@catch_exceptions
def cli_lock_project(obj, environment):
    from suite_py.commands.project_lock import ProjectLock

    obj.call(ProjectLock, env=environment, action="lock").run()


@main.command("unlock", help="Unlock project on staging or prod")
@click.argument(
    "environment", type=click.Choice(("staging", "production", "deploy", "merge"))
)
@click.pass_obj
@catch_exceptions
def cli_unlock_project(obj, environment):
    from suite_py.commands.project_lock import ProjectLock

    obj.call(ProjectLock, env=environment, action="unlock").run()


@main.command(
    "estimate-cone",
    help="Point-in-time estimate of the time needed to complete all unresolved children of a card using the Cone of Uncertainty",
)
@click.option("--issue", prompt="Issue ID", type=str)
@click.option("--sprint-board", prompt="Sprint Board ID", type=str)
@click.option("--previous-sprints", required=False, type=int, default=6)
@click.pass_obj
@catch_exceptions
def estimate_cone(
    obj: Context,
    issue: Optional[str],
    sprint_board: Optional[str],
    previous_sprints: int,
):
    from suite_py.commands.estimate_cone import EstimateCone

    obj.call(EstimateCone).run(
        issue=issue, sprint_board=sprint_board, previous_sprints=previous_sprints
    )


@main.command("open-pr", help="Open a PR on GitHub")
@click.pass_obj
@catch_exceptions
def cli_open_pr(obj):
    from suite_py.commands.ask_review import AskReview
    from suite_py.commands.open_pr import OpenPR

    ask_review = obj.call(AskReview)
    obj.call(OpenPR, ask_review=ask_review).run()


@main.command("ask-review", help="Requests a PR review")
@click.pass_obj
@catch_exceptions
def cli_ask_review(obj):
    from suite_py.commands.ask_review import AskReview

    obj.call(AskReview).run()


@main.command(
    "merge-pr", help="Merge the selected branch to master if all checks are OK"
)
@click.pass_obj
@catch_exceptions
def cli_merge_pr(obj):
    from suite_py.commands.merge_pr import MergePR

    obj.call(MergePR).run()


@main.group("release", help="Manage releases")
def release():
    pass


@release.command(
    "create", help="Create a github release (and deploy it if GHA are used)"
)
@click.pass_obj
@catch_exceptions
def cli_release_create(obj):
    from suite_py.commands.release import Release

    obj.call(Release, action="create").run()


@main.command("status", help="Current status of a project")
@click.pass_obj
@catch_exceptions
def cli_status(obj):
    from suite_py.commands.status import Status

    obj.call(Status).run()


@main.command("check", help="Verify authorisations for third party services")
@click.pass_obj
@catch_exceptions
def cli_check(obj):
    from suite_py.commands.check import Check

    obj.call(Check).run()


@main.command("login", help="Manage login against Okta")
@click.pass_obj
@catch_exceptions
def login(obj):
    from suite_py.commands.login import Login

    obj.call(Login).run()


@main.command("set-token", help="Create or update a service token")
@click.pass_obj
@catch_exceptions
def cli_set_token(obj):
    from suite_py.commands.set_token import SetToken

    obj.call(SetToken).run()
