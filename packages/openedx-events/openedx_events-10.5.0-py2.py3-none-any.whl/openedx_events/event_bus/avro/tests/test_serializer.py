"""Tests for avro.serializer module."""

import json
from datetime import datetime

import pytest
from django.test import TestCase
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys.edx.locator import LibraryLocatorV2, LibraryUsageLocatorV2

from openedx_events.event_bus.avro.serializer import AvroSignalSerializer, serialize_event_data_to_bytes
from openedx_events.event_bus.avro.tests.test_utilities import (
    CustomAttrsWithDefaults,
    CustomAttrsWithoutDefaults,
    EventData,
    NestedAttrsWithDefaults,
    NestedNonAttrs,
    NonAttrs,
    SimpleAttrs,
    SimpleAttrsWithDefaults,
    SpecialSerializer,
    SubTestData0,
    SubTestData1,
    create_simple_signal,
)
from openedx_events.tests.utils import FreezeSignalCacheMixin


class TestAvroSignalSerializerCache(FreezeSignalCacheMixin, TestCase):
    """Tests for AvroSignalSerializer."""

    def test_schema_string(self):
        """
        Test JSON round-trip; schema creation is tested more fully in test_schema.py.
        """
        SIGNAL = create_simple_signal({
            "data": SimpleAttrs
        })
        actual_schema = json.loads(AvroSignalSerializer(SIGNAL).schema_string())
        expected_schema = {
            'name': 'CloudEvent',
            'type': 'record',
            'doc': 'Avro Event Format for CloudEvents created with openedx_events/schema',
            'namespace': 'simple.signal',
            'fields': [
                {
                    'name': 'data',
                    'type': {
                        'name': 'SimpleAttrs',
                        'type': 'record',
                        'fields': [
                            {'name': 'boolean_field', 'type': 'boolean'},
                            {'name': 'int_field', 'type': 'long'},
                            {'name': 'float_field', 'type': 'double'},
                            {'name': 'bytes_field', 'type': 'bytes'},
                            {'name': 'string_field', 'type': 'string'},
                        ]
                    }
                }
            ]
        }
        assert actual_schema == expected_schema

    def test_convert_event_data_to_dict(self):
        """
        Tests that an event with complex attrs objects can be converted to a dict.
        """

        # A test record that we can try to serialize to avro.
        test_data = EventData(
            "foo",
            "bar.course",
            SubTestData0("a.sub.name", "a.nother.course"),
            SubTestData1("b.uber.sub.name", "b.uber.another.course"),
        )
        SIGNAL = create_simple_signal({"test_data": EventData})

        serializer = AvroSignalSerializer(SIGNAL)

        data_dict = serializer.to_dict({"test_data": test_data})
        expected_dict = {
            "test_data": {
                "course_id": "bar.course",
                "sub_name": "foo",
                "sub_test_0": {"course_id": "a.nother.course", "sub_name": "a.sub.name"},
                "sub_test_1": {
                    "course_id": "b.uber.another.course",
                    "sub_name": "b.uber.sub.name",
                },
            }
        }
        self.assertDictEqual(data_dict, expected_dict)

    def test_default_datetime_serialization(self):
        SIGNAL = create_simple_signal({"birthday": datetime})
        serializer = AvroSignalSerializer(SIGNAL)
        birthday = datetime(year=1989, month=9, day=6)
        test_data = {"birthday": birthday}
        data_dict = serializer.to_dict(test_data)
        self.assertDictEqual(data_dict, {"birthday": birthday.isoformat()})

    def test_default_coursekey_serialization(self):
        SIGNAL = create_simple_signal({"course": CourseKey})
        serializer = AvroSignalSerializer(SIGNAL)
        course_key = CourseKey.from_string("course-v1:edX+DemoX.1+2014")
        test_data = {"course": course_key}
        data_dict = serializer.to_dict(test_data)
        self.assertDictEqual(data_dict, {"course": str(course_key)})

    def test_default_usagekey_serialization(self):
        """
        Test serialization of UsageKey
        """
        SIGNAL = create_simple_signal({"usage_key": UsageKey})
        serializer = AvroSignalSerializer(SIGNAL)
        usage_key = UsageKey.from_string(
            "block-v1:edx+DemoX+Demo_course+type@video+block@UaEBjyMjcLW65gaTXggB93WmvoxGAJa0JeHRrDThk",
        )
        test_data = {"usage_key": usage_key}
        data_dict = serializer.to_dict(test_data)
        self.assertDictEqual(data_dict, {"usage_key": str(usage_key)})

    def test_default_librarylocatorv2_serialization(self):
        """
        Test serialization of LibraryLocatorV2
        """
        SIGNAL = create_simple_signal({"library_key": LibraryLocatorV2})
        serializer = AvroSignalSerializer(SIGNAL)
        library_key = LibraryLocatorV2.from_string("lib:MITx:reallyhardproblems")
        test_data = {"library_key": library_key}
        data_dict = serializer.to_dict(test_data)
        self.assertDictEqual(data_dict, {"library_key": str(library_key)})

    def test_default_libraryusagelocatorv2_serialization(self):
        """
        Test serialization of LibraryUsageLocatorV2
        """
        SIGNAL = create_simple_signal({"usage_key": LibraryUsageLocatorV2})
        serializer = AvroSignalSerializer(SIGNAL)
        usage_key = LibraryUsageLocatorV2.from_string("lb:MITx:reallyhardproblems:problem:problem1")
        test_data = {"usage_key": usage_key}
        data_dict = serializer.to_dict(test_data)
        self.assertDictEqual(data_dict, {"usage_key": str(usage_key)})

    def test_serialization_with_custom_serializer(self):
        SIGNAL = create_simple_signal({"test_data": NonAttrs})

        serializer = SpecialSerializer(SIGNAL)
        test_data = {
            "test_data": NonAttrs("a.val", "a.nother.val")
        }
        data_dict = serializer.to_dict(test_data)
        self.assertDictEqual(data_dict, {"test_data": "a.val:a.nother.val"})

    def test_serialization_with_custom_serializer_on_nested_fields(self):
        SIGNAL = create_simple_signal({"test_data": NestedNonAttrs})
        test_data = {
            "test_data": NestedNonAttrs(field_0=NonAttrs("a.val", "a.nother.val"))
        }
        serializer = SpecialSerializer(SIGNAL)
        test_data = {"test_data": NestedNonAttrs(field_0=NonAttrs("a.val", "a.nother.val"))}
        data_dict = serializer.to_dict(test_data)
        self.assertDictEqual(data_dict, {"test_data": {
            "field_0": "a.val:a.nother.val"
        }})

    def test_serialization_of_optional_simple_fields(self):
        SIGNAL = create_simple_signal({
            "data": SimpleAttrsWithDefaults
        })
        serializer = AvroSignalSerializer(SIGNAL)
        event_data = {"data": SimpleAttrsWithDefaults()}
        data_dict = serializer.to_dict(event_data)
        self.assertDictEqual(data_dict, {"data": {'boolean_field': None,
                                                  'bytes_field': None,
                                                  'float_field': None,
                                                  'int_field': None,
                                                  'string_field': None,
                                                  'attrs_field': None}})

    def test_serialization_of_optional_custom_fields(self):
        SIGNAL = create_simple_signal({"data": CustomAttrsWithDefaults})
        serializer = AvroSignalSerializer(SIGNAL)
        event_data = {"data": CustomAttrsWithDefaults(coursekey_field=None, datetime_field=None)}
        data_dict = serializer.to_dict(event_data)
        self.assertDictEqual(data_dict, {"data": {'coursekey_field': None,
                                                  'datetime_field': None}})

    def test_serialization_of_none_mandatory_custom_fields(self):
        """Check that None isn't accepted if field not optional."""
        SIGNAL = create_simple_signal({"data": CustomAttrsWithoutDefaults})
        serializer = AvroSignalSerializer(SIGNAL)
        event_data = {"data": CustomAttrsWithoutDefaults(coursekey_field=None, datetime_field=None)}
        with pytest.raises(Exception) as excinfo:
            serializer.to_dict(event_data)
        assert excinfo.value.args[0] == "None cannot be handled by custom serializers (and default=None was not set)"

    def test_serialization_of_nested_optional_fields(self):
        SIGNAL = create_simple_signal({
            "data": NestedAttrsWithDefaults
        })
        serializer = AvroSignalSerializer(SIGNAL)

        event_data = {"data": NestedAttrsWithDefaults(field_0=SimpleAttrsWithDefaults())}
        data_dict = serializer.to_dict(event_data)
        self.assertDictEqual(data_dict, {"data": {"field_0": {'boolean_field': None,
                                                              'bytes_field': None,
                                                              'float_field': None,
                                                              'int_field': None,
                                                              'string_field': None,
                                                              'attrs_field': None
                                                              }}})

    def test_serialize_event_data_to_bytes(self):
        """
        Test serialize_event_data_to_bytes utility function.
        """
        SIGNAL = create_simple_signal({"test_data": EventData})
        event_data = {"test_data": EventData(
            "foo",
            "bar.course",
            SubTestData0("a.sub.name", "a.nother.course"),
            SubTestData1("b.uber.sub.name", "b.uber.another.course"),
        )}
        serialized = serialize_event_data_to_bytes(event_data, SIGNAL)
        expected = b'\x06foo\x14bar.course\x14a.sub.name\x1ea.nother.course\x1eb.uber.sub.name*b.uber.another.course'
        self.assertEqual(serialized, expected)
