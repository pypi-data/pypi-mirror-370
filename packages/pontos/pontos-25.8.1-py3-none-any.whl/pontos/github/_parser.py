# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Argument parser for pontos-github"""

import os
from argparse import ArgumentParser, FileType, Namespace
from pathlib import Path
from typing import Optional, Sequence

import shtab

from pontos.enum import enum_choice, enum_type
from pontos.github.cmds import (
    create_pull_request,
    create_release,
    create_tag,
    file_status,
    labels,
    pull_request,
    release,
    repos,
    tag,
    update_pull_request,
)
from pontos.github.models.base import FileStatus
from pontos.github.models.organization import RepositoryType

body_template = Path(__file__).parent / "pr_template.md"


def from_env(name: str) -> str:
    return os.environ.get(name, name)


def parse_args(args: Optional[Sequence[str]] = None) -> Namespace:
    """
    Parsing args for Pontos GitHub

    Arguments:
        args        The program arguments passed by exec
    """

    parser = ArgumentParser(
        description="Greenbone GitHub API.",
    )
    shtab.add_argument_to(parser)
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Don't print messages to the terminal",
    )

    parser.add_argument(
        "--log-file",
        dest="log_file",
        type=str,
        help="Activate logging using the given file path",
    ).complete = shtab.FILE  # type: ignore[attr-defined]

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Valid subcommands",
        help="Additional help",
        dest="command",
    )

    # create a PR from command line
    pr_parser = subparsers.add_parser(
        "pull-request",
        aliases=["pr", "PR", "pullrequest"],
        help="Pull request related commands",
    )

    pr_parser.set_defaults(func=pull_request)

    pr_parser.add_argument(
        "-t",
        "--token",
        default="GITHUB_TOKEN",
        type=from_env,
        help=(
            "GitHub Token to access the repository. "
            "Default looks for environment variable 'GITHUB_TOKEN'"
        ),
    )

    pr_subparsers = pr_parser.add_subparsers(
        title="method",
        dest="pr_method",
        metavar="name",
        description="Valid pull request method",
        help="Pull request method",
        required=True,
    )

    create_pr_parser = pr_subparsers.add_parser(
        "create", help="Create Pull Request"
    )

    create_pr_parser.set_defaults(pr_func=create_pull_request)

    create_pr_parser.add_argument(
        "repo", help="GitHub repository (owner/name) to use"
    )

    create_pr_parser.add_argument(
        "head",
        help=("Branch to create a pull request from"),
    )

    create_pr_parser.add_argument(
        "target",
        default="main",
        help="Branch as as target for the pull. Default: %(default)s",
    )

    create_pr_parser.add_argument(
        "title",
        help="Title for the pull request",
    )

    create_pr_parser.add_argument(
        "-b",
        "--body",
        default=body_template.read_text(encoding="utf-8"),
        help=(
            "Description for the pull request. Can be formatted in Markdown."
        ),
    )

    update_pr_parser = pr_subparsers.add_parser(
        "update", help="Update Pull Request"
    )

    update_pr_parser.set_defaults(pr_func=update_pull_request)

    update_pr_parser.add_argument(
        "repo", help="GitHub repository (owner/name) to use"
    )
    update_pr_parser.add_argument(
        "pull_request", type=int, help="Pull Request to update"
    )
    update_pr_parser.add_argument(
        "--target",
        help="Branch as as target for the pull.",
    )
    update_pr_parser.add_argument(
        "--title",
        help="Title for the pull request",
    )

    update_pr_parser.add_argument(
        "-b",
        "--body",
        help=(
            "Description for the pull request. Can be formatted in Markdown."
        ),
    )

    # get files
    file_status_parser = subparsers.add_parser(
        "file-status", aliases=["status", "FS"], help="File status"
    )

    file_status_parser.set_defaults(func=file_status)

    file_status_parser.add_argument(
        "repo", help=("GitHub repository (owner/name) to use")
    )

    file_status_parser.add_argument(
        "pull_request", help="Specify the Pull Request number", type=int
    )

    file_status_parser.add_argument(
        "-s",
        "--status",
        choices=enum_choice(FileStatus),
        default=[FileStatus.ADDED, FileStatus.MODIFIED],
        nargs="+",
        help="What file status should be returned. Default: %(default)s",
    )

    file_status_parser.add_argument(
        "-o",
        "--output",
        type=FileType("w", encoding="utf-8"),
        help=(
            "Specify an output file. "
            "If none is given, output will be prompted"
            "The file will contain all files, with status "
            "changes, as given, separated by a newline"
        ),
    )

    file_status_parser.add_argument(
        "-t",
        "--token",
        default="GITHUB_TOKEN",
        type=from_env,
        help=(
            "GitHub Token to access the repository. "
            "Default looks for environment variable 'GITHUB_TOKEN'"
        ),
    )

    # labels
    label_parser = subparsers.add_parser(
        "labels", aliases=["L"], help="Issue/pull Request label handling"
    )

    label_parser.set_defaults(func=labels)

    label_parser.add_argument(
        "repo", help="GitHub repository (owner/name) to use"
    )

    label_parser.add_argument(
        "issue", help="Specify the Issue/Pull Request number", type=int
    )

    label_parser.add_argument(
        "--labels",
        "-L",
        nargs="+",
        help="Specify the labels, that should be set",
    )

    label_parser.add_argument(
        "-t",
        "--token",
        default="GITHUB_TOKEN",
        type=from_env,
        help=(
            "GitHub Token to access the repository. "
            "Default looks for environment variable 'GITHUB_TOKEN'"
        ),
    )

    repos_parser = subparsers.add_parser(
        "repos", aliases=["R"], help="Repository information"
    )

    repos_parser.set_defaults(func=repos)

    repos_parser.add_argument("orga", help="GitHub organization to use")

    repos_parser.add_argument(
        "-t",
        "--token",
        default="GITHUB_TOKEN",
        type=from_env,
        help=(
            "GitHub Token to access the repository. "
            "Default looks for environment variable 'GITHUB_TOKEN'"
        ),
    )

    repos_parser.add_argument(
        "--type",
        choices=enum_choice(RepositoryType),
        type=enum_type(RepositoryType),
        default=RepositoryType.PUBLIC,
        help=(
            "Define the type of repositories that should be covered. "
            "Default: %(default)s"
        ),
    )

    repos_parser.add_argument(
        "-p",
        "--path",
        help="Define the Path to save the Repository Information",
    )

    # create a release from command line
    re_parser = subparsers.add_parser(
        "release", aliases=["re", "RE", "release"], help="Release commands"
    )

    re_parser.set_defaults(func=release)

    re_parser.add_argument(
        "-t",
        "--token",
        default="GITHUB_TOKEN",
        type=from_env,
        help=(
            "GitHub Token to access the repository. "
            "Default looks for environment variable 'GITHUB_TOKEN'"
        ),
    )

    re_subparsers = re_parser.add_subparsers(
        title="method",
        dest="re_method",
        metavar="name",
        description="Valid release method",
        help="Release method",
        required=True,
    )

    create_re_parser = re_subparsers.add_parser("create", help="Create release")

    create_re_parser.set_defaults(re_func=create_release)

    create_re_parser.add_argument(
        "repo", help="GitHub repository (owner/name) to use"
    )

    create_re_parser.add_argument(
        "tag",
        help="Tag to use for release",
    )

    create_re_parser.add_argument(
        "name",
        help="Name of the release",
    )

    create_re_parser.add_argument(
        "-b",
        "--body",
        default=None,
        help="Description for the Release. Can be formatted in Markdown.",
    )

    create_re_parser.add_argument(
        "-tc",
        "--target-commitish",
        default=None,
        help="Git reference to use for the release",
    )

    create_re_parser.add_argument(
        "-d",
        "--draft",
        action="store_true",
        default=False,
        help="Create a draft release.",
    )

    create_re_parser.add_argument(
        "-p",
        "--prerelease",
        action="store_true",
        default=False,
        help="Create a pre-release.",
    )

    # Create a tag from command line
    tag_parser = subparsers.add_parser(
        "tag", aliases=["tag", "TAG"], help="Tag commands"
    )

    tag_parser.set_defaults(func=tag)

    tag_parser.add_argument(
        "-t",
        "--token",
        default="GITHUB_TOKEN",
        type=from_env,
        help=(
            "GitHub Token to access the repository. "
            "Default looks for environment variable 'GITHUB_TOKEN'"
        ),
    )

    tag_subparsers = tag_parser.add_subparsers(
        title="method",
        dest="tag_method",
        metavar="name",
        description="Valid tag method",
        help="Release method",
        required=True,
    )

    create_tag_parser = tag_subparsers.add_parser("create", help="Create tag")

    create_tag_parser.set_defaults(tag_func=create_tag)

    create_tag_parser.add_argument(
        "repo", help="GitHub repository (owner/name) to use"
    )

    create_tag_parser.add_argument(
        "tag",
        help="Tag name to use",
    )

    create_tag_parser.add_argument(
        "name",
        help="Name of the user",
    )

    create_tag_parser.add_argument(
        "message",
        help="Tag message",
    )

    create_tag_parser.add_argument(
        "git_object",
        help="The SHA of the git object this is tagging.",
    )
    create_tag_parser.add_argument(
        "email",
        help="Email address of the user",
    )

    create_tag_parser.add_argument(
        "-got",
        "--git-object-type",
        default="commit",
        help="The type of the object we're tagging",
    )

    create_tag_parser.add_argument(
        "-d",
        "--date",
        default=None,
        help=(
            "When this object was tagged. ISO 8601 format:"
            " YYYY-MM-DDTHH:MM:SSZ."
        ),
    )
    return parser.parse_args(args)
