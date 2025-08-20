import datetime
import logging
import os
import unittest

import numpy as np

import evefile.boundaries.evefile
from evefile.controllers import version_mapping
import evefile.entities.data


class MockHDF5Item:
    def __init__(self, name="", filename=""):
        self.filename = filename
        self.name = name
        self.attributes = {}


class MockHDF5Dataset(MockHDF5Item):
    def __init__(self, name="", filename=""):
        super().__init__(name=name, filename=filename)
        self.data = None
        self.get_data_called = False
        self.dtype = np.dtype(
            [("PosCounter", "<i4"), (name.split("/")[-1], "<f8")]
        )

    @property
    def shape(self):
        if self.data is not None:
            shape = self.data.shape
        else:
            shape = (0,)
        return shape

    def get_data(self):
        self.get_data_called = True


class MockHDF5Group(MockHDF5Item):
    def __init__(self, name="", filename=""):
        super().__init__(name=name, filename=filename)
        self._items = {}

    def __iter__(self):
        for item in self._items.values():
            yield item

    def add_item(self, item):
        name = item.name.split("/")[-1]
        setattr(self, name, item)
        self._items[name] = item

    def remove_item(self, item):
        name = item.name.split("/")[-1]
        delattr(self, name)
        self._items.pop(name)

    def item_names(self):
        return list(self._items.keys())


class MockEveH5(MockHDF5Group):

    # noinspection PyUnresolvedReferences
    def __init__(self):
        super().__init__()
        self.filename = "test.h5"
        self.name = "/"
        self.attributes = {
            "EVEH5Version": "7",
            "Location": "TEST",
            "Version": "2.0",
            "XMLversion": "9.2",
            "Comment": "",
            "Simulation": "no",
            "SCML-Author": "biskup02@a23bashful",
            "SCML-Name": "test.scml",
            "StartDate": "03.06.2024",
            "StartTime": "12:01:32",
            "StartTimeISO": "2024-06-03T12:01:32",
            "EndTimeISO": "2024-06-03T12:01:37",
        }
        self.add_item(MockHDF5Group(name="/c1", filename=self.filename))
        self.c1.attributes = {
            "EndTimeISO": "2024-06-03T12:01:37",
            "StartDate": "03.06.2024",
            "StartTime": "12:01:32",
            "StartTimeISO": "2024-06-03T12:01:32",
            "preferredAxis": "OMS58:io1501003",
            "preferredChannel": "A2980:22704chan1",
            "preferredNormalizationChannel": "A2980:22704chan1",
        }
        self.c1.add_item(
            MockHDF5Group(name="/c1/meta", filename=self.filename)
        )
        poscounttimer = MockHDF5Dataset(
            name="/c1/meta/PosCountTimer", filename=self.filename
        )
        poscounttimer.dtype = np.dtype(
            [("PosCounter", "<i4"), ("PosCountTimer", "<i4")]
        )
        poscounttimer.attributes = {"Unit": "msecs"}
        self.c1.meta.add_item(poscounttimer)


