import contextlib
import datetime
from io import StringIO
import unittest

from evefile.entities import file


class TestFile(unittest.TestCase):
    def setUp(self):
        self.file = file.File()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "data",
            "log_messages",
            "snapshots",
            "monitors",
            "position_timestamps",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.file, attribute))


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = file.Metadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "filename",
            "eveh5_version",
            "eve_version",
            "xml_version",
            "measurement_station",
            "start",
            "end",
            "description",
            "simulation",
            "preferred_axis",
            "preferred_channel",
            "preferred_normalisation_channel",
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
            item for item in dir(self.metadata) if not item.startswith("_")
        ]
        for attribute in attributes:
            self.assertIn(attribute, output)


class TestLogMessage(unittest.TestCase):
    def setUp(self):
        self.log_message = file.LogMessage()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = ["timestamp", "message"]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.log_message, attribute))

    def test_from_string_sets_timestamp_and_message(self):
        string = "2024-07-25T10:04:03: Lorem ipsum"
        self.log_message.from_string(string)
        timestamp, message = string.split(": ", maxsplit=1)
        self.assertEqual(
            datetime.datetime.fromisoformat(timestamp),
            self.log_message.timestamp,
        )
        self.assertEqual(message, self.log_message.message)

    def test_print_prints_log_message(self):
        string = "2024-07-25T10:04:03: Lorem ipsum"
        self.log_message.from_string(string)
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.log_message)
        output = temp_stdout.getvalue().strip()
        self.assertEqual(string, output)
