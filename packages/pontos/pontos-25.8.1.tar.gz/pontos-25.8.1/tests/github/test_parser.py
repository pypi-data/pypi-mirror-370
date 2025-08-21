# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=no-member

import io
import unittest
from argparse import Namespace
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import Mock, patch

from pontos.github._parser import parse_args
from pontos.github.cmds import (
    create_pull_request,
    create_release,
    create_tag,
    file_status,
    update_pull_request,
)
from pontos.github.models.base import FileStatus
from pontos.testing import temp_directory


class TestArgparsing(unittest.TestCase):
    def setUp(self):
        self.term = Mock()

    def test_create_pr_parse_args(self):
        argv = [
            "pr",
            "create",
            "foo/bar",
            "baz",
            "main",
            "baz in main",
        ]
        with patch.dict("os.environ", {}, clear=True):
            parsed_args = parse_args(argv)

        template = Path().cwd() / "pontos/github/pr_template.md"

        self.assertEqual(parsed_args.command, "pr")
        self.assertEqual(parsed_args.token, "GITHUB_TOKEN")
        self.assertEqual(parsed_args.body, template.read_text(encoding="utf-8"))
        self.assertEqual(parsed_args.pr_func, create_pull_request)
        self.assertEqual(parsed_args.repo, "foo/bar")
        self.assertEqual(parsed_args.target, "main")
        self.assertEqual(parsed_args.title, "baz in main")

    def test_create_pr_parse_args_fail(self):
        argv = ["pr", "create", "foo/bar"]

        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            parse_args(argv)

    def test_update_pr_parse_args(self):
        argv = [
            "-q",
            "--log-file",
            "foo",
            "pr",
            "update",
            "foo/bar",
            "123",
            "--body",
            "foo",
            "--target",
            "main",
            "--title",
            "baz in main",
        ]

        with patch.dict("os.environ", {}, clear=True):
            parsed_args = parse_args(argv)

        self.assertEqual(parsed_args.command, "pr")
        self.assertEqual(parsed_args.token, "GITHUB_TOKEN")
        self.assertEqual(parsed_args.body, "foo")
        self.assertEqual(parsed_args.pr_func, update_pull_request)
        self.assertEqual(parsed_args.repo, "foo/bar")
        self.assertEqual(parsed_args.pull_request, 123)
        self.assertEqual(parsed_args.target, "main")
        self.assertEqual(parsed_args.title, "baz in main")
        self.assertTrue(parsed_args.quiet)
        self.assertEqual(parsed_args.log_file, "foo")

    def test_update_pr_parse_args_fail(self):
        argv = ["pr", "update", "foo/bar"]

        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            parse_args(argv)

    def test_fs_parse_args(self):
        with temp_directory(change_into=True) as tmp_dir:
            argv = [
                "FS",
                "foo/bar",
                "8",
                "-o",
                "some.file",
            ]

            with patch.dict("os.environ", {}, clear=True):
                parsed_args = parse_args(argv)

            output = open(tmp_dir / "some.file", mode="w", encoding="utf-8")

            expected_args = Namespace(
                command="FS",
                func=file_status,
                repo="foo/bar",
                pull_request=8,
                output=output,
                status=[FileStatus.ADDED, FileStatus.MODIFIED],
                token="GITHUB_TOKEN",
            )

            self.assertEqual(
                type(parsed_args.output), type(expected_args.output)
            )
            self.assertEqual(parsed_args.command, expected_args.command)
            self.assertEqual(parsed_args.func, expected_args.func)
            self.assertEqual(parsed_args.repo, expected_args.repo)
            self.assertEqual(
                parsed_args.pull_request, expected_args.pull_request
            )
            self.assertEqual(parsed_args.status, expected_args.status)
            self.assertEqual(parsed_args.token, expected_args.token)

            output.close()
            parsed_args.output.close()

    def test_create_release_parse_args(self):
        argv = [
            "re",
            "create",
            "foo/bar",
            "123",
            "release_name",
            "--body",
            "foo",
        ]

        with patch.dict("os.environ", {}, clear=True):
            parsed_args = parse_args(argv)

        self.assertEqual(parsed_args.command, "re")
        self.assertEqual(parsed_args.token, "GITHUB_TOKEN")
        self.assertEqual(parsed_args.re_func, create_release)
        self.assertEqual(parsed_args.repo, "foo/bar")
        self.assertEqual(parsed_args.tag, "123")
        self.assertEqual(parsed_args.name, "release_name")
        self.assertEqual(parsed_args.body, "foo")
        self.assertEqual(parsed_args.target_commitish, None)
        self.assertFalse(parsed_args.draft)
        self.assertFalse(parsed_args.prerelease)

    def test_create_tag_parse_args(self):
        argv = [
            "tag",
            "create",
            "foo/bar",
            "v1",
            "test user",
            "",
            "sha",
            "test@test.test",
        ]

        parsed_args = parse_args(argv)

        self.assertEqual(parsed_args.command, "tag")
        self.assertEqual(parsed_args.tag_func, create_tag)
        self.assertEqual(parsed_args.repo, "foo/bar")
        self.assertEqual(parsed_args.tag, "v1")
        self.assertEqual(parsed_args.message, "")
        self.assertEqual(parsed_args.git_object, "sha")
        self.assertEqual(parsed_args.email, "test@test.test")