class MockEveH5v4(MockEveH5):

    # noinspection PyUnresolvedReferences
    def __init__(self):
        super().__init__()
        self.attributes.update(
            {
                "EVEH5Version": "4",
                "Location": "TEST",
                "Version": "1.27",
                "XMLversion": "5.0",
            }
        )
        # Only starting with v4
        self.c1.add_item(
            MockHDF5Group(name="/c1/main", filename=self.filename)
        )
        self.c1.add_item(
            MockHDF5Group(name="/c1/snapshot", filename=self.filename)
        )

    # noinspection PyUnresolvedReferences
    def add_singlepoint_detector_data(self, normalized=False):
        names = [
            "A2980:gw24103chan1",
            "K0617:gw24126chan1",
            "mlsCurrent:Mnt1chan1",
        ]
        for name in names:
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
                "Unit": "mA",
                "Detectortype": "Standard",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{name}", "f8"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            # noinspection PyUnresolvedReferences
            self.c1.main.add_item(dataset)
        if normalized:
            name = "K0617:gw24126chan1"
            normalized = "A2980:gw24103chan1"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/normalized/{name}__{normalized}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
                "Unit": "mA",
                "Detectortype": "Standard",
                "channel": name,
                "normalizeId": normalized,
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{name}", "f8"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(MockHDF5Group(name="/c1/main/normalized"))
            self.c1.main.normalized.add_item(dataset)
        return names

    # noinspection PyUnresolvedReferences
    def add_interval_detector_data(self, normalized=False):
        self.c1.main.add_item(MockHDF5Group(name="/c1/main/standarddev"))
        if normalized:
            basename = "bIICurrent:Mnt1chan1"
            name = f"{basename}__bIICurrent:Mnt1lifeTimechan1"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/normalized/{name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{basename}",
                "Name": basename,
                "Detectortype": "Interval",
                "channel": basename,
                "normalizeId": name.split("__")[1],
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{basename}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{basename}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(MockHDF5Group(name="/c1/main/normalized"))
            self.c1.main.normalized.add_item(dataset)
            # Non-normalized dataset
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{basename}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{basename}",
                "Name": basename,
                "Detectortype": "Standard",
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{basename}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{basename}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(dataset)
        else:
            name = "mlsCurrent:Mnt1chan1"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
                "Detectortype": "Interval",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{name}", "f8"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            # noinspection PyUnresolvedReferences
            self.c1.main.add_item(dataset)
        metadata = "Count"
        dataset = MockHDF5Dataset(
            name=f"/c1/main/standarddev/{name}__{metadata}",
            filename=self.filename,
        )
        dataset.attributes = {
            "Name": name,
            "channel": name,
        }
        dtype = np.dtype(
            [
                ("PosCounter", "<i4"),
                (f"{metadata}", "f8"),
            ]
        )
        data_ = np.ndarray([2], dtype=dtype)
        data_["PosCounter"] = np.asarray([2, 5])
        data_[f"{metadata}"] = [42.0, 42.0]
        dataset.data = data_
        dataset.dtype = dtype
        # noinspection PyUnresolvedReferences
        self.c1.main.standarddev.add_item(dataset)
        metadata = "TrigIntv-StdDev"
        dataset = MockHDF5Dataset(
            name=f"/c1/main/standarddev/{name}__{metadata}",
            filename=self.filename,
        )
        dataset.attributes = {
            "Name": name,
            "channel": name,
        }
        dtype = np.dtype(
            [
                ("PosCounter", "<i4"),
                ("TriggerIntv", "f8"),
                ("StandardDeviation", "f8"),
            ]
        )
        data_ = np.ndarray([2], dtype=dtype)
        data_["PosCounter"] = np.asarray([2, 5])
        data_["TriggerIntv"] = [0.1, 0.1]
        data_["StandardDeviation"] = [42.21, 42.21]
        dataset.data = data_
        dataset.dtype = dtype
        # noinspection PyUnresolvedReferences
        self.c1.main.standarddev.add_item(dataset)
        return name

    # noinspection PyUnresolvedReferences
    def add_average_detector_data(self, maxdev=False, normalized=False):
        self.c1.main.add_item(MockHDF5Group(name="/c1/main/averagemeta"))
        if normalized:
            basename = "bIICurrent:Mnt1chan1"
            normalize_name = "bIICurrent:Mnt1lifeTimechan1"
            name = f"{basename}__{normalize_name}"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/normalized/{name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{basename}",
                "Name": basename,
                "Detectortype": "Standard",
                "channel": basename,
                "normalizeId": normalized,
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{basename}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{basename}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(MockHDF5Group(name="/c1/main/normalized"))
            self.c1.main.normalized.add_item(dataset)
            # Non-normalized dataset
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{basename}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{basename}",
                "Name": basename,
                "Detectortype": "Standard",
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{basename}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{basename}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(dataset)
            # Normalizing dataset
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{normalize_name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{normalize_name}",
                "Name": normalize_name,
                "Detectortype": "Standard",
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{normalize_name}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{normalize_name}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.main.add_item(dataset)
        else:
            name = "mlsCurrent:Mnt1chan1"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/{name}", filename=self.filename
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
                "Detectortype": "Standard",
            }
            data_ = np.ndarray(
                [2],
                dtype=np.dtype(
                    [
                        ("PosCounter", "<i4"),
                        (f"{name}", "f8"),
                    ]
                ),
            )
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            # noinspection PyUnresolvedReferences
            self.c1.main.add_item(dataset)
        metadata = "AverageCount"
        dataset = MockHDF5Dataset(
            name=f"/c1/main/averagemeta/{name}__{metadata}",
            filename=self.filename,
        )
        dataset.attributes = {
            "Name": name,
            "channel": name,
        }
        dtype = np.dtype(
            [
                ("PosCounter", "<i4"),
                ("AverageCount", "<i4"),
                ("Preset", "<i4"),
            ]
        )
        data_ = np.ndarray([2], dtype=dtype)
        data_["PosCounter"] = np.asarray([2, 5])
        data_["AverageCount"] = [3, 3]
        data_["Preset"] = [3, 3]
        dataset.data = data_
        dataset.dtype = dtype
        # noinspection PyUnresolvedReferences
        self.c1.main.averagemeta.add_item(dataset)
        if maxdev:
            metadata = "Attempts"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/averagemeta/{name}__{metadata}",
                filename=self.filename,
            )
            dataset.attributes = {
                "Name": name,
                "channel": name,
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    ("Attempts", "<i4"),
                    ("MaxAttempts", "<i4"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_["Attempts"] = [1, 1]
            data_["MaxAttempts"] = [4, 4]
            dataset.data = data_
            dataset.dtype = dtype
            # noinspection PyUnresolvedReferences
            self.c1.main.averagemeta.add_item(dataset)
            metadata = "Limit-MaxDev"
            dataset = MockHDF5Dataset(
                name=f"/c1/main/averagemeta/{name}__{metadata}",
                filename=self.filename,
            )
            dataset.attributes = {
                "Name": name,
                "channel": name,
            }
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    ("Limit", "f8"),
                    ("maxDeviation", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_["Limit"] = [21.42, 21.42]
            data_["maxDeviation"] = [0.21, 0.21]
            dataset.data = data_
            dataset.dtype = dtype
            # noinspection PyUnresolvedReferences
            self.c1.main.averagemeta.add_item(dataset)
        return name

    # noinspection PyUnresolvedReferences
    def add_axes_snapshot_data(self):
        # Axes have a unit attribute
        axes_names = [
            "SimMt:testrack01000",
            "SimMt:testrack01001",
            "SimMt:testrack01002",
            "SimMt:testrack01003",
            "SimMt:testrack01004",
            "SimMt:testrack01005",
        ]
        # Nonnumeric axes have no unit attribute
        nonnumeric_axes_names = [
            "DiscPosSimMt:testrack01000",
            "DiscPosSimMt:testrack01001",
        ]
        for name in [*axes_names, *nonnumeric_axes_names]:
            dataset = MockHDF5Dataset(
                name=f"/c1/snapshot/{name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Axis",
                "Access": f"ca:{name}",
                "Name": name,
            }
            if name not in nonnumeric_axes_names:
                dataset.attributes["Unit"] = "degrees"
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{name}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.snapshot.add_item(dataset)
        return [*axes_names, *nonnumeric_axes_names]

    # noinspection PyUnresolvedReferences
    def add_channel_snapshot_data(self):
        # Channels need not have a unit attribute, example: SmCounter-det
        channel_names = [
            "SmCounter-det",
            "U125P:ioIDB00GapMotchan1",
            "bIICurrent:Mnt1chan1",
            "bIICurrent:Mnt1lifeTimechan1",
        ]
        # Nonnumeric channels definitely have no unit attribute
        nonnumeric_channel_names = [
            "bIICurrent:Mnt1topupStatechan1",
            "wftest:filenamechan1",
        ]
        for name in [*channel_names, *nonnumeric_channel_names]:
            dataset = MockHDF5Dataset(
                name=f"/c1/snapshot/{name}",
                filename=self.filename,
            )
            dataset.attributes = {
                "DeviceType": "Channel",
                "Access": f"ca:{name}",
                "Name": name,
            }
            if name not in ["SmCounter-det", *nonnumeric_channel_names]:
                dataset.attributes["Unit"] = "mA"
            dtype = np.dtype(
                [
                    ("PosCounter", "<i4"),
                    (f"{name}", "f8"),
                ]
            )
            data_ = np.ndarray([2], dtype=dtype)
            data_["PosCounter"] = np.asarray([2, 5])
            data_[f"{name}"] = [42.0, 42.0]
            dataset.data = data_
            self.c1.snapshot.add_item(dataset)
        return [*channel_names, *nonnumeric_channel_names]


class MockEveH5v5(MockEveH5v4):
    pass


class MockFile:
    pass


class TestVersionMapperFactory(unittest.TestCase):

    def setUp(self):
        self.factory = version_mapping.VersionMapperFactory()
        self.eveh5 = MockEveH5()
        self.logger = logging.getLogger(name="evedata")

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "eveh5",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.factory, attribute))

    def test_get_mapper_returns_mapper(self):
        self.factory.eveh5 = self.eveh5
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapper)

    def test_get_mapper_with_eveh5_argument_sets_eveh5_property(self):
        self.factory.get_mapper(eveh5=self.eveh5)
        self.assertEqual(self.factory.eveh5, self.eveh5)

    def test_get_mapper_without_eveh5_raises(self):
        with self.assertRaises(ValueError):
            self.factory.get_mapper()

    def test_get_mapper_returns_correct_mapper(self):
        self.factory.eveh5 = self.eveh5
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapperV7)

    def test_get_mapper_with_fractional_version_returns_correct_mapper(self):
        self.eveh5.attributes["EVEH5Version"] = "7.0"
        self.factory.eveh5 = self.eveh5
        mapper = self.factory.get_mapper()
        self.assertIsInstance(mapper, version_mapping.VersionMapperV7)

    def test_get_mapper_with_unknown_version_raises(self):
        self.eveh5.attributes["EVEH5Version"] = "0"
        self.factory.eveh5 = self.eveh5
        with self.assertRaises(AttributeError):
            self.factory.get_mapper()

    def test_get_mapper_with_unknown_version_logs(self):
        self.eveh5.attributes["EVEH5Version"] = "0"
        self.factory.eveh5 = self.eveh5
        self.logger.setLevel(logging.ERROR)
        self.logger.addHandler(logging.NullHandler())
        with self.assertLogs(level=logging.ERROR) as captured:
            with self.assertRaises(AttributeError):
                self.factory.get_mapper()
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(
                captured.records[0].getMessage(),
                "No mapper for version 0",
            )

    def test_get_mapper_sets_source_in_mapper(self):
        self.factory.eveh5 = self.eveh5
        mapper = self.factory.get_mapper()
        self.assertEqual(mapper.source, self.eveh5)


class TestVersionMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapper()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "source",
            "destination",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.mapper, attribute))

    def test_map_without_source_raises(self):
        self.mapper.source = None
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_without_destination_raises(self):
        self.mapper.source = MockEveH5()
        with self.assertRaises(ValueError):
            self.mapper.map()

    def test_map_with_source_and_destination_parameters(self):
        self.mapper.source = None
        self.mapper.map(source=MockEveH5(), destination=MockFile())

    def test_get_hdf5_dataset_importer_returns_importer(self):
        self.assertIsInstance(
            self.mapper.get_hdf5_dataset_importer(dataset=MockHDF5Dataset()),
            evefile.entities.data.HDF5DataImporter,
        )

    def test_get_hdf5_dataset_importer_sets_source_and_item(self):
        dataset = MockHDF5Dataset(filename="test.h5", name="/c1/main/foobar")
        importer = self.mapper.get_hdf5_dataset_importer(dataset=dataset)
        self.assertEqual(dataset.filename, importer.source)
        self.assertEqual(dataset.name, importer.item)

    def test_get_hdf5_dataset_importer_sets_mapping(self):
        dataset = MockHDF5Dataset(filename="test.h5", name="/c1/main/foobar")
        mapping = {0: "foobar", 1: "barbaz"}
        importer = self.mapper.get_hdf5_dataset_importer(
            dataset=dataset, mapping=mapping
        )
        mapping_dict = {
            dataset.dtype.names[0]: mapping[0],
            dataset.dtype.names[1]: mapping[1],
        }
        self.assertDictEqual(mapping_dict, importer.mapping)


