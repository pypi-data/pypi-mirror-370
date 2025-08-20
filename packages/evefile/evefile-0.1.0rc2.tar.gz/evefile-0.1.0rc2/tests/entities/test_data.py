import contextlib
import copy
import logging
import os
import unittest
from io import StringIO

import h5py
import numpy as np
import pandas as pd

from evefile.entities import data, metadata


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename
        self.shape = 10

    def create(self, random=False, double=False, gaps=False):
        with h5py.File(self.filename, "w") as file:
            c1 = file.create_group("c1")
            c1.create_group("main")
            c1.create_group("snapshot")
            meta = c1.create_group("meta")
            data_ = np.ndarray(
                [self.shape],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
                ),
            )
            if random:
                data_["PosCounter"] = np.random.randint(
                    low=1, high=self.shape, size=self.shape
                )
                data_["PosCountTimer"] = np.linspace(start=2, stop=20, num=10)
            elif double:
                data_["PosCounter"] = np.asarray(
                    [1, 1, 2, 3, 4, 4, 4, 5, 6, 6]
                )
                self.shape = len(np.unique(data_["PosCounter"]))
                data_["PosCountTimer"] = np.asarray(
                    [2, 3, 4, 6, 8, 9, 9, 10, 12, 13]
                )
            elif gaps:
                data_["PosCounter"] = np.asarray(
                    [1, 2, 4, 5, 6, 8, 9, 10, 12, 13]
                )
                self.shape = len(np.unique(data_["PosCounter"]))
                data_["PosCountTimer"] = np.asarray(
                    [2, 3, 4, 6, 8, 9, 9, 10, 12, 13]
                )
            else:
                data_["PosCounter"] = np.linspace(
                    start=1, stop=self.shape, num=self.shape
                )
                data_["PosCountTimer"] = np.linspace(
                    start=2, stop=self.shape * 2, num=self.shape
                )
            poscounttimer = meta.create_dataset("PosCountTimer", data=data_)
            poscounttimer.attrs["Unit"] = np.bytes_(["msecs"])


