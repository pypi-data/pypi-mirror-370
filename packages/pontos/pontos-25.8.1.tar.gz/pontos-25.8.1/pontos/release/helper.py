# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Optional

from pontos.enum import StrEnum
from pontos.git import Git, GitError
from pontos.terminal import Terminal
from pontos.version import Version, VersionCalculator, VersionError

DEFAULT_TIMEOUT = 1000
DEFAULT_CHUNK_SIZE = 4096


class ReleaseType(StrEnum):
    """
    Type of the release. Used to determine the next release version.

    Attributes:
        PATCH: A patch version release (1.2.x)
        CALENDAR: A calendar versioning release (year.month.X)
        VERSION: The version is explicitly set
        MAJOR: A major version release (x.0.0)
        MINOR: A minor version release (1.x.0)
        ALPHA: A alpha version release
        BETA: A beta version release
        RELEASE_CANDIDATE: A release candidate
    """

    PATCH = "patch"
    CALENDAR = "calendar"
    VERSION = "version"
    MAJOR = "major"
    MINOR = "minor"
    ALPHA = "alpha"
    BETA = "beta"
    RELEASE_CANDIDATE = "release-candidate"


def get_git_repository_name(
    remote: str = "origin",
) -> str:
    """Get the git repository name

    Arguments:
        remote: the remote to look up the name (str) default: origin

    Returns:
        The git project name
    """

    ret = Git().remote_url(remote)
    return ret.rsplit("/", maxsplit=1)[-1].replace(".git", "").strip()


def find_signing_key(terminal: Terminal) -> str:
    """Find the signing key in the config

    Arguments:
        terminal: The terminal for console output

    Returns:
        git signing key or empty string
    """

    try:
        return Git().config("user.signingkey").strip()
    except GitError as e:
        # The command `git config user.signingkey` returns
        # return code 1 if no key is set.
        # So we will return empty string ...
        if e.returncode == 1:
            terminal.warning("No signing key found.")
        return ""


def get_next_release_version(
    *,
    last_release_version: Optional[Version],
    calculator: type[VersionCalculator],
    release_type: ReleaseType,
    release_version: Optional[Version],
) -> Version:
    if release_version:
        if release_type and release_type != ReleaseType.VERSION:
            raise VersionError(
                f"Invalid release type {release_type.value} when setting "
                "release version explicitly. Use release type version instead."
            )

        return release_version
    else:
        if not release_type or release_type == ReleaseType.VERSION:
            raise VersionError(
                "No release version provided. Either use a different release "
                "type or provide a release version."
            )

    if not last_release_version:
        raise VersionError(
            "No last release version found for release type "
            f"{release_type.value}. Either check the project setup or set a "
            "release version explicitly."
        )

    if release_type == ReleaseType.CALENDAR:
        return calculator.next_calendar_version(last_release_version)

    if release_type == ReleaseType.PATCH:
        return calculator.next_patch_version(last_release_version)

    if release_type == ReleaseType.MINOR:
        return calculator.next_minor_version(last_release_version)

    if release_type == ReleaseType.MAJOR:
        return calculator.next_major_version(last_release_version)

    if release_type == ReleaseType.ALPHA:
        return calculator.next_alpha_version(last_release_version)

    if release_type == ReleaseType.BETA:
        return calculator.next_beta_version(last_release_version)

    if release_type == ReleaseType.RELEASE_CANDIDATE:
        return calculator.next_release_candidate_version(last_release_version)

    raise VersionError(f"Unsupported release type {release_type.value}.")


def repository_split(repository: str) -> tuple[str, str]:
    """
    Split a GitHub repository (owner/name) into a space, project tuple
    """
    splitted_repo = repository.split("/")
    if len(splitted_repo) != 2:
        raise ValueError(
            f"Invalid repository {repository}. Format must be " "owner/name."
        )
    return splitted_repo[0], splitted_repo[1]
