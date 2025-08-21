"""
Module for interacting with git through the CLI
"""

import logging
from pathlib import Path

from pydantic import BaseModel

from iccore.system import process
from iccore.project import version

logger = logging.getLogger(__name__)


class GitUser(BaseModel):
    """
    A git user
    """

    name: str = ""
    email: str = ""


class GitRemote(BaseModel):
    """
    A git remote
    """

    url: str = ""
    name: str = "origin"


class GitRepo(BaseModel):
    """
    Representation of a git repository, including methods for querying and modifying
    repo contents.
    """

    user: GitUser
    remotes: list[GitRemote] = []
    path: Path


def init_repo(repo_dir: Path) -> str:
    """
    Run git init in the repo
    """
    cmd = "git init ."
    return process.run(cmd, repo_dir)


def _get_user_email(repo_dir: Path) -> str:
    """
    Return the user's email for the given repo
    """
    cmd = "git config user.email"
    return process.run(cmd, repo_dir, is_read_only=True).strip()


def _get_user_name(repo_dir: Path) -> str:
    """
    Get the git user's name
    """
    cmd = "git config user.name"
    return process.run(cmd, repo_dir, is_read_only=True).strip()


def get_user(repo_dir: Path) -> GitUser:
    """
    Get the git user
    """

    email = _get_user_email(repo_dir)
    name = _get_user_name(repo_dir)
    return GitUser(**{"name": name, "email": email})


def get_remotes(repo_dir: Path) -> list[GitRemote]:
    """
    Return the repo's remotes
    """
    cmd = "git remote"

    return [
        GitRemote(**{"name": n})
        for n in process.run(cmd, repo_dir, is_read_only=True).splitlines()
    ]


def get_repo_info(repo_dir: Path) -> GitRepo:
    """
    Get the repo info as an object
    """
    return GitRepo(
        user=get_user(repo_dir), remotes=get_remotes(repo_dir), path=repo_dir
    )


def add_remote(repo_dir: Path, remote: GitRemote):
    """
    Add a remote to the repo
    """
    logger.info("Adding remote with name %s and url %s", remote.name, remote.url)
    cmd = f"git remote add {remote.name} {remote.url}"
    process.run(cmd, repo_dir)


def get_changed_files(repo_dir: Path) -> list[str]:
    cmd = "git diff --name-only"
    result = process.run(cmd, repo_dir, is_read_only=True)
    return result.splitlines()


def has_tags(repo_dir: Path) -> bool:
    cmd = "git tag -l"
    # Result will be empty string if no tags
    return bool(process.run(cmd, repo_dir, is_read_only=True))


def get_latest_tag_on_branch(repo_dir: Path) -> str:
    if not has_tags(repo_dir):
        return ""

    cmd = "git describe --tags --abbrev=0"
    return process.run(cmd, repo_dir, is_read_only=True).strip()


def get_branch(repo_dir: Path) -> str:
    cmd = "git branch --show-current"
    return process.run(cmd, repo_dir, is_read_only=True)


def push_tags(repo_dir: Path, remote: str = "origin"):
    cmd = f"git push --tags {remote}"
    process.run(cmd, repo_dir)


def set_tag(repo_dir: Path, tag: str):
    cmd = f"git tag {tag}"
    process.run(cmd, repo_dir)


def _set_user_email(repo_dir: Path, email: str):
    cmd = f"git config user.email {email}"
    process.run(cmd, repo_dir)


def _set_user_name(repo_dir: Path, name: str):
    cmd = f"git config user.name {name}"
    process.run(cmd, repo_dir)


def set_user(repo_dir: Path, user: GitUser):
    """
    Set the user on the git repo
    """
    logger.info("Setting user name: %s and email: %s", user.name, user.email)
    _set_user_email(repo_dir, user.email)
    _set_user_name(repo_dir, user.name)


def add_all(repo_dir: Path):
    cmd = "git add ."
    process.run(cmd, repo_dir)


def commit(repo_dir: Path, message: str):
    cmd = f'git commit -m "{message}"'
    process.run(cmd, repo_dir)


def push(
    repo_dir: Path,
    remote: str = "origin",
    src: str = "HEAD",
    dst: str = "main",
    extra_args: str = "",
):
    """
    Push the current git state to the remote
    """
    cmd = f"git push {remote} {src}:{dst} {extra_args}"
    process.run(cmd, repo_dir)


def switch_branch(repo_dir: Path, target_branch: str):
    cmd = f"git checkout {target_branch}"
    return process.run(cmd, repo_dir)


def get_tag_commit(repo_dir: Path, tag: str) -> str:
    cmd = f"git rev-list -n 1 {tag}"
    return process.run(cmd, repo_dir)


def get_head_commit(repo_dir: Path) -> str:
    cmd = "git rev-parse HEAD"
    return process.run(cmd, repo_dir)


def increment_tag(
    repo_dir: Path,
    version_scheme: str = "semver",
    field: str = "patch",
    branch="main",
    check: bool = False,
    remote: str | None = None,
    push: bool = True,
):
    """
    Given a local repo, a versioning schema and field
    increment the current git tag and push it to the
    given remote.
    """

    current_branch = get_branch(repo_dir)
    if current_branch != branch:
        switch_branch(repo_dir, branch)

    latest_tag = get_latest_tag_on_branch(repo_dir)

    repo_version = version.parse(latest_tag, version_scheme)
    logger.info("Current tag is: %s", repo_version.as_string())

    if check:
        tag_commit = get_tag_commit(repo_dir, latest_tag)
        head_commit = get_head_commit(repo_dir)
        if tag_commit == head_commit:
            logger.info("No new commits found on branch: %s.", branch)
            return

    repo_version = version.increment(repo_version, field)
    logger.info("Updating tag to: %s", repo_version.as_string())
    set_tag(repo_dir, repo_version.as_string())

    if not push:
        return

    if remote:
        working_remote = remote
    else:
        remotes = get_remotes(repo_dir)
        working_remote = remotes[-1].name
    logger.info("Setting remote to: %s", working_remote)
    push_tags(repo_dir, working_remote)
