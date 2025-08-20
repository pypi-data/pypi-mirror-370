import contextlib
import os
import unittest
from io import StringIO

import h5py
import numpy as np
import pandas as pd

from evefile.boundaries import evefile
import evefile.entities.data
import evefile.entities.file


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self, set_preferred=False, add_snapshot=False):
        with h5py.File(self.filename, "w") as file:
            file.attrs["EVEH5Version"] = np.bytes_(["7"])
            file.attrs["Version"] = np.bytes_(["2.0"])
            file.attrs["XMLversion"] = np.bytes_(["9.2"])
            file.attrs["Comment"] = np.bytes_([""])
            file.attrs["Location"] = np.bytes_(["Unittest"])
            file.attrs["StartTimeISO"] = np.bytes_(["2024-06-03T12:01:32"])
            file.attrs["EndTimeISO"] = np.bytes_(["2024-06-03T12:01:37"])
            file.attrs["Simulation"] = np.bytes_(["no"])
            c1 = file.create_group("c1")
            main = c1.create_group("main")
            meta = c1.create_group("meta")
            simmot = main.create_dataset(
                "SimMot:01",
                data=np.ones(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimMot:01", "<f8")]
                    ),
                ),
            )
            simmot["PosCounter"] = np.linspace(2, 6, 5)
            simmot["SimMot:01"] = np.random.random(5)
            simmot.attrs["Name"] = np.bytes_(["foo"])
            simmot.attrs["Access"] = np.bytes_(["ca:foobar"])
            simmot.attrs["DeviceType"] = np.bytes_(["Axis"])
            simchan = main.create_dataset(
                "SimChan:01",
                data=np.ones(
                    [5],
                    dtype=np.dtype(
                        [("PosCounter", "<i4"), ("SimChan:01", "<f8")]
                    ),
                ),
            )
            simchan["PosCounter"] = np.linspace(4, 8, 5)
            simchan["SimChan:01"] = np.random.random(5)
            simchan.attrs["Name"] = np.bytes_(["bar"])
            simchan.attrs["Access"] = np.bytes_(["ca:barbaz"])
            simchan.attrs["DeviceType"] = np.bytes_(["Channel"])
            simchan.attrs["Detectortype"] = np.bytes_(["Standard"])
            data = np.ndarray(
                [9],
                dtype=np.dtype(
                    [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
                ),
            )
            poscounttimer = meta.create_dataset("PosCountTimer", data=data)
            poscounttimer.attrs["Unit"] = np.bytes_(["msecs"])
            if set_preferred:
                c1.attrs["preferredAxis"] = np.bytes_(["SimMot:01"])
                c1.attrs["preferredChannel"] = np.bytes_(["SimChan:01"])
                c1.attrs["preferredNormalizationChannel"] = np.bytes_(
                    ["SimChan:01"]
                )
            if add_snapshot:
                snapshot = c1.create_group("snapshot")
                simmot = snapshot.create_dataset(
                    "SimMot:01",
                    data=np.ndarray(
                        [2],
                        dtype=np.dtype(
                            [("PosCounter", "<i4"), ("SimMot:01", "<f8")]
                        ),
                    ),
                )
                simmot["PosCounter"] = np.asarray([1, 9])
                simmot["SimMot:01"] = np.random.random(2)
                simmot.attrs["Name"] = np.bytes_(["foo"])
                simmot.attrs["Unit"] = np.bytes_(["eV"])
                simmot.attrs["Access"] = np.bytes_(["ca:foobar"])
                simmot.attrs["DeviceType"] = np.bytes_(["Axis"])
                simchan = snapshot.create_dataset(
                    "SimChan:01",
                    data=np.ndarray(
                        [2],
                        dtype=np.dtype(
                            [("PosCounter", "<i4"), ("SimChan:01", "<f8")]
                        ),
                    ),
                )
                simchan["PosCounter"] = np.asarray([1, 9])
                simchan["SimChan:01"] = np.random.random(2)
                simchan.attrs["Name"] = np.bytes_(["bar"])
                simchan.attrs["Unit"] = np.bytes_(["A"])
                simchan.attrs["Access"] = np.bytes_(["ca:barbaz"])
                simchan.attrs["DeviceType"] = np.bytes_(["Channel"])
                simchan.attrs["Detectortype"] = np.bytes_(["Standard"])
                simchan3 = snapshot.create_dataset(
                    "SimChan:03",
                    data=np.ndarray(
                        [2],
                        dtype=np.dtype(
                            [("PosCounter", "<i4"), ("SimChan:03", "<f8")]
                        ),
                    ),
                )
                simchan3["PosCounter"] = np.asarray([1, 9])
                simchan3["SimChan:03"] = np.random.random(2)
                simchan3.attrs["Name"] = np.bytes_(["bazfoo"])
                simchan3.attrs["Unit"] = np.bytes_(["A"])
                simchan3.attrs["Access"] = np.bytes_(["ca:bazfoo"])
                simchan3.attrs["DeviceType"] = np.bytes_(["Channel"])
                simchan3.attrs["Detectortype"] = np.bytes_(["Standard"])


class TestEveFile(unittest.TestCase):
    def setUp(self):
        self.filename = "file.h5"
        self.evefile = evefile.EveFile(filename=self.filename, load=False)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        evefile.EveFile(load=False)

    def test_has_attributes(self):
        attributes = [
            "metadata",
            "log_messages",
            "data",
            "snapshots",
            "monitors",
            "position_timestamps",
            "filename",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.evefile, attribute))

    def test_setting_filename_sets_metadata_filename(self):
        filename = "foobar.h5"
        self.evefile.filename = filename
        self.assertEqual(self.evefile.metadata.filename, filename)

    def test_init_with_filename_sets_metadata_filename(self):
        filename = "foobar.h5"
        file = evefile.EveFile(filename=filename, load=False)
        self.assertEqual(filename, file.metadata.filename)

    def test_init_with_load_and_missing_filename_raises(self):
        with self.assertRaisesRegex(ValueError, "No filename given"):
            evefile.EveFile(filename="", load=True)

    def test_init_with_load_and_nonexisting_file_raises(self):
        filename = "nonexisting.h5"
        with self.assertRaisesRegex(
            FileNotFoundError, f"File {filename} does " f"not " f"exist."
        ):
            evefile.EveFile(filename=filename, load=True)

    def test_load_sets_file_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        root_mappings = {
            "eveh5_version": "7",
            "measurement_station": "Unittest",
        }
        for key, value in root_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(getattr(self.evefile.metadata, key), value)

    def test_get_data_returns_data_by_name(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        self.assertEqual(
            self.evefile.data["SimMot:01"],
            self.evefile.get_data("foo"),
        )

    def test_get_data_list_returns_data_by_name_as_array(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        self.assertEqual(
            self.evefile.data["SimMot:01"],
            self.evefile.get_data(["foo", "bar"])[0],
        )

    def test_data_have_correct_shape(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        self.assertEqual(5, len(self.evefile.data["SimChan:01"].data))
        self.assertEqual(5, len(self.evefile.data["SimMot:01"].data))

    def test_get_data_names(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        self.assertEqual(
            [item.metadata.name for item in self.evefile.data.values()],
            self.evefile.get_data_names(),
        )

    def test_get_preferred_data_returns_list(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=True)
        self.evefile = evefile.EveFile(filename=self.filename)
        self.assertIsInstance(self.evefile.get_preferred_data(), list)

    def test_get_preferred_data_contains_datasets(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=True)
        self.evefile = evefile.EveFile(filename=self.filename)
        self.assertIsInstance(
            self.evefile.get_preferred_data()[0],
            evefile.entities.data.AxisData,
        )
        self.assertIsInstance(
            self.evefile.get_preferred_data()[1],
            evefile.entities.data.ChannelData,
        )
        self.assertIsInstance(
            self.evefile.get_preferred_data()[2],
            evefile.entities.data.ChannelData,
        )

    def test_get_preferred_data_without_preferences_returns_none(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=False)
        self.evefile = evefile.EveFile(filename=self.filename)
        self.assertListEqual(
            self.evefile.get_preferred_data(), [None, None, None]
        )

    def test_get_joined_data_returns_list(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        self.assertIsInstance(self.evefile.get_joined_data(), list)

    def test_get_joined_data_returns_data_objects(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        result = self.evefile.get_joined_data()
        self.assertTrue(result)
        for item in result:
            self.assertIsInstance(item, evefile.entities.data.MeasureData)

    def test_get_joined_data_by_default_returns_all_data_objects(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        result = self.evefile.get_joined_data()
        self.assertTrue(result)
        self.assertEqual(len(self.evefile.data), len(result))

    def test_get_joined_data_joins_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        result = self.evefile.get_joined_data()
        positions = np.union1d(
            self.evefile.data["SimMot:01"].position_counts,
            self.evefile.data["SimChan:01"].position_counts,
        )
        for item in result:
            self.assertEqual(len(positions), len(item.position_counts))

    def test_get_joined_data_uses_correct_mode(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        result = self.evefile.get_joined_data(mode="AxisAndChannelPositions")
        positions = np.intersect1d(
            self.evefile.data["SimMot:01"].position_counts,
            self.evefile.data["SimChan:01"].position_counts,
        )
        for item in result:
            self.assertEqual(len(positions), len(item.position_counts))

    def test_show_info_prints_metadata(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.evefile.show_info()
        output = temp_stdout.getvalue().strip()
        self.assertIn("METADATA", output)
        self.assertIn("filename: ", output)

    def test_show_info_prints_log_messages(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        log_message = evefile.entities.file.LogMessage()
        log_message.from_string("2025-08-12T09:06:05: Lorem ipsum")
        self.evefile.log_messages.append(log_message)
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.evefile.show_info()
        output = temp_stdout.getvalue().strip()
        self.assertIn("LOG MESSAGES", output)
        self.assertIn(": Lorem ipsum", output)

    def test_show_info_prints_data(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.evefile.show_info()
        output = temp_stdout.getvalue().strip()
        self.assertIn(f"\nDATA", output)

    def test_show_info_prints_snapshots(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=True, add_snapshot=True)
        self.evefile = evefile.EveFile(filename=self.filename)
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.evefile.show_info()
        output = temp_stdout.getvalue().strip()
        self.assertIn(f"\nSNAPSHOTS", output)

    def test_show_info_prints_monitors(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=True, add_snapshot=True)
        self.evefile = evefile.EveFile(filename=self.filename)
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.evefile.show_info()
        output = temp_stdout.getvalue().strip()
        self.assertIn(f"\nMONITORS", output)
        # print(output)

    def test_get_dataframe_returns_dataframe(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create(set_preferred=True, add_snapshot=True)
        self.evefile = evefile.EveFile(filename=self.filename)
        dataframe = self.evefile.get_dataframe()
        self.assertIsInstance(dataframe, pd.DataFrame)

    def test_dataframe_by_default_contains_all_data_objects(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        dataframe = self.evefile.get_dataframe()
        self.assertTrue(dataframe.columns.size)
        self.assertListEqual(
            list(dataframe.columns),
            [item.metadata.name for item in self.evefile.data.values()],
        )

    def test_dataframe_with_name_of_data_object(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        data_name = "foo"
        dataframe = self.evefile.get_dataframe(data=[data_name])
        self.assertTrue(dataframe.columns.size)
        self.assertListEqual(list(dataframe.columns), [data_name])

    def test_dataframe_with_id_of_data_object(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        data_name = "SimMot:01"
        dataframe = self.evefile.get_dataframe(data=[data_name])
        self.assertTrue(dataframe.columns.size)
        self.assertListEqual(
            list(dataframe.columns),
            [self.evefile.data[data_name].metadata.name],
        )

    def test_dataframe_contains_index_name(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        dataframe = self.evefile.get_dataframe()
        self.assertEqual("position", dataframe.index.name)

    def test_get_dataframe_uses_correct_mode(self):
        h5file = DummyHDF5File(filename=self.filename)
        h5file.create()
        self.evefile = evefile.EveFile(filename=self.filename)
        dataframe = self.evefile.get_dataframe(mode="AxisAndChannelPositions")
        positions = np.intersect1d(
            self.evefile.data["SimMot:01"].position_counts,
            self.evefile.data["SimChan:01"].position_counts,
        )
        self.assertEqual(len(positions), len(dataframe.index))
