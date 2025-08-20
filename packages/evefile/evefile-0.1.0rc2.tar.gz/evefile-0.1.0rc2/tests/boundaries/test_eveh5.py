import functools
import os
import unittest

import h5py
import numpy as np

from evefile.boundaries import eveh5


class DummyHDF5File:
    def __init__(self, filename=""):
        self.filename = filename

    def create(self):
        with h5py.File(self.filename, "w") as file:
            file.attrs["Version"] = np.bytes_(["0.1.0"])
            file.attrs["Location"] = np.bytes_(["Unittest"])
            c1 = file.create_group("c1")
            c1.attrs["start"] = np.bytes_(["2024-01-01"])
            main = c1.create_group("main")
            main.attrs["name"] = np.bytes_(["foo"])
            meta = c1.create_group("meta")
            meta.attrs["name"] = np.bytes_(["foo"])
            test = main.create_dataset("test", data=np.ones([5, 2]))
            test.attrs["name"] = np.bytes_(["foo"])
            poscounttimer = meta.create_dataset("PosCountTimer", (1, 1))
            poscounttimer.attrs["foo"] = np.bytes_(["bar"])
            scml = file.create_dataset("SCML", (1, 1))
            scml.attrs["foo"] = np.bytes_(["bar"])


class TestHDF5Item(unittest.TestCase):
    def setUp(self):
        self.hdf5_item = eveh5.HDF5Item()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = ["filename", "name", "attributes"]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.hdf5_item, attribute))

    def test_set_filename_on_init(self):
        filename = "foo"
        hdf5_item = eveh5.HDF5Item(filename=filename)
        self.assertEqual(filename, hdf5_item.filename)

    def test_set_name_on_init(self):
        name = "bar"
        hdf5_item = eveh5.HDF5Item(name=name)
        self.assertEqual(name, hdf5_item.name)

    def test_get_attributes_without_filename_raises(self):
        with self.assertRaisesRegex(ValueError, "Missing attribute filename"):
            self.hdf5_item.get_attributes()

    def test_get_attributes_without_name_raises(self):
        self.hdf5_item.filename = "foo"
        with self.assertRaisesRegex(ValueError, "Missing attribute name"):
            self.hdf5_item.get_attributes()

    def test_get_attributes_reads_attributes(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_item.filename = self.filename
        self.hdf5_item.name = "/"
        self.hdf5_item.get_attributes()
        self.assertTrue(self.hdf5_item.attributes)

    def test_get_attributes_with_iso8859_characters_reads_attributes(self):
        DummyHDF5File(filename=self.filename).create()
        with h5py.File(self.filename, "w") as file:
            file.attrs["Comment"] = np.bytes_(
                ["äöü".encode(encoding="iso8859")]
            )
        self.hdf5_item.filename = self.filename
        self.hdf5_item.name = "/"
        self.hdf5_item.get_attributes()
        self.assertTrue(self.hdf5_item.attributes)

    def test_attribute_values_are_strings(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_item.filename = self.filename
        self.hdf5_item.name = "/"
        self.hdf5_item.get_attributes()
        for value in self.hdf5_item.attributes.values():
            with self.subTest(value=value):
                self.assertIsInstance(value, str)


class TestHDF5Dataset(unittest.TestCase):
    def setUp(self):
        self.hdf5_dataset = eveh5.HDF5Dataset()
        self.filename = "test.h5"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_implements_hdf5_item(self):
        self.assertIsInstance(self.hdf5_dataset, eveh5.HDF5Item)

    def test_has_attributes_from_parent_class(self):
        attributes = [
            x for x in dir(eveh5.HDF5Item()) if not x.startswith("_")
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.hdf5_dataset, attribute))

    def test_set_filename_on_init(self):
        filename = "foo"
        hdf5_dataset = eveh5.HDF5Dataset(filename=filename)
        self.assertEqual(filename, hdf5_dataset.filename)

    def test_set_name_on_init(self):
        name = "bar"
        hdf5_dataset = eveh5.HDF5Dataset(name=name)
        self.assertEqual(name, hdf5_dataset.name)

    def test_get_data_without_filename_raises(self):
        with self.assertRaisesRegex(ValueError, "Missing attribute filename"):
            self.hdf5_dataset.get_data()

    def test_get_data_without_name_raises(self):
        self.hdf5_dataset.filename = "foo"
        with self.assertRaisesRegex(ValueError, "Missing attribute name"):
            self.hdf5_dataset.get_data()

    def test_get_data_sets_data(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_dataset.filename = self.filename
        self.hdf5_dataset.name = "/c1/main/test"
        self.hdf5_dataset.get_data()
        self.assertGreater(self.hdf5_dataset.data.size, 0)

    def test_accessing_data_sets_data(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_dataset.filename = self.filename
        self.hdf5_dataset.name = "/c1/main/test"
        self.assertGreater(self.hdf5_dataset.data.size, 0)

    def test_get_data_does_nothing_if_data_are_set(self):
        array = np.random.random(5)
        self.hdf5_dataset.data = array
        self.hdf5_dataset.get_data()
        np.testing.assert_array_equal(array, self.hdf5_dataset.data)

    def test_dtype_without_filename_raises(self):
        with self.assertRaisesRegex(ValueError, "Missing attribute filename"):
            _ = self.hdf5_dataset.dtype

    def test_dtype_without_name_raises(self):
        self.hdf5_dataset.filename = "foo"
        with self.assertRaisesRegex(ValueError, "Missing attribute name"):
            _ = self.hdf5_dataset.dtype

    def test_dtype_returns_dtype(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_dataset.filename = self.filename
        self.hdf5_dataset.name = "/c1/main/test"
        self.assertIsInstance(self.hdf5_dataset.dtype, np.dtype)

    def test_dtype_returns_existing_dtype(self):
        self.hdf5_dataset._dtype = "foo"
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_dataset.filename = self.filename
        self.hdf5_dataset.name = "/c1/main/test"
        self.assertEqual(self.hdf5_dataset.dtype, "foo")

    def test_shape_without_filename_raises(self):
        with self.assertRaisesRegex(ValueError, "Missing attribute filename"):
            _ = self.hdf5_dataset.shape

    def test_shape_without_name_raises(self):
        self.hdf5_dataset.filename = "foo"
        with self.assertRaisesRegex(ValueError, "Missing attribute name"):
            _ = self.hdf5_dataset.shape

    def test_shape_returns_shape(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_dataset.filename = self.filename
        self.hdf5_dataset.name = "/c1/main/test"
        self.assertIsInstance(self.hdf5_dataset.shape, tuple)

    def test_shape_does_not_load_data(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_dataset.filename = self.filename
        self.hdf5_dataset.name = "/c1/main/test"
        self.assertTupleEqual((0,), self.hdf5_dataset._data.shape)


class TestHDF5Group(unittest.TestCase):
    def setUp(self):
        self.hdf5_group = eveh5.HDF5Group()
        self.item = eveh5.HDF5Item(filename="foo", name="bar")

    def test_instantiate_class(self):
        pass

    def test_implements_hdf5_item(self):
        self.assertIsInstance(self.hdf5_group, eveh5.HDF5Item)

    def test_has_attributes_from_parent_class(self):
        attributes = [
            x for x in dir(eveh5.HDF5Item()) if not x.startswith("_")
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.hdf5_group, attribute))

    def test_set_filename_on_init(self):
        filename = "foo"
        hdf5_group = eveh5.HDF5Group(filename=filename)
        self.assertEqual(filename, hdf5_group.filename)

    def test_set_name_on_init(self):
        name = "bar"
        hdf5_group = eveh5.HDF5Group(name=name)
        self.assertEqual(name, hdf5_group.name)

    def test_add_item_sets_property_identical_to_item_name(self):
        self.hdf5_group.add_item(self.item)
        self.assertTrue(hasattr(self.hdf5_group, self.item.name))

    def test_item_name_is_only_part_after_last_slash(self):
        self.item.name = "foo/bar/bla/blub"
        self.hdf5_group.add_item(self.item)
        self.assertTrue(hasattr(self.hdf5_group, "blub"))

    def test_iterate_over_group_yields_item(self):
        self.hdf5_group.add_item(self.item)
        elements = [element for element in self.hdf5_group]
        self.assertTrue(elements)

    def test_iterate_over_group_yields_hdf5item(self):
        self.hdf5_group.add_item(self.item)
        for element in self.hdf5_group:
            self.assertIsInstance(element, eveh5.HDF5Item)

    def test_item_names_returns_names_of_items(self):
        item_names = ["foo", "bar", "baz"]
        for name in item_names:
            self.hdf5_group.add_item(
                eveh5.HDF5Item(filename="foo", name=name)
            )
        self.assertListEqual(item_names, self.hdf5_group.item_names())


class TestHDF5File(unittest.TestCase):
    def setUp(self):
        self.hdf5_file = eveh5.HDF5File()
        self.filename = "test.h5"
        self.items = []
        self.items_with_type = {}

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def get_items_from_hdf5_file(self):
        with h5py.File(self.filename, "r") as file:
            file.visit(self.items.append)

    def get_items_with_type_from_hdf5_file(self):
        def inspect(name, item):
            if isinstance(item, h5py.Group):
                node_type = eveh5.HDF5Group
            else:
                node_type = eveh5.HDF5Dataset
            self.items_with_type[name] = node_type

        with h5py.File(self.filename, "r") as file:
            file.visititems(inspect)

    def test_instantiate_class(self):
        pass

    def test_implements_hdf5_group(self):
        self.assertIsInstance(self.hdf5_file, eveh5.HDF5Group)

    def test_has_attributes_from_parent_class(self):
        attributes = [
            x for x in dir(eveh5.HDF5Group()) if not x.startswith("_")
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.hdf5_file, attribute))

    def test_name_is_root(self):
        self.assertEqual("/", self.hdf5_file.name)

    def test_read_sets_filename(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_file.read(self.filename)
        self.assertEqual(self.filename, self.hdf5_file.filename)

    def test_read_without_filename_parameter_but_filename_set(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_file.filename = self.filename
        self.hdf5_file.read()

    def test_read_without_filename_raises(self):
        with self.assertRaisesRegex(ValueError, "Missing attribute filename"):
            self.hdf5_file.read()

    def test_read_adds_items_to_root(self):
        DummyHDF5File(filename=self.filename).create()
        self.get_items_from_hdf5_file()
        self.hdf5_file.read(self.filename)
        root_items = [x for x in self.items if "/" not in x]
        for item in root_items:
            with self.subTest(item=item):
                self.assertTrue(hasattr(self.hdf5_file, item))

    def test_read_instantiates_correct_item_type(self):
        DummyHDF5File(filename=self.filename).create()
        self.get_items_with_type_from_hdf5_file()
        self.hdf5_file.read(self.filename)
        for item, node_type in self.items_with_type.items():
            if "/" not in item:
                with self.subTest(item=item):
                    self.assertIsInstance(
                        getattr(self.hdf5_file, item), node_type
                    )

    def test_read_sets_item_filename(self):
        DummyHDF5File(filename=self.filename).create()
        self.get_items_from_hdf5_file()
        self.hdf5_file.read(self.filename)
        root_items = [x for x in self.items if "/" not in x]
        for item in root_items:
            with self.subTest(item=item):
                self.assertEqual(
                    self.filename, getattr(self.hdf5_file, item).filename
                )

    def test_read_sets_item_name(self):
        DummyHDF5File(filename=self.filename).create()
        self.get_items_from_hdf5_file()
        self.hdf5_file.read(self.filename)
        root_items = [x for x in self.items if "/" not in x]
        for item in root_items:
            with self.subTest(item=item):
                self.assertEqual(
                    f"/{item}", getattr(self.hdf5_file, item).name
                )

    def test_read_adds_item_hierarchy(self):
        DummyHDF5File(filename=self.filename).create()
        self.get_items_from_hdf5_file()
        self.hdf5_file.read(self.filename)
        for item in self.items:
            with self.subTest(item=item):
                functools.reduce(getattr, item.split("/"), self.hdf5_file)

    def test_read_with_read_attributes_sets_item_attributes(self):
        DummyHDF5File(filename=self.filename).create()
        self.get_items_from_hdf5_file()
        self.hdf5_file.read_attributes = True
        self.hdf5_file.read(self.filename)
        for item in self.items:
            with self.subTest(item=item):
                self.assertTrue(
                    functools.reduce(
                        getattr, item.split("/"), self.hdf5_file
                    ).attributes
                )

    def test_read_with_read_attributes_sets_file_attributes(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_file.read_attributes = True
        self.hdf5_file.read(self.filename)
        self.assertTrue(self.hdf5_file.attributes)

    def test_read_closes_hdf5_file(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_file.read_attributes = True
        self.hdf5_file.read(self.filename)
        self.assertFalse(self.hdf5_file._hdf5_filehandle)

    def test_read_with_close_file_false_leaves_hdf5_file_open(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_file.read_attributes = True
        self.hdf5_file.close_file = False
        self.hdf5_file.read(self.filename)
        self.assertTrue(self.hdf5_file._hdf5_filehandle)
        self.hdf5_file._hdf5_filehandle.close()

    def test_close_closes_open_hdf5_file(self):
        DummyHDF5File(filename=self.filename).create()
        self.hdf5_file.read_attributes = True
        self.hdf5_file.close_file = False
        self.hdf5_file.read(self.filename)
        self.assertTrue(self.hdf5_file._hdf5_filehandle)
        self.hdf5_file.close()
        self.assertFalse(self.hdf5_file._hdf5_filehandle)