class TestData(unittest.TestCase):
    def setUp(self):
        self.data = data.Data()
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.WARNING)

        class MockData(data.Data):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "importer",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_setting_data_sets_data(self):
        self.data.data = np.random.random(5)
        self.assertTrue(self.data)

    def test_accessing_data_calls_get_data_if_data_not_loaded(self):
        _ = self.mock_data.data
        self.assertTrue(self.mock_data.get_data_called)

    def test_accessing_data_with_data_does_not_call_get_data(self):
        self.mock_data.data = np.random.random(5)
        _ = self.mock_data.data
        self.assertFalse(self.mock_data.get_data_called)

    def test_get_data_loads_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertTrue(self.data.data.any())

    def test_copy_attributes_from_copies_attributes(self):
        new_data = data.Data()
        self.data.options = {"foo": "bar", "bla": "blub"}
        new_data.copy_attributes_from(self.data)
        self.assertDictEqual(self.data.options, new_data.options)

    def test_copy_attributes_from_copies_only_existing_attributes(self):
        new_data = data.Data()
        self.data.non_existing_attribute = None
        new_data.copy_attributes_from(self.data)
        self.assertFalse(hasattr(new_data, "non_existing_attribute"))

    def test_copy_attributes_from_copies_only_attr_existing_in_source(self):
        new_data = data.Data()
        new_data.non_existing_attribute = None
        self.logger.setLevel(logging.DEBUG)
        with self.assertLogs(level=logging.DEBUG) as captured:
            new_data.copy_attributes_from(self.data)
        self.assertEqual(len(captured.records), 1)
        self.assertIn(
            "Cannot set non-existing attribute",
            captured.records[0].getMessage(),
        )

    def test_copied_attribute_is_copy(self):
        new_data = data.Data()
        self.data.options = {"foo": "bar", "bla": "blub"}
        new_data.copy_attributes_from(self.data)
        self.data.options.update({"baz": "foobar"})
        self.assertNotIn("baz", new_data.options)

    def test_copy_attributes_from_copies_metadata(self):
        new_data = data.Data()
        self.data.metadata.name = "foo"
        new_data.copy_attributes_from(self.data)
        self.assertEqual(self.data.metadata.name, new_data.metadata.name)

    def test_copy_attributes_from_copies_only_existing_metadata(self):
        new_data = data.Data()
        self.data.metadata.nonexisting_attribute = "foo"
        new_data.copy_attributes_from(self.data)
        self.assertFalse(hasattr(new_data.metadata, "nonexisting_attribute"))

    def test_copy_attributes_from_without_source_raises(self):
        with self.assertRaisesRegex(
            ValueError, "No source provided to copy attributes from."
        ):
            self.data.copy_attributes_from()

    def test_print_prints_human_friendly_output(self):
        self.data.metadata.name = "foo"
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.data)
        output = temp_stdout.getvalue().strip()
        self.assertEqual(f"{self.data.metadata.name} <Data>", output)

    def test_show_info_prints_metadata(self):
        self.data.metadata.name = "foo"
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.data.show_info()
        output = temp_stdout.getvalue().strip()
        self.assertIn("METADATA", output)
        self.assertIn("name: ", output)

    def test_show_info_prints_option_keys_if_they_exist(self):
        self.data.options = {
            "foo": np.ndarray([]),
            "bar": np.ndarray([]),
        }
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.data.show_info()
        output = temp_stdout.getvalue().strip()
        self.assertIn("OPTIONS", output)
        self.assertIn("foo", output)
        self.assertIn("bar", output)

    def test_show_info_does_not_print_options_if_they_dont_exist(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.data.show_info()
        output = temp_stdout.getvalue().strip()
        self.assertNotIn("OPTIONS", output)

    def test_show_info_prints_fields(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.data.show_info()
        output = temp_stdout.getvalue().strip()
        self.assertIn("FIELDS", output)
        self.assertIn("data", output)

    def test_get_dataframe_returns_dataframe(self):
        dataframe = self.data.get_dataframe()
        self.assertIsInstance(dataframe, pd.DataFrame)

    def test_dataframe_contains_data_column(self):
        dataframe = self.data.get_dataframe()
        self.assertTrue(dataframe.columns.size)
        self.assertListEqual(
            list(dataframe.columns),
            ["data"],
        )

    def test_get_dataframe_loads_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        dataframe = self.data.get_dataframe()
        self.assertTrue(dataframe.size)


class TestMonitorData(unittest.TestCase):
    def setUp(self):
        self.data = data.MonitorData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "milliseconds",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.MonitorMetadata)

    def test_print_prints_human_friendly_output(self):
        self.data.metadata.name = "foo"
        self.data.metadata.id = "foo:42"
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.data)
        output = temp_stdout.getvalue().strip()
        self.assertEqual(
            f"{self.data.metadata.name} ("
            f"{self.data.metadata.id}) <MonitorData>",
            output,
        )

    def test_show_info_prints_fields(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.data.show_info()
        output = temp_stdout.getvalue().strip()
        for field in ["data", "milliseconds"]:
            self.assertIn(field, output)

    def test_dataframe_has_correct_index_name(self):
        dataframe = self.data.get_dataframe()
        self.assertEqual("milliseconds", dataframe.index.name)

    def test_dataframe_has_correct_index_values(self):
        self.data.data = np.random.random(3)
        self.data.milliseconds = np.asarray([3, 12, 28])
        dataframe = self.data.get_dataframe()
        np.testing.assert_array_equal(self.data.milliseconds, dataframe.index)


class TestMeasureData(unittest.TestCase):
    def setUp(self):
        self.data = data.MeasureData()
        self.filename = "test.h5"

        class MockData(data.MeasureData):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.MeasureMetadata)

    def test_get_data_sorts_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(random=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertTrue(np.all(np.diff(self.data.position_counts) >= 0))
        self.assertFalse(np.all(np.diff(self.data.data) >= 0))

    def test_setting_positions_sets_positions(self):
        self.data.position_counts = np.random.random(5)
        self.assertGreater(len(self.data.position_counts), 0)

    def test_accessing_positions_calls_get_data_if_not_loaded(self):
        _ = self.mock_data.position_counts
        self.assertTrue(self.mock_data.get_data_called)

    def test_accessing_positions_with_positions_does_not_call_get_data(self):
        self.mock_data.position_counts = np.random.random(5)
        _ = self.mock_data.position_counts
        self.assertFalse(self.mock_data.get_data_called)

    def test_print_prints_human_friendly_output(self):
        self.data.metadata.name = "foo"
        self.data.metadata.id = "foo:42"
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            print(self.data)
        output = temp_stdout.getvalue().strip()
        self.assertEqual(
            f"{self.data.metadata.name} ("
            f"{self.data.metadata.id}) <MeasureData>",
            output,
        )

    def test_show_info_prints_fields(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.data.show_info()
        output = temp_stdout.getvalue().strip()
        for field in ["data", "position_counts"]:
            self.assertIn(field, output)

    def test_dataframe_has_correct_index_name(self):
        dataframe = self.data.get_dataframe()
        self.assertEqual("position", dataframe.index.name)

    def test_dataframe_has_correct_index_values(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 12, 28])
        dataframe = self.data.get_dataframe()
        np.testing.assert_array_equal(
            self.data.position_counts, dataframe.index
        )

    def test_join_without_positions_raises(self):
        with self.assertRaisesRegex(ValueError, "No positions provided"):
            self.data.join()

    def test_join_with_identical_positions(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = self.data.position_counts
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(self.data.data, data_.data)
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts
        )

    def test_join_with_positions_subset_reduces(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = self.data.position_counts[[0, 2]]
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(self.data.data[[0, 2]], data_.data)
        np.testing.assert_array_equal(
            self.data.position_counts[[0, 2]], data_.position_counts
        )

    def test_join_with_positions_superset_masks(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6], dtype=np.int64)
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(self.data.data, data_.data[1:4])
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        np.testing.assert_array_equal(positions, data_.position_counts)
        self.assertIsInstance(data_.data, np.ma.MaskedArray)


class TestDeviceData(unittest.TestCase):
    def setUp(self):
        self.data = data.DeviceData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.DeviceMetadata)


