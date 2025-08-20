import contextlib
import logging
import unittest
from io import StringIO

import numpy
import numpy as np

from evefile.entities import metadata


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.Metadata()
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.WARNING)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_copy_attributes_from_copies_attributes(self):
        new_metadata = metadata.Metadata()
        self.metadata.options = {"foo": "bar", "bla": "blub"}
        new_metadata.copy_attributes_from(self.metadata)
        self.assertDictEqual(self.metadata.options, new_metadata.options)

    def test_copy_attributes_from_copies_only_attr_existing_in_target(self):
        new_metadata = metadata.Metadata()
        self.metadata.non_existing_attribute = None
        new_metadata.copy_attributes_from(self.metadata)
        self.assertFalse(hasattr(new_metadata, "non_existing_attribute"))

    def test_copy_attributes_from_copies_only_attr_existing_in_source(self):
        new_metadata = metadata.Metadata()
        new_metadata.non_existing_attribute = None
        self.logger.setLevel(logging.DEBUG)
        with self.assertLogs(level=logging.DEBUG) as captured:
            new_metadata.copy_attributes_from(self.metadata)
        self.assertEqual(len(captured.records), 1)
        self.assertIn(
            "Cannot set non-existing attribute",
            captured.records[0].getMessage(),
        )

    def test_copied_attribute_is_copy(self):
        new_metadata = metadata.Metadata()
        self.metadata.options = {"foo": "bar", "bla": "blub"}
        new_metadata.copy_attributes_from(self.metadata)
        self.metadata.options.update({"baz": "foobar"})
        self.assertNotIn("baz", new_metadata.options)

    def test_copy_attributes_from_without_source_raises(self):
        with self.assertRaisesRegex(
            ValueError, "No source provided to copy attributes from."
        ):
            self.metadata.copy_attributes_from()

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)

    def test_print_with_options_prints_options(self):
        self.metadata.options = {
            "foo": "bar",
            "bla": "blub",
            "hugo": "heinz",
        }
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        self.assertIn("SCALAR OPTIONS", output)
        for key, value in self.metadata.options.items():
            self.assertIn(f"{key}: {value}", output)


class TestAbstractDeviceMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AbstractDeviceMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestMeasureMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.MeasureMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestMonitorMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.MonitorMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestDeviceMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.DeviceMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestAxisMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AxisMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "deadband",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.ChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestTimestampMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.TimestampMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestSinglePointChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.SinglePointChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestAverageChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AverageChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "n_averages",
            "low_limit",
            "max_attempts",
            "max_deviation",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestIntervalChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.IntervalChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "trigger_interval",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.NormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))


class TestSinglePointNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.SinglePointNormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestAverageNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.AverageNormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestIntervalNormalizedChannelMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.IntervalNormalizedChannelMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "options",
            "unit",
            "id",
            "pv",
            "access_mode",
            "normalize_id",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.metadata, attribute))

    def test_print_prints_attribute_names(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.metadata)
        output = temp_stdout.getvalue().strip()
        attributes = [
            item
            for item in dir(self.metadata)
            if not item.startswith("_")
            and not callable(getattr(self.metadata, item))
            and not item == "options"
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)