class TestVersionMapperV5(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV5()
        self.source = MockEveH5v5()
        self.destination = evefile.boundaries.evefile.EveFile(load=False)
        self.logger = logging.getLogger(name="evedata")
        self.logger.setLevel(logging.ERROR)

    def tearDown(self):
        if os.path.exists(self.source.filename):
            os.remove(self.source.filename)

    def destination_data(self, name=""):
        return self.destination.data[name]

    def test_instantiate_class(self):
        pass

    def test_map_sets_file_metadata_from_root_group(self):
        self.mapper.source = self.source
        self.mapper.map(destination=self.destination)
        # destination: source
        root_mappings = {
            "eveh5_version": "EVEH5Version",
            "eve_version": "Version",
            "xml_version": "XMLversion",
            "measurement_station": "Location",
            "description": "Comment",
        }
        for key, value in root_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(
                    getattr(self.destination.metadata, key),
                    self.mapper.source.attributes[value],
                )

    def test_map_sets_file_metadata_from_root_group_without_comment(self):
        self.mapper.source = self.source
        self.mapper.source.attributes.pop("Comment")
        self.mapper.map(destination=self.destination)
        # destination: source
        root_mappings = {
            "eveh5_version": "EVEH5Version",
            "eve_version": "Version",
            "xml_version": "XMLversion",
            "measurement_station": "Location",
        }
        for key, value in root_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(
                    getattr(self.destination.metadata, key),
                    self.mapper.source.attributes[value],
                )

    def test_map_sets_file_metadata_from_c1_group(self):
        self.mapper.source = self.source
        self.mapper.map(destination=self.destination)
        # destination: source
        c1_mappings = {
            "preferred_axis": "preferredAxis",
            "preferred_channel": "preferredChannel",
            "preferred_normalisation_channel": "preferredNormalizationChannel",
        }
        for key, value in c1_mappings.items():
            with self.subTest(key=key, val=value):
                # noinspection PyUnresolvedReferences
                self.assertEqual(
                    getattr(self.destination.metadata, key),
                    self.mapper.source.c1.attributes[value],
                )

    def test_map_converts_date_to_datetime(self):
        self.mapper.source = self.source
        keys_to_drop = [
            key
            for key in self.mapper.source.attributes.keys()
            if "ISO" in key
        ]
        for key in keys_to_drop:
            self.mapper.source.attributes.pop(key)
        self.mapper.map(destination=self.destination)
        self.assertEqual(
            self.destination.metadata.start,
            datetime.datetime.strptime(
                f"{self.mapper.source.attributes['StartDate']} "
                f"{self.mapper.source.attributes['StartTime']}",
                "%d.%m.%Y %H:%M:%S",
            ),
        )

    def test_map_sets_end_date_to_unix_start_time(self):
        self.mapper.source = self.source
        keys_to_drop = [
            key
            for key in self.mapper.source.attributes.keys()
            if "ISO" in key
        ]
        for key in keys_to_drop:
            self.mapper.source.attributes.pop(key)
        self.mapper.map(destination=self.destination)
        self.assertEqual(
            self.destination.metadata.end, datetime.datetime(1970, 1, 1)
        )

    def test_map_adds_log_messages(self):
        log_messages = [
            b"2024-07-25T10:04:03: Lorem ipsum",
            b"2024-07-25T10:05:23: dolor sit amet",
        ]
        self.mapper.source = self.source
        self.mapper.source.LiveComment = MockHDF5Dataset()
        self.mapper.source.LiveComment.data = np.asarray(log_messages)
        self.mapper.map(destination=self.destination)
        self.assertTrue(self.mapper.source.LiveComment.get_data_called)
        self.assertTrue(self.destination.log_messages)
        self.assertIsInstance(
            self.destination.log_messages[0],
            evefile.entities.file.LogMessage,
        )
        timestamp, message = log_messages[0].decode().split(": ", maxsplit=1)
        self.assertEqual(
            datetime.datetime.fromisoformat(timestamp),
            self.destination.log_messages[0].timestamp,
        )
        self.assertEqual(message, self.destination.log_messages[0].message)

    def test_map_adds_monitor_datasets(self):
        self.mapper.source = self.source
        monitor1 = MockHDF5Dataset(name="/device/monitor")
        monitor1.attributes = {"Name": "mymonitor", "Access": "ca:foobar"}
        monitor2 = MockHDF5Dataset(name="/device/monitor2")
        monitor2.attributes = {"Name": "mymonitor2", "Access": "ca:barbaz"}
        self.mapper.source.add_item(MockHDF5Group(name="/device"))
        # noinspection PyUnresolvedReferences
        self.mapper.source.device.add_item(monitor1)
        # noinspection PyUnresolvedReferences
        self.mapper.source.device.add_item(monitor2)
        self.mapper.map(destination=self.destination)
        for monitor in self.destination.monitors.values():
            self.assertIsInstance(
                monitor,
                evefile.entities.data.MonitorData,
            )
        self.assertEqual(
            "monitor",
            self.destination.monitors["monitor"].metadata.id,
        )
        self.assertEqual(
            monitor1.attributes["Name"],
            self.destination.monitors["monitor"].metadata.name,
        )
        self.assertEqual(
            monitor1.attributes["Access"].split(":", maxsplit=1)[1],
            self.destination.monitors["monitor"].metadata.pv,
        )
        self.assertEqual(
            monitor1.attributes["Access"].split(":", maxsplit=1)[0],
            self.destination.monitors["monitor"].metadata.access_mode,
        )

    def test_monitor_datasets_contain_importer(self):
        self.mapper.source = self.source
        monitor = MockHDF5Dataset(name="/device/monitor")
        monitor.filename = "test.h5"
        monitor.attributes = {"Name": "mymonitor", "Access": "ca:foobar"}
        self.mapper.source.add_item(MockHDF5Group(name="/device"))
        # noinspection PyUnresolvedReferences
        self.mapper.source.device.add_item(monitor)
        self.mapper.map(destination=self.destination)
        self.assertEqual(
            "/device/monitor",
            self.destination.monitors["monitor"].importer[0].item,
        )
        self.assertEqual(
            monitor.filename,
            self.destination.monitors["monitor"].importer[0].source,
        )
        mapping_dict = {
            monitor.dtype.names[0]: "milliseconds",
            monitor.dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict,
            self.destination.monitors["monitor"].importer[0].mapping,
        )

    # noinspection PyUnresolvedReferences
    def test_map_adds_timestampdata_dataset(self):
        self.mapper.source = self.source
        self.mapper.map(destination=self.destination)
        self.assertIsInstance(
            self.destination.position_timestamps,
            evefile.entities.data.TimestampData,
        )
        self.assertEqual(
            self.mapper.source.c1.meta.PosCountTimer.attributes["Unit"],
            self.destination.position_timestamps.metadata.unit,
        )
        self.assertEqual(
            self.mapper.source.c1.meta.PosCountTimer.name,
            self.destination.position_timestamps.importer[0].item,
        )
        self.assertEqual(
            self.mapper.source.c1.meta.PosCountTimer.filename,
            self.destination.position_timestamps.importer[0].source,
        )
        mapping_dict = {
            self.mapper.source.c1.meta.PosCountTimer.dtype.names[
                0
            ]: "position_counts",
            self.mapper.source.c1.meta.PosCountTimer.dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict,
            self.destination.position_timestamps.importer[0].mapping,
        )

    def test_map_adds_axis_datasets(self):
        self.mapper.source = self.source
        axis1 = MockHDF5Dataset(name="/c1/main/axis1")
        axis1.attributes = {
            "Name": "myaxis1",
            "Unit": "eV",
            "Access": "ca:foobar",
            "DeviceType": "Axis",
        }
        axis2 = MockHDF5Dataset(name="/c1/main/axis2")
        axis2.attributes = {
            "Name": "myaxis2",
            "Unit": "nm",
            "Access": "ca:barbaz",
            "DeviceType": "Axis",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis1)
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis2)
        self.mapper.map(destination=self.destination)
        for axis in self.destination.data.values():
            self.assertIsInstance(
                axis,
                evefile.entities.data.AxisData,
            )
        self.assertEqual(
            "axis1",
            self.destination_data("axis1").metadata.id,
        )
        self.assertEqual(
            axis1.attributes["Name"],
            self.destination_data("axis1").metadata.name,
        )
        self.assertEqual(
            axis1.attributes["Unit"],
            self.destination_data("axis1").metadata.unit,
        )
        self.assertEqual(
            axis1.attributes["Access"].split(":", maxsplit=1)[1],
            self.destination_data("axis1").metadata.pv,
        )
        self.assertEqual(
            axis1.attributes["Access"].split(":", maxsplit=1)[0],
            self.destination_data("axis1").metadata.access_mode,
        )

    def test_axis_datasets_contain_importer(self):
        self.mapper.source = self.source
        axis1 = MockHDF5Dataset(name="/c1/main/axis1")
        axis1.attributes = {
            "Name": "myaxis1",
            "Access": "ca:foobar",
            "DeviceType": "Axis",
        }
        axis2 = MockHDF5Dataset(name="/c1/main/axis2")
        axis2.attributes = {
            "Name": "myaxis2",
            "Access": "ca:barbaz",
            "DeviceType": "Axis",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis1)
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis2)
        self.mapper.map(destination=self.destination)
        self.assertEqual(
            "/c1/main/axis1", self.destination_data("axis1").importer[0].item
        )
        self.assertEqual(
            axis1.filename, self.destination_data("axis1").importer[0].source
        )
        mapping_dict = {
            axis1.dtype.names[0]: "position_counts",
            axis1.dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data("axis1").importer[0].mapping
        )

    def test_map_axis_dataset_removes_dataset_from_list2map(self):
        self.mapper.source = self.source
        axis1 = MockHDF5Dataset(name="/c1/main/axis1")
        axis1.attributes = {
            "Name": "myaxis1",
            "Access": "ca:foobar",
            "DeviceType": "Axis",
        }
        # noinspection PyUnresolvedReferences
        self.mapper.source.c1.main.add_item(axis1)
        self.mapper.map(destination=self.destination)
        self.assertNotIn("axis1", self.mapper.datasets2map_in_main)

    # noinspection PyUnresolvedReferences
    def test_map_singlepoint_datasets_removes_from_list2map(self):
        self.mapper.source = self.source
        self.mapper.source.add_singlepoint_detector_data(normalized=False)
        self.mapper.map(destination=self.destination)
        self.assertFalse(self.mapper.datasets2map_in_main)

    # noinspection PyUnresolvedReferences
    def test_map_singlepoint_datasets_adds_datasets(self):
        self.mapper.source = self.source
        datasets = self.mapper.source.add_singlepoint_detector_data(
            normalized=False
        )
        self.mapper.map(destination=self.destination)
        for dataset in datasets:
            h5_dataset = getattr(self.mapper.source.c1.main, dataset)
            self.assertIn(dataset, self.destination.data.keys())
            self.assertIsInstance(
                self.destination_data(dataset),
                evefile.entities.data.SinglePointChannelData,
            )
            self.assertEqual(
                dataset,
                self.destination_data(dataset).metadata.id,
            )
            self.assertEqual(
                h5_dataset.attributes["Name"],
                self.destination_data(dataset).metadata.name,
            )
            self.assertEqual(
                h5_dataset.attributes["Unit"],
                self.destination_data(dataset).metadata.unit,
            )
            self.assertEqual(
                h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
                self.destination_data(dataset).metadata.pv,
            )
            self.assertEqual(
                h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
                self.destination_data(dataset).metadata.access_mode,
            )

    # noinspection PyUnresolvedReferences
    def test_map_singlepoint_datasets_adds_importer(self):
        self.mapper.source = self.source
        datasets = self.mapper.source.add_singlepoint_detector_data(
            normalized=False
        )
        self.mapper.map(destination=self.destination)
        for dataset in datasets:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                self.destination_data(dataset).importer[0].source,
            )
            mapping_dict = {
                getattr(self.mapper.source.c1.main, dataset).dtype.names[
                    0
                ]: "position_counts",
                getattr(self.mapper.source.c1.main, dataset).dtype.names[
                    1
                ]: "data",
            }
            self.assertDictEqual(
                mapping_dict,
                self.destination_data(dataset).importer[0].mapping,
            )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_singlepoint_datasets_adds_datasets(self):
        self.mapper.source = self.source
        self.mapper.source.add_singlepoint_detector_data(normalized=True)
        dataset = "K0617:gw24126chan1"
        normalizing = "K0617:gw24126chan1__A2980:gw24103chan1"
        self.mapper.map(destination=self.destination)
        self.assertIn(dataset, self.destination.data.keys())
        self.assertIsInstance(
            self.destination_data(dataset),
            evefile.entities.data.SinglePointNormalizedChannelData,
        )
        h5_dataset = getattr(
            self.mapper.source.c1.main.normalized, normalizing
        )
        self.assertEqual(
            h5_dataset.attributes["normalizeId"],
            self.destination_data(dataset).metadata.normalize_id,
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_singlepoint_datasets_adds_importer(self):
        self.mapper.source = self.source
        self.mapper.source.add_singlepoint_detector_data(normalized=True)
        dataset = "K0617:gw24126chan1"
        normalizing = "K0617:gw24126chan1__A2980:gw24103chan1"
        self.mapper.map(destination=self.destination)
        for importer in self.destination_data(dataset).importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, normalizing
            ).dtype.names[1]: "normalized_data",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[1].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main, normalizing.split("__")[1]
            ).dtype.names[1]: "normalizing_data",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[2].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_interval_dataset_removes_from_list2map(self):
        self.mapper.source = self.source
        self.mapper.source.add_interval_detector_data(normalized=False)
        self.mapper.map(destination=self.destination)
        self.assertFalse(self.mapper.datasets2map_in_main)

    # noinspection PyUnresolvedReferences
    def test_map_interval_dataset_adds_dataset(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=False
        )
        self.mapper.map(destination=self.destination)
        h5_dataset = getattr(self.mapper.source.c1.main, dataset)
        self.assertIn(dataset, self.destination.data.keys())
        self.assertIsInstance(
            self.destination_data(dataset),
            evefile.entities.data.IntervalChannelData,
        )
        self.assertEqual(
            dataset,
            self.destination_data(dataset).metadata.id,
        )
        self.assertEqual(
            h5_dataset.attributes["Name"],
            self.destination_data(dataset).metadata.name,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
            self.destination_data(dataset).metadata.pv,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
            self.destination_data(dataset).metadata.access_mode,
        )

    def test_map_interval_channel_sets_trigger_interval(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=False
        )
        self.mapper.map(destination=self.destination)
        # noinspection PyUnresolvedReferences
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.standarddev,
                f"{dataset}__TrigIntv-StdDev",
            ).data["TriggerIntv"][0],
            self.destination_data(dataset).metadata.trigger_interval,
        )

    # noinspection PyUnresolvedReferences
    def test_map_interval_dataset_adds_importer(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=False
        )
        self.mapper.map(destination=self.destination)
        for importer in self.destination_data(dataset).importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                0
            ]: "position_counts",
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[0].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.standarddev, f"{dataset}__Count"
            ).dtype.names[1]: "counts",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[1].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.standarddev,
                f"{dataset}__TrigIntv-StdDev",
            ).dtype.names[2]: "std",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[2].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_interval_dataset_adds_dataset(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=True
        )
        self.mapper.map(destination=self.destination)
        h5_dataset = getattr(self.mapper.source.c1.main.normalized, dataset)
        self.assertIn(dataset, self.destination.data.keys())
        self.assertIsInstance(
            self.destination_data(dataset),
            evefile.entities.data.IntervalNormalizedChannelData,
        )
        self.assertEqual(
            dataset,
            self.destination_data(dataset).metadata.id,
        )
        self.assertEqual(
            h5_dataset.attributes["Name"],
            self.destination_data(dataset).metadata.name,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
            self.destination_data(dataset).metadata.pv,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
            self.destination_data(dataset).metadata.access_mode,
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_interval_dataset_adds_importer(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_interval_detector_data(
            normalized=True
        )
        self.mapper.map(destination=self.destination)
        for importer in self.destination_data(dataset).importer:
            self.assertEqual(
                getattr(
                    self.mapper.source.c1.main.normalized, dataset
                ).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[0]: "position_counts",
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[1]: "data",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[0].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.standarddev, f"{dataset}__Count"
            ).dtype.names[1]: "counts",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[1].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.standarddev,
                f"{dataset}__TrigIntv-StdDev",
            ).dtype.names[2]: "std",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[2].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[1]: "normalized_data",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[3].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_average_dataset_removes_from_list2map(self):
        self.mapper.source = self.source
        self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=False
        )
        self.mapper.map(destination=self.destination)
        self.assertFalse(self.mapper.datasets2map_in_main)

    # noinspection PyUnresolvedReferences
    def test_map_average_dataset_adds_dataset(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=False
        )
        self.mapper.map(destination=self.destination)
        h5_dataset = getattr(self.mapper.source.c1.main, dataset)
        self.assertIn(dataset, self.destination.data.keys())
        self.assertIsInstance(
            self.destination_data(dataset),
            evefile.entities.data.AverageChannelData,
        )
        self.assertEqual(
            dataset,
            self.destination_data(dataset).metadata.id,
        )
        self.assertEqual(
            h5_dataset.attributes["Name"],
            self.destination_data(dataset).metadata.name,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
            self.destination_data(dataset).metadata.pv,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
            self.destination_data(dataset).metadata.access_mode,
        )

    # noinspection PyUnresolvedReferences
    def test_map_average_dataset_adds_importer(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=False
        )
        self.mapper.map(destination=self.destination)
        for importer in self.destination_data(dataset).importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                0
            ]: "position_counts",
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[0].mapping
        )

    # noinspection PyUnresolvedReferences
    def test_map_average_dataset_with_maxdev_adds_additional_importer(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=True
        )
        self.mapper.map(destination=self.destination)
        for importer in self.destination_data(dataset).importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                0
            ]: "position_counts",
            getattr(self.mapper.source.c1.main, dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[0].mapping
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.averagemeta, f"{dataset}__Attempts"
            ).dtype.names[1]: "attempts",
        }
        self.assertDictEqual(
            mapping_dict, self.destination_data(dataset).importer[1].mapping
        )

    def test_map_average_channel_sets_metadata(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=False
        )
        self.mapper.map(destination=self.destination)
        # noinspection PyUnresolvedReferences
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.averagemeta,
                f"{dataset}__AverageCount",
            ).data["AverageCount"][0],
            self.destination_data(dataset).metadata.n_averages,
        )

    # noinspection PyUnresolvedReferences
    def test_map_average_channel_with_maxdev_sets_metadata(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_average_detector_data(
            normalized=False, maxdev=True
        )
        self.mapper.map(destination=self.destination)
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.averagemeta,
                f"{dataset}__Attempts",
            ).data["MaxAttempts"][0],
            self.destination_data(dataset).metadata.max_attempts,
        )
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.averagemeta,
                f"{dataset}__Limit-MaxDev",
            ).data["Limit"][0],
            self.destination_data(dataset).metadata.low_limit,
        )
        self.assertEqual(
            getattr(
                self.mapper.source.c1.main.averagemeta,
                f"{dataset}__Limit-MaxDev",
            ).data["maxDeviation"][0],
            self.destination_data(dataset).metadata.max_deviation,
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_average_dataset_adds_dataset(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_average_detector_data(
            normalized=True, maxdev=False
        )
        self.mapper.map(destination=self.destination)
        h5_dataset = getattr(self.mapper.source.c1.main.normalized, dataset)
        dataset = dataset.split("__")[0]
        self.assertIn(dataset, self.destination.data.keys())
        self.assertIsInstance(
            self.destination_data(dataset),
            evefile.entities.data.AverageNormalizedChannelData,
        )
        self.assertEqual(
            dataset,
            self.destination_data(dataset).metadata.id,
        )
        self.assertEqual(
            h5_dataset.attributes["Name"],
            self.destination_data(dataset).metadata.name,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[1],
            self.destination_data(dataset).metadata.pv,
        )
        self.assertEqual(
            h5_dataset.attributes["Access"].split(":", maxsplit=1)[0],
            self.destination_data(dataset).metadata.access_mode,
        )

    # noinspection PyUnresolvedReferences
    def test_map_normalized_average_dataset_adds_importer(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_average_detector_data(
            normalized=True, maxdev=False
        )
        self.mapper.map(destination=self.destination)
        base_dataset = dataset.split("__")[0]
        for importer in self.destination_data(base_dataset).importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, base_dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, base_dataset).dtype.names[
                0
            ]: "position_counts",
            getattr(self.mapper.source.c1.main, base_dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict,
            self.destination_data(base_dataset).importer[0].mapping,
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[1]: "normalized_data",
        }
        self.assertDictEqual(
            mapping_dict,
            self.destination_data(base_dataset).importer[1].mapping,
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main, dataset.split("__")[1]
            ).dtype.names[1]: "normalizing_data",
        }
        self.assertDictEqual(
            mapping_dict,
            self.destination_data(base_dataset).importer[2].mapping,
        )

    # noinspection PyUnresolvedReferences
    def test_map_norm_avg_dataset_with_maxdev_adds_additional_importer(self):
        self.mapper.source = self.source
        dataset = self.mapper.source.add_average_detector_data(
            normalized=True, maxdev=True
        )
        self.mapper.map(destination=self.destination)
        base_dataset = dataset.split("__")[0]
        for importer in self.destination_data(base_dataset).importer:
            self.assertEqual(
                getattr(self.mapper.source.c1.main, base_dataset).filename,
                importer.source,
            )
        mapping_dict = {
            getattr(self.mapper.source.c1.main, base_dataset).dtype.names[
                0
            ]: "position_counts",
            getattr(self.mapper.source.c1.main, base_dataset).dtype.names[
                1
            ]: "data",
        }
        self.assertDictEqual(
            mapping_dict,
            self.destination_data(base_dataset).importer[0].mapping,
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.averagemeta, f"{dataset}__Attempts"
            ).dtype.names[1]: "attempts",
        }
        self.assertDictEqual(
            mapping_dict,
            self.destination_data(base_dataset).importer[1].mapping,
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main.normalized, dataset
            ).dtype.names[1]: "normalized_data",
        }
        self.assertDictEqual(
            mapping_dict,
            self.destination_data(base_dataset).importer[2].mapping,
        )
        mapping_dict = {
            getattr(
                self.mapper.source.c1.main, dataset.split("__")[1]
            ).dtype.names[1]: "normalizing_data",
        }
        self.assertDictEqual(
            mapping_dict,
            self.destination_data(base_dataset).importer[3].mapping,
        )

    def test_map_axes_snapshot_datasets(self):
        self.mapper.source = self.source
        datasets = self.mapper.source.add_axes_snapshot_data()
        self.mapper.map(destination=self.destination)
        self.assertTrue(self.destination.snapshots)
        for dataset in datasets:
            self.assertIsInstance(
                self.destination.snapshots[dataset],
                evefile.entities.data.AxisData,
            )

    def test_map_axes_snapshot_datasets_removes_from_2map(self):
        self.mapper.source = self.source
        datasets = self.mapper.source.add_axes_snapshot_data()
        self.mapper.map(destination=self.destination)
        for dataset in datasets:
            self.assertNotIn(dataset, self.mapper.datasets2map_in_snapshot)

    def test_map_channel_snapshot_datasets(self):
        self.mapper.source = self.source
        datasets = self.mapper.source.add_channel_snapshot_data()
        self.mapper.map(destination=self.destination)
        self.assertTrue(self.destination.snapshots)
        for dataset in datasets:
            self.assertIsInstance(
                self.destination.snapshots[dataset],
                evefile.entities.data.ChannelData,
            )

    def test_map_channel_snapshot_datasets_removes_from_2map(self):
        self.mapper.source = self.source
        datasets = self.mapper.source.add_channel_snapshot_data()
        self.mapper.map(destination=self.destination)
        for dataset in datasets:
            self.assertNotIn(dataset, self.mapper.datasets2map_in_snapshot)

    def test_map_without_main_group(self):
        self.mapper.source = MockEveH5()
        self.mapper.map(destination=self.destination)


