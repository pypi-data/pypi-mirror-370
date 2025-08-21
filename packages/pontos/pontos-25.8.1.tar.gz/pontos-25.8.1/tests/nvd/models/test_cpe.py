# SPDX-FileCopyrightText: 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

# pylint: disable=line-too-long
# ruff: noqa: E501

import unittest
from datetime import datetime, timezone
from uuid import UUID

from pontos.nvd.models.cpe import CPE, ReferenceType
from tests.nvd import get_cpe_data


class CPETestCase(unittest.TestCase):
    def test_required_only(self):
        cpe = CPE.from_dict(get_cpe_data())

        self.assertEqual(
            cpe.cpe_name,
            "cpe:2.3:o:microsoft:windows_10_22h2:-:*:*:*:*:*:arm64:*",
        )
        self.assertEqual(
            cpe.cpe_name_id, UUID("9BAECDB2-614D-4E9C-9936-190C30246F03")
        )
        self.assertFalse(cpe.deprecated)
        self.assertEqual(
            cpe.last_modified,
            datetime(2022, 12, 9, 18, 15, 16, 973000, tzinfo=timezone.utc),
        )
        self.assertEqual(
            cpe.created,
            datetime(2022, 12, 9, 16, 20, 6, 943000, tzinfo=timezone.utc),
        )

        self.assertEqual(cpe.titles, [])
        self.assertEqual(cpe.refs, [])
        self.assertEqual(cpe.deprecated_by, [])

    def test_titles(self):
        cpe = CPE.from_dict(
            get_cpe_data(
                {
                    "titles": [
                        {
                            "title": "Microsoft Windows 10 22h2 on ARM64",
                            "lang": "en",
                        }
                    ],
                }
            )
        )

        self.assertEqual(len(cpe.titles), 1)

        title = cpe.titles[0]
        self.assertEqual(title.title, "Microsoft Windows 10 22h2 on ARM64")
        self.assertEqual(title.lang, "en")

    def test_refs(self):
        cpe = CPE.from_dict(
            get_cpe_data(
                {
                    "refs": [
                        {
                            "ref": "https://learn.microsoft.com/en-us/windows/release-health/release-information",
                            "type": "Version",
                        }
                    ],
                }
            )
        )

        self.assertEqual(len(cpe.refs), 1)

        reference = cpe.refs[0]
        self.assertEqual(
            reference.ref,
            "https://learn.microsoft.com/en-us/windows/release-health/release-information",
        )
        self.assertEqual(reference.type, ReferenceType.VERSION)

    def test_deprecated(self):
        cpe = CPE.from_dict(
            get_cpe_data(
                {
                    "deprecated": True,
                    "deprecated_by": [
                        {
                            "cpe_name": "cpe:2.3:o:microsoft:windows_10_22h2:-:*:*:*:*:*:x64:*",
                            "cpe_name_id": "A09335E2-B42F-4820-B487-57A4BF0CEE98",
                        }
                    ],
                }
            )
        )

        self.assertTrue(cpe.deprecated)
        self.assertEqual(len(cpe.deprecated_by), 1)

        deprecated_by = cpe.deprecated_by[0]
        self.assertEqual(
            deprecated_by.cpe_name,
            "cpe:2.3:o:microsoft:windows_10_22h2:-:*:*:*:*:*:x64:*",
        )
        self.assertEqual(
            deprecated_by.cpe_name_id,
            UUID("A09335E2-B42F-4820-B487-57A4BF0CEE98"),
        )
