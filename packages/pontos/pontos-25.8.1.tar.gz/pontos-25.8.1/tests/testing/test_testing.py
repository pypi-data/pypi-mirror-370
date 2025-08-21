# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import struct
import unittest
from pathlib import Path

from pontos.git import Git
from pontos.helper import unload_module
from pontos.testing import (
    temp_directory,
    temp_file,
    temp_git_repository,
    temp_python_module,
)


class TempDirectoryTestCase(unittest.TestCase):
    def test_temp_directory(self):
        with temp_directory() as tmp_dir:
            tmp_file = tmp_dir / "test.txt"
            tmp_file.write_text("Lorem Ipsum", encoding="utf8")

            self.assertTrue(tmp_dir.exists())
            self.assertTrue(tmp_file.exists())

        self.assertFalse(tmp_dir.exists())
        self.assertFalse(tmp_file.exists())

    def test_temp_directory_exception(self):
        try:
            with temp_directory() as tmp_dir:
                tmp_file = tmp_dir / "test.txt"
                tmp_file.write_text("Lorem Ipsum", encoding="utf8")

                self.assertTrue(tmp_dir.exists())
                self.assertTrue(tmp_file.exists())
                raise ValueError()
        except ValueError:
            pass
        finally:
            self.assertFalse(tmp_dir.exists())
            self.assertFalse(tmp_file.exists())

    def test_temp_directory_change_into(self):
        old_cwd = Path.cwd()
        with temp_directory(change_into=True) as tmp_dir:
            new_cwd = Path.cwd()

            self.assertEqual(new_cwd, tmp_dir.resolve())
            self.assertNotEqual(old_cwd, new_cwd)

    def test_temp_directory_add_to_sys_path(self):
        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import mymodule2  # noqa: F401,F811

        with temp_directory(add_to_sys_path=True) as module_path:
            mymodule_file = module_path / "mymodule2.py"
            mymodule_file.touch()

            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import mymodule2  # noqa: F401,F811

        unload_module("mymodule")


class TempGitRepositoryTestCase(unittest.TestCase):
    def test_temp_git_repository(self):
        with temp_git_repository(branch="foo") as git_directory:
            test_file = git_directory / "test.txt"
            test_file.write_text("Lorem Ipsum", encoding="utf8")

            self.assertTrue(git_directory.exists())
            self.assertTrue(test_file.exists())

            git = Git(git_directory)
            git.add(test_file)

        self.assertFalse(git_directory.exists())
        self.assertFalse(test_file.exists())

    def test_temp_git_repository_exception(self):
        try:
            with temp_git_repository(branch="foo") as git_directory:
                test_file = git_directory / "test.txt"
                test_file.write_text("Lorem Ipsum", encoding="utf8")

                self.assertTrue(git_directory.exists())
                self.assertTrue(test_file.exists())

                git = Git(git_directory)
                git.add(test_file)

                raise ValueError()
        except ValueError:
            pass
        finally:
            self.assertFalse(git_directory.exists())
            self.assertFalse(test_file.exists())


class TempFileTestCase(unittest.TestCase):
    def test_temp_file(self):
        with temp_file("my content") as test_file:
            self.assertTrue(test_file.exists())
            self.assertEqual("my content", test_file.read_text(encoding="utf8"))

        self.assertFalse(test_file.exists())

    def test_temp_binary_file(self):
        data = struct.pack(">if", 42, 2.71828182846)
        with temp_file(data) as test_file:
            self.assertTrue(test_file.exists())
            self.assertEqual(data, test_file.read_bytes())

        self.assertFalse(test_file.exists())

    def test_temp_file_without_content(self):
        with temp_file(name="foo.bar") as test_file:
            self.assertTrue(test_file.exists())
            self.assertTrue(test_file.is_file())
            self.assertEqual("", test_file.read_text(encoding="utf8"))

        self.assertFalse(test_file.exists())

    def test_temp_file_exception(self):
        try:
            with temp_file("my content") as test_file:
                self.assertTrue(test_file.exists())
                self.assertEqual(
                    "my content", test_file.read_text(encoding="utf8")
                )

                raise ValueError()

        except ValueError:
            pass
        finally:
            self.assertFalse(test_file.exists())

    def test_temp_file_name(self):
        with temp_file("my content", name="foo.txt") as test_file:
            self.assertTrue(test_file.exists())
            self.assertEqual(test_file.name, "foo.txt")
            self.assertEqual("my content", test_file.read_text(encoding="utf8"))

        self.assertFalse(test_file.exists())

    def test_temp_file_change_into(self):
        old_cwd = Path.cwd()
        with temp_file("my content", change_into=True) as test_file:
            new_cwd = Path.cwd()

            self.assertTrue(test_file.exists())
            self.assertEqual("my content", test_file.read_text(encoding="utf8"))

            self.assertEqual(new_cwd, test_file.parent.resolve())
            self.assertNotEqual(old_cwd, new_cwd)

        self.assertFalse(test_file.exists())


class TempPythonModuleTestCase(unittest.TestCase):
    def test_temp_python_module(self):
        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import foo  # noqa: F401,F811

        with temp_python_module("def foo():\n  pass") as module_path:
            self.assertTrue(module_path.exists())

            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import foo  # noqa: F401,F811

        self.assertFalse(module_path.exists())

        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import foo  # noqa: F401,F811

    def test_temp_python_module_exception(self):
        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import foo  # noqa: F401,F811

        try:
            with temp_python_module("def foo():\n  pass") as module_path:
                self.assertTrue(module_path.exists())

                # pylint: disable=import-error,import-outside-toplevel,unused-import # noqa: E501
                import foo  # noqa: F401,F811

                raise ValueError()
        except ValueError:
            pass
        finally:
            self.assertFalse(module_path.exists())

        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import foo  # noqa: F401,F811

    def test_temp_python_module_name(self):
        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import mymodule3  # noqa: F401,F811

        with temp_python_module(
            "def foo():\n  pass", name="mymodule3"
        ) as module_path:
            self.assertTrue(module_path.exists())

            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import mymodule3  # noqa: F401,F811

        self.assertFalse(module_path.exists())

        with self.assertRaises(ImportError):
            # pylint: disable=import-error,import-outside-toplevel,unused-import
            import mymodule3  # noqa: F401,F811