class TestVersionMapperV6(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV6()
        self.destination = evefile.boundaries.evefile.EveFile(load=False)

    def test_instantiate_class(self):
        pass

    def test_map_converts_date_to_datetime(self):
        self.mapper.source = MockEveH5v5()
        self.mapper.map(destination=self.destination)
        date_mappings = {
            "start": "StartTimeISO",
            "end": "EndTimeISO",
        }
        for key, value in date_mappings.items():
            with self.subTest(key=key, val=value):
                self.assertEqual(
                    getattr(self.destination.metadata, key),
                    datetime.datetime.fromisoformat(
                        self.mapper.source.attributes[value]
                    ),
                )


class TestVersionMapperV7(unittest.TestCase):
    def setUp(self):
        self.mapper = version_mapping.VersionMapperV7()
        self.source = MockEveH5()
        self.destination = evefile.boundaries.evefile.EveFile(load=False)

    def tearDown(self):
        if os.path.exists(self.source.filename):
            os.remove(self.source.filename)

    def test_instantiate_class(self):
        pass

    def test_map_converts_simulation_flag_to_boolean(self):
        self.mapper.source = MockEveH5v5()
        self.mapper.source.attributes["Simulation"] = "no"
        self.mapper.map(destination=self.destination)
        self.assertIsInstance(self.destination.metadata.simulation, bool)
        self.assertFalse(self.destination.metadata.simulation)
        self.mapper.source.attributes["Simulation"] = "yes"
        self.mapper.map(destination=self.destination)
        self.assertIsInstance(self.destination.metadata.simulation, bool)
        self.assertTrue(self.destination.metadata.simulation)
