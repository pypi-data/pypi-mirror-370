# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# pylint: disable=no-member, disallowed-name

import unittest
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Union

from pontos.models import Model, ModelAttribute, ModelError, dotted_attributes


class DottedAttributesTestCase(unittest.TestCase):
    def test_with_new_class(self):
        class Foo:
            pass

        foo = Foo()
        attrs = {"bar": 123, "hello": "World", "baz": [1, 2, 3]}

        foo = dotted_attributes(foo, attrs)

        self.assertEqual(foo.bar, 123)
        self.assertEqual(foo.baz, [1, 2, 3])
        self.assertEqual(foo.hello, "World")

    def test_with_github_model_attribute(self):
        foo = ModelAttribute()
        attrs = {"bar": 123, "hello": "World", "baz": [1, 2, 3]}

        foo = dotted_attributes(foo, attrs)

        self.assertEqual(foo.bar, 123)
        self.assertEqual(foo.baz, [1, 2, 3])
        self.assertEqual(foo.hello, "World")


class ModelTestCase(unittest.TestCase):
    def test_from_dict(self):
        model = Model.from_dict(
            {
                "x": 1,
                "y": 2,
                "hello": "World",
                "baz": [1, 2, 3],
                "bar": {"a": "b"},
            }
        )

        self.assertEqual(model.x, 1)
        self.assertEqual(model.y, 2)
        self.assertEqual(model.hello, "World")
        self.assertEqual(model.baz, [1, 2, 3])
        self.assertEqual(model.bar.a, "b")

    def test_from_dict_failure(self):
        with self.assertRaisesRegex(
            ValueError, "Invalid data for creating an instance of.*"
        ):
            Model.from_dict("foo")


class ExampleModelTestCase(unittest.TestCase):
    def test_optional(self):
        @dataclass
        class OtherModel(Model):
            something: str

        @dataclass
        class ExampleModel(Model):
            foo: str
            bar: Optional[OtherModel] = None

        model = ExampleModel.from_dict({"foo": "abc"})

        self.assertIsNone(model.bar)

    def test_list(self):
        @dataclass
        class ExampleModel(Model):
            foo: List[str]

        model = ExampleModel.from_dict({"foo": ["a", "b", "c"]})
        self.assertEqual(model.foo, ["a", "b", "c"])

    def test_list_with_default(self):
        @dataclass
        class ExampleModel(Model):
            foo: List[str] = field(default_factory=list)

        model = ExampleModel.from_dict({})
        self.assertEqual(model.foo, [])

    def test_datetime(self):
        @dataclass
        class ExampleModel(Model):
            foo: datetime

        model = ExampleModel.from_dict({"foo": "1988-10-01T04:00:00.000"})
        self.assertEqual(
            model.foo, datetime(1988, 10, 1, 4, tzinfo=timezone.utc)
        )

        model = ExampleModel.from_dict({"foo": "1988-10-01T04:00:00Z"})
        self.assertEqual(
            model.foo, datetime(1988, 10, 1, 4, tzinfo=timezone.utc)
        )

        model = ExampleModel.from_dict({"foo": "1988-10-01T04:00:00+00:00"})
        self.assertEqual(
            model.foo, datetime(1988, 10, 1, 4, tzinfo=timezone.utc)
        )

        model = ExampleModel.from_dict({"foo": "1988-10-01T04:00:00+01:00"})
        self.assertEqual(
            model.foo,
            datetime(1988, 10, 1, 4, tzinfo=timezone(timedelta(hours=1))),
        )

        model = ExampleModel.from_dict({"foo": "2021-06-06T11:15:10.213"})
        self.assertEqual(
            model.foo,
            datetime(2021, 6, 6, 11, 15, 10, 213000, tzinfo=timezone.utc),
        )

    def test_date(self):
        @dataclass
        class ExampleModel(Model):
            foo: date

        model = ExampleModel.from_dict({"foo": "1988-10-01"})

        self.assertEqual(model.foo, date(1988, 10, 1))

    def test_union(self):
        @dataclass
        class ExampleModel(Model):
            foo: Union[str, int]

        model = ExampleModel.from_dict({"foo": "123"})

        self.assertEqual(model.foo, "123")

        model = ExampleModel.from_dict({"foo": 123})
        self.assertEqual(model.foo, 123)

    def test_other_model(self):
        @dataclass
        class OtherModel(Model):
            bar: str

        @dataclass
        class ExampleModel(Model):
            foo: Optional[OtherModel] = None

        model = ExampleModel.from_dict({"foo": {"bar": "baz"}})
        self.assertEqual(model.foo.bar, "baz")

    def test_all(self):
        @dataclass
        class OtherModel(Model):
            something: str

        @dataclass
        class ExampleModel(Model):
            foo: str
            bar: datetime
            id: Union[str, int]
            baz: List[str] = field(default_factory=list)
            ipsum: Optional[OtherModel] = None

        model = ExampleModel.from_dict(
            {
                "foo": "abc",
                "bar": "1988-10-01T04:00:00.000",
                "id": 123,
                "baz": ["a", "b", "c"],
                "ipsum": {"something": "def"},
            }
        )

        self.assertEqual(model.foo, "abc")
        self.assertEqual(
            model.bar, datetime(1988, 10, 1, 4, tzinfo=timezone.utc)
        )
        self.assertEqual(model.id, 123)
        self.assertEqual(model.baz, ["a", "b", "c"])
        self.assertIsNotNone(model.ipsum)
        self.assertEqual(model.ipsum.something, "def")

    def test_list_with_dict(self):
        @dataclass
        class ExampleModel(Model):
            foo: List[Dict]

        model = ExampleModel.from_dict({"foo": [{"a": 1}, {"b": 2}, {"c": 3}]})
        self.assertEqual(model.foo, [{"a": 1}, {"b": 2}, {"c": 3}])

    def test_model_error(self):
        @dataclass
        class ExampleModel(Model):
            foo: Optional[str] = None

        with self.assertRaisesRegex(
            ModelError,
            "Error while creating ExampleModel model. Could not set value for "
            "property 'foo' from '{'bar': 'baz'}'.",
        ):
            ExampleModel.from_dict({"foo": {"bar": "baz"}})

    def test_model_error_2(self):
        @dataclass
        class OtherModel(Model):
            something: str

        @dataclass
        class ExampleModel(Model):
            foo: Optional[OtherModel]

        with self.assertRaisesRegex(
            ModelError,
            "Error while creating ExampleModel model. Could not set value for "
            "property 'foo' from 'abc'.",
        ):
            ExampleModel.from_dict(
                {
                    "foo": "abc",
                }
            )