class TestAxisData(unittest.TestCase):
    def setUp(self):
        self.data = data.AxisData()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "set_values",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.AxisMetadata)

    def test_get_data_takes_last_from_duplicate_pos_counts(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(double=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertTrue(np.all(np.diff(self.data.position_counts) > 0))
        self.assertTrue(np.any(self.data.data % 2))
        self.assertEqual(h5file.shape, len(self.data.data))

    def test_get_data_preserves_length_of_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(double=False)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertEqual(h5file.shape, len(self.data.data))

    def test_get_data_with_gaps_in_position_counts_returns_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(gaps=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertEqual(h5file.shape, len(self.data.data))

    def test_join_with_positions_subset_reduces(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = self.data.position_counts[[0, 2]]
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(self.data.data[[0, 2]], data_.data)
        np.testing.assert_array_equal(
            self.data.position_counts[[0, 2]], data_.position_counts
        )

    def test_join_with_positions_superset_masks(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6], dtype=np.int64)
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(self.data.data, data_.data[1:4])
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        np.testing.assert_array_equal(positions, data_.position_counts)
        self.assertIsInstance(data_.data, np.ma.MaskedArray)

    def test_join_with_positions_left_superset_and_fill_fills(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6], dtype=np.int64)
        data_ = copy.copy(self.data)
        data_.join(positions=positions, fill=True)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(self.data.data, data_.data[1:4])
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        self.assertEqual(self.data.data[-1], data_.data[-1])
        np.testing.assert_array_equal(positions, data_.position_counts)
        self.assertIsInstance(data_.data, np.ma.MaskedArray)

    def test_join_with_positions_right_superset_and_fill_fills(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([3, 4, 5, 6], dtype=np.int64)
        data_ = copy.copy(self.data)
        data_.join(positions=positions, fill=True)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(self.data.data, data_.data[0:3])
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[0:3]
        )
        self.assertEqual(self.data.data[-1], data_.data[-1])
        np.testing.assert_array_equal(positions, data_.position_counts)
        self.assertNotIsInstance(data_.data, np.ma.MaskedArray)

    def test_join_with_positions_superset_and_snapshot_fills(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6], dtype=np.int64)
        snapshot = data.AxisData()
        snapshot.position_counts = np.asarray([2], dtype=np.int64)
        snapshot.data = np.random.random(1)
        data_ = copy.copy(self.data)
        data_.join(positions=positions, snapshot=snapshot)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(data_.data[1:4], self.data.data)
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        self.assertEqual(snapshot.data, data_.data[0])
        self.assertEqual(self.data.data[-1], data_.data[-1])
        np.testing.assert_array_equal(positions, data_.position_counts)
        self.assertNotIsInstance(data_.data, np.ma.MaskedArray)

    def test_join_with_positions_superset_and_snapshots_fills(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6, 7, 8, 9], dtype=np.int64)
        snapshot = data.AxisData()
        snapshot.position_counts = np.asarray([2, 8], dtype=np.int64)
        snapshot.data = np.random.random(2)
        data_ = copy.copy(self.data)
        data_.join(positions=positions, snapshot=snapshot)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(data_.data[1:4], self.data.data)
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        self.assertEqual(snapshot.data[0], data_.data[0])
        self.assertEqual(snapshot.data[1], data_.data[6])
        self.assertEqual(self.data.data[2], data_.data[5])
        np.testing.assert_array_equal(positions, data_.position_counts)
        self.assertNotIsInstance(data_.data, np.ma.MaskedArray)

    def test_join_with_positions_superset_and_late_snapshot(self):
        self.data.data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.int64)
        snapshot = data.AxisData()
        snapshot.position_counts = np.asarray([2, 8], dtype=np.int64)
        snapshot.data = np.random.random(2)
        data_ = copy.copy(self.data)
        data_.join(positions=positions, snapshot=snapshot)
        self.assertTrue(data_.data.any())
        np.testing.assert_array_equal(data_.data[2:5], self.data.data)
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[2:5]
        )
        self.assertEqual(snapshot.data[0], data_.data[1])
        self.assertEqual(snapshot.data[1], data_.data[7])
        self.assertEqual(self.data.data[2], data_.data[6])
        np.testing.assert_array_equal(positions, data_.position_counts)
        self.assertIsInstance(data_.data, np.ma.MaskedArray)


class TestChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.ChannelData()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.ChannelMetadata)

    def test_get_data_takes_first_from_duplicate_pos_counts(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(double=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertTrue(np.all(np.diff(self.data.position_counts) > 0))
        self.assertFalse(np.any(self.data.data % 2))

    def test_get_data_with_gaps_in_position_counts_returns_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(gaps=True)
        importer = data.HDF5DataImporter(source=self.filename)
        importer.item = "/c1/meta/PosCountTimer"
        importer.mapping = {
            "PosCounter": "position_counts",
            "PosCountTimer": "data",
        }
        self.data.importer.append(importer)
        self.data.get_data()
        self.assertEqual(h5file.shape, len(self.data.data))


class TestTimestampData(unittest.TestCase):
    def setUp(self):
        self.data = data.TimestampData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(self.data.metadata, metadata.TimestampMetadata)

    def test_get_position_returns_position(self):
        self.data.position_counts = np.linspace(start=4, stop=23, num=20)
        self.data.data = np.linspace(start=0, stop=19, num=20)
        self.assertEqual(
            self.data.position_counts[3], self.data.get_position(3.2)
        )

    def test_get_position_with_array_returns_position_array(self):
        self.data.position_counts = np.linspace(start=4, stop=23, num=20)
        self.data.data = np.linspace(start=0, stop=19, num=20)
        np.testing.assert_array_equal(
            self.data.position_counts[[3, 5, 6]],
            self.data.get_position([3.2, 5.5, 6.8]),
        )

    def test_get_position_for_minus_one_returns_first_position(self):
        self.data.position_counts = np.linspace(start=4, stop=23, num=20)
        self.data.data = np.linspace(start=0, stop=19, num=20)
        self.assertEqual(
            self.data.position_counts[0], self.data.get_position(-1)
        )

    def test_get_position_with_minus_one_in_array(self):
        self.data.position_counts = np.linspace(start=4, stop=23, num=20)
        self.data.data = np.linspace(start=0, stop=19, num=20)
        np.testing.assert_array_equal(
            self.data.position_counts[[0, 3, 5, 6]],
            self.data.get_position([-1, 3.2, 5.5, 6.8]),
        )


class TestSinglePointChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.SinglePointChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.SinglePointChannelMetadata
        )


class TestAverageChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.AverageChannelData()

        class MockData(data.AverageChannelData):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "attempts",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.AverageChannelMetadata
        )

    def test_mean_returns_data_values(self):
        self.data.data = np.asarray([1, 2, 3])
        np.testing.assert_array_equal(self.data.data, self.data.mean)

    def test_show_info_prints_fields(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.data.show_info()
        output = temp_stdout.getvalue().strip()
        for field in ["data", "position_counts", "attempts", "mean"]:
            self.assertIn(field, output)

    def test_dataframe_contains_additional_columns(self):
        dataframe = self.data.get_dataframe()
        self.assertTrue(dataframe.columns.size)
        self.assertListEqual(
            list(dataframe.columns),
            ["data", "attempts"],
        )

    def test_join_with_positions_subset_reduces_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.attempts = np.asarray([3, 4, 3], dtype=np.int64)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = self.data.position_counts[[0, 2]]
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(data_, attribute),
                getattr(self.data, attribute)[[0, 2]],
            )
        np.testing.assert_array_equal(
            self.data.position_counts[[0, 2]], data_.position_counts
        )

    def test_join_with_positions_superset_masks_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.attempts = np.asarray([3, 4, 3], dtype=np.int64)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6], dtype=np.int64)
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(self.data, attribute), getattr(data_, attribute)[1:4]
            )
            self.assertIsInstance(
                getattr(data_, attribute), np.ma.MaskedArray
            )
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        np.testing.assert_array_equal(positions, data_.position_counts)

    def test_accessing_attempts_calls_get_data_if_data_not_loaded(self):
        _ = self.mock_data.attempts
        self.assertTrue(self.mock_data.get_data_called)


class TestIntervalChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.IntervalChannelData()

        class MockData(data.IntervalChannelData):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "counts",
            "std",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.IntervalChannelMetadata
        )

    def test_mean_returns_data_values(self):
        self.data.data = np.asarray([1, 2, 3])
        np.testing.assert_array_equal(self.data.data, self.data.mean)

    def test_dataframe_contains_additional_columns(self):
        dataframe = self.data.get_dataframe()
        self.assertTrue(dataframe.columns.size)
        self.assertListEqual(
            list(dataframe.columns),
            ["data", "counts", "std"],
        )

    def test_join_with_positions_subset_reduces_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.counts = np.asarray([3, 4, 3], dtype=np.int64)
        self.data.std = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = self.data.position_counts[[0, 2]]
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(data_, attribute),
                getattr(self.data, attribute)[[0, 2]],
            )
        np.testing.assert_array_equal(
            self.data.position_counts[[0, 2]], data_.position_counts
        )

    def test_join_with_positions_superset_masks_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.counts = np.asarray([3, 4, 3], dtype=np.int64)
        self.data.std = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6], dtype=np.int64)
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(self.data, attribute), getattr(data_, attribute)[1:4]
            )
            self.assertIsInstance(
                getattr(data_, attribute), np.ma.MaskedArray
            )
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        np.testing.assert_array_equal(positions, data_.position_counts)

    def test_accessing_counts_calls_get_data_if_data_not_loaded(self):
        _ = self.mock_data.counts
        self.assertTrue(self.mock_data.get_data_called)

    def test_accessing_std_calls_get_data_if_data_not_loaded(self):
        _ = self.mock_data.std
        self.assertTrue(self.mock_data.get_data_called)


class TestNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.NormalizedChannelData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.NormalizedChannelMetadata
        )


class TestSinglePointNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.SinglePointNormalizedChannelData()

        class MockData(data.SinglePointNormalizedChannelData):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.SinglePointNormalizedChannelMetadata
        )

    def test_dataframe_contains_additional_columns(self):
        dataframe = self.data.get_dataframe()
        self.assertTrue(dataframe.columns.size)
        self.assertListEqual(
            list(dataframe.columns),
            ["data", "normalized_data", "normalizing_data"],
        )

    def test_join_with_positions_subset_reduces_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.normalized_data = np.random.random(3)
        self.data.normalizing_data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = self.data.position_counts[[0, 2]]
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(data_, attribute),
                getattr(self.data, attribute)[[0, 2]],
            )
        np.testing.assert_array_equal(
            self.data.position_counts[[0, 2]], data_.position_counts
        )

    def test_join_with_positions_superset_masks_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.normalized_data = np.random.random(3)
        self.data.normalizing_data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6], dtype=np.int64)
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(self.data, attribute), getattr(data_, attribute)[1:4]
            )
            self.assertIsInstance(
                getattr(data_, attribute), np.ma.MaskedArray
            )
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        np.testing.assert_array_equal(positions, data_.position_counts)

    def test_accessing_normalized_data_calls_get_data_if_data_not_loaded(
        self,
    ):
        _ = self.mock_data.normalized_data
        self.assertTrue(self.mock_data.get_data_called)

    def test_accessing_normalizing_data_calls_get_data_if_data_not_loaded(
        self,
    ):
        _ = self.mock_data.normalizing_data
        self.assertTrue(self.mock_data.get_data_called)


class TestAverageNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.AverageNormalizedChannelData()

        class MockData(data.AverageNormalizedChannelData):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "attempts",
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.AverageNormalizedChannelMetadata
        )

    def test_dataframe_contains_additional_columns(self):
        dataframe = self.data.get_dataframe()
        self.assertTrue(dataframe.columns.size)
        self.assertListEqual(
            list(dataframe.columns),
            ["data", "attempts", "normalized_data", "normalizing_data"],
        )

    def test_join_with_positions_subset_reduces_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.attempts = np.asarray([3, 4, 3], dtype=np.int64)
        self.data.normalized_data = np.random.random(3)
        self.data.normalizing_data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = self.data.position_counts[[0, 2]]
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(data_, attribute),
                getattr(self.data, attribute)[[0, 2]],
            )
        np.testing.assert_array_equal(
            self.data.position_counts[[0, 2]], data_.position_counts
        )

    def test_join_with_positions_superset_masks_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.attempts = np.asarray([3, 4, 3], dtype=np.int64)
        self.data.normalized_data = np.random.random(3)
        self.data.normalizing_data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6], dtype=np.int64)
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(self.data, attribute), getattr(data_, attribute)[1:4]
            )
            self.assertIsInstance(
                getattr(data_, attribute), np.ma.MaskedArray
            )
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        np.testing.assert_array_equal(positions, data_.position_counts)

    def test_accessing_normalized_data_calls_get_data_if_data_not_loaded(
        self,
    ):
        _ = self.mock_data.normalized_data
        self.assertTrue(self.mock_data.get_data_called)

    def test_accessing_normalizing_data_calls_get_data_if_data_not_loaded(
        self,
    ):
        _ = self.mock_data.normalizing_data
        self.assertTrue(self.mock_data.get_data_called)


class TestIntervalNormalizedChannelData(unittest.TestCase):
    def setUp(self):
        self.data = data.IntervalNormalizedChannelData()

        class MockData(data.IntervalNormalizedChannelData):

            def __init__(self):
                super().__init__()
                self.get_data_called = False

            def get_data(self):
                super().get_data()
                self.get_data_called = True

        self.mock_data = MockData()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "options",
            "data",
            "position_counts",
            "counts",
            "normalized_data",
            "normalizing_data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.data, attribute))

    def test_metadata_are_of_corresponding_type(self):
        self.assertIsInstance(
            self.data.metadata, metadata.IntervalNormalizedChannelMetadata
        )

    def test_dataframe_contains_additional_columns(self):
        dataframe = self.data.get_dataframe()
        self.assertTrue(dataframe.columns.size)
        self.assertListEqual(
            list(dataframe.columns),
            ["data", "counts", "std", "normalized_data", "normalizing_data"],
        )

    def test_join_with_positions_subset_reduces_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.counts = np.asarray([3, 4, 3], dtype=np.int64)
        self.data.std = np.random.random(3)
        self.data.normalized_data = np.random.random(3)
        self.data.normalizing_data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = self.data.position_counts[[0, 2]]
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(data_, attribute),
                getattr(self.data, attribute)[[0, 2]],
            )
        np.testing.assert_array_equal(
            self.data.position_counts[[0, 2]], data_.position_counts
        )

    def test_join_with_positions_superset_masks_all_attributes(self):
        self.data.data = np.random.random(3)
        self.data.counts = np.asarray([3, 4, 3], dtype=np.int64)
        self.data.std = np.random.random(3)
        self.data.normalized_data = np.random.random(3)
        self.data.normalizing_data = np.random.random(3)
        self.data.position_counts = np.asarray([3, 4, 5], dtype=np.int64)
        positions = np.asarray([2, 3, 4, 5, 6], dtype=np.int64)
        data_ = copy.copy(self.data)
        data_.join(positions=positions)
        for attribute in data_._data_attributes:
            self.assertTrue(getattr(data_, attribute).any())
            np.testing.assert_array_equal(
                getattr(self.data, attribute), getattr(data_, attribute)[1:4]
            )
            self.assertIsInstance(
                getattr(data_, attribute), np.ma.MaskedArray
            )
        np.testing.assert_array_equal(
            self.data.position_counts, data_.position_counts[1:4]
        )
        np.testing.assert_array_equal(positions, data_.position_counts)

    def test_accessing_normalized_data_calls_get_data_if_data_not_loaded(
        self,
    ):
        _ = self.mock_data.normalized_data
        self.assertTrue(self.mock_data.get_data_called)

    def test_accessing_normalizing_data_calls_get_data_if_data_not_loaded(
        self,
    ):
        _ = self.mock_data.normalizing_data
        self.assertTrue(self.mock_data.get_data_called)


class TestDataImporter(unittest.TestCase):
    def setUp(self):
        self.importer = data.DataImporter()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
            "preprocessing",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.importer, attribute))

    def test_load_without_source_raises(self):
        self.importer.source = ""
        with self.assertRaises(ValueError):
            self.importer.load()

    def test_load_with_source_as_parameter(self):
        self.importer.source = ""
        self.importer.load(source="foo")

    def test_load_returns_data(self):

        class MockDataImporter(data.DataImporter):
            def _load(self):
                return "foo"

        importer = MockDataImporter()
        importer.source = "baz"
        self.assertTrue(importer.load())

    def test_instantiate_with_source_sets_source(self):
        source = "baz"
        importer = data.DataImporter(source=source)
        self.assertEqual(source, importer.source)


class TestHDF5DataImporter(unittest.TestCase):
    def setUp(self):
        self.importer = data.HDF5DataImporter()
        self.filename = "test.h5"
        self.item = "/c1/main/test"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def create_hdf5_file(self):
        with h5py.File(self.filename, "w") as file:
            c1 = file.create_group("c1")
            main = c1.create_group("main")
            main.create_dataset("test", data=np.ones([5, 2]))

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
            "item",
            "mapping",
            "data",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.importer, attribute))

    def test_load_without_item_raises(self):
        self.importer.source = "foo"
        with self.assertRaises(ValueError):
            self.importer.load()

    def test_load_with_item_as_parameter(self):
        self.create_hdf5_file()
        self.importer.source = self.filename
        self.importer.load(item=self.item)

    def test_load_returns_HDF5_dataset_data(self):
        self.create_hdf5_file()
        self.importer.source = self.filename
        self.importer.item = self.item
        np.testing.assert_array_equal(np.ones([5, 2]), self.importer.load())

    def test_load_sets_data_attribute(self):
        self.create_hdf5_file()
        self.importer.source = self.filename
        self.importer.item = self.item
        self.importer.load()
        np.testing.assert_array_equal(np.ones([5, 2]), self.importer.data)
