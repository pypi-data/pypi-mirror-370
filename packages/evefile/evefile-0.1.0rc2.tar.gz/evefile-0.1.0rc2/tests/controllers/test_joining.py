import unittest

import numpy as np
from numpy import ma

from evefile.controllers import joining
import evefile.entities.data


class MockChannel(evefile.entities.data.ChannelData):
    def __init__(
        self, data=np.random.random(5), positions=np.arange(2, 7), name=""
    ):
        super().__init__()
        self.data = data
        self.position_counts = positions
        self.metadata.name = name


class MockAxis(evefile.entities.data.AxisData):
    def __init__(
        self, data=np.random.random(5), positions=np.arange(2, 7), name=""
    ):
        super().__init__()
        self.data = data
        self.position_counts = positions
        self.metadata.name = name


class MockEveFile:
    def __init__(self, snapshots=False):
        self.data = {
            "SimChan:01": MockChannel(),
            "SimMot:01": MockAxis(),
        }
        if snapshots:
            self.snapshots = {
                "SimChan:01": MockChannel(
                    data=np.random.random(2), positions=np.asarray([1, 7])
                ),
                "SimMot:01": MockAxis(
                    data=np.random.random(2), positions=np.asarray([1, 7])
                ),
            }
        else:
            self.snapshots = {}

    def set_ids(self):
        for key, value in self.data.items():
            value.metadata.id = key
        for key, value in self.snapshots.items():
            value.metadata.id = key

    def get_data(self, name=""):
        names = {item.metadata.name: key for key, item in self.data.items()}
        return self.data[names[name]]


class TestJoin(unittest.TestCase):
    def setUp(self):
        self.join = joining.Join()
        self.evefile = MockEveFile()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "evefile",
        ]
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.join, attribute))

    def test_initialise_with_evefile_sets_evefile(self):
        evefile = self.evefile
        join = joining.Join(evefile=evefile)
        self.assertEqual(evefile, join.evefile)

    def test_join_without_evefile_raises(self):
        self.join.evefile = None
        with self.assertRaisesRegex(
            ValueError, "Need an evefile to join data."
        ):
            self.join.join()

    def test_join_without_data_raises(self):
        self.join.evefile = self.evefile
        with self.assertRaisesRegex(ValueError, "Need data to join data."):
            self.join.join()

    def test_join_returns_list(self):
        class MyJoin(joining.Join):
            def _join(self, data=None):
                return data

        self.join = MyJoin()
        self.join.evefile = self.evefile
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        self.assertIsInstance(result, list)

    def test_join_with_data(self):
        class MyJoin(joining.Join):
            def _join(self, data=None):
                return data

        self.join = MyJoin()
        self.join.evefile = self.evefile
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.join.join(data=list(self.join.evefile.data.values()))
        self.assertTrue(result)
        for item in result:
            self.assertIsInstance(item, evefile.entities.data.MeasureData)

    def test_join_with_ids_converts_to_datasets(self):
        class MyJoin(joining.Join):
            def _join(self, data=None):
                return data

        self.join = MyJoin()
        self.join.evefile = MockEveFile()
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        for item in result:
            self.assertIsInstance(item, evefile.entities.data.MeasureData)

    def test_join_with_names_converts_to_datasets(self):
        class MyJoin(joining.Join):
            def _join(self, data=None):
                return data

        self.join = MyJoin()
        self.join.evefile = MockEveFile()
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(5),
                positions=np.linspace(0, 4, 5),
                name="bar",
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(7),
                positions=np.linspace(0, 6, 7),
                name="baz",
            ),
        }
        result = self.join.join(data=["bar", "baz"])
        for item in result:
            self.assertIsInstance(item, evefile.entities.data.MeasureData)


class TestChannelPositions(unittest.TestCase):
    def setUp(self):
        self.join = joining.ChannelPositions()
        self.join.evefile = MockEveFile()

    def test_instantiate_class(self):
        pass

    def test_join_returns_list_of_measuredata(self):
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        for item in result:
            self.assertIsInstance(item, evefile.entities.data.MeasureData)

    def test_join_returns_copy_of_measuredata(self):
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        self.assertIsNot(result[0], self.join.evefile.data["SimChan:01"])
        self.assertIsNot(result[1], self.join.evefile.data["SimMot:01"])

    def test_join_returns_data_in_input_order(self):
        result = self.join.join(data=["SimMot:01", "SimChan:01"])
        self.assertIsInstance(result[0], evefile.entities.data.AxisData)
        self.assertIsInstance(result[1], evefile.entities.data.ChannelData)
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        self.assertIsInstance(result[0], evefile.entities.data.ChannelData)
        self.assertIsInstance(result[1], evefile.entities.data.AxisData)

    def test_join_returns_only_values_for_channel_positions(self):
        self.join.evefile.data = {
            "SimMot:01": MockAxis(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
        }
        result = self.join.join(data=["SimMot:01", "SimChan:01"])
        for item in result:
            self.assertEqual(
                len(self.join.evefile.data["SimChan:01"].data), len(item.data)
            )

    def test_join_returns_values_for_all_channel_positions(self):
        self.join.evefile.data = {
            "SimMot:01": MockAxis(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimChan:01": MockChannel(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.join.join(data=["SimMot:01", "SimChan:01"])
        for item in result:
            self.assertEqual(
                len(self.join.evefile.data["SimChan:01"].data), len(item.data)
            )

    def test_join_returns_only_values_for_channel_positions_with_gaps(self):
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(4), positions=np.asarray([0, 2, 3, 4])
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        self.assertEqual(len(result[0].data), len(result[1].data))

    def test_join_fills_axes_values(self):
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(4), positions=np.linspace(0, 3, 4)
            ),
        }
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        self.assertEqual(len(result[0].data), len(result[1].data))
        np.testing.assert_array_equal(
            self.join.evefile.data["SimMot:01"].data,
            result[1].data[:-1],
        )
        self.assertEqual(result[1].data[-2], result[1].data[-1])

    def test_join_masks_axes_values_with_gap_at_beginning(self):
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(3), positions=np.linspace(2, 4, 3)
            ),
        }
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        self.assertEqual(len(result[0].data), len(result[1].data))
        np.testing.assert_array_equal(
            self.join.evefile.data["SimMot:01"].data,
            result[1].data[2:],
        )
        self.assertIsInstance(result[1].data, ma.masked_array)
        self.assertTrue(result[1].data.mask[0])

    def test_join_fills_axes_values_with_gaps(self):
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(4), positions=np.asarray([0, 2, 4])
            ),
        }
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        self.assertEqual(len(result[0].data), len(result[1].data))
        self.assertEqual(result[1].data[0], result[1].data[1])
        self.assertEqual(result[1].data[2], result[1].data[3])

    def test_join_fills_axes_values_with_snapshots(self):
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.arange(2, 7)
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(4), positions=np.asarray([3, 4, 5, 6])
            ),
        }
        self.join.evefile.snapshots = {
            "SimChan:01": MockChannel(
                data=np.random.random(2), positions=np.asarray([1, 7])
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(2), positions=np.asarray([1, 7])
            ),
        }
        self.join.evefile.set_ids()
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        self.assertEqual(len(result[0].data), len(result[1].data))
        self.assertEqual(
            self.join.evefile.snapshots["SimMot:01"].data[0],
            result[1].data[0],
        )

    def test_join_returns_values_for_union_of_all_channel_positions(self):
        self.join.evefile.data = {
            "SimMot:01": MockAxis(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimChan:02": MockChannel(
                data=np.random.random(5), positions=np.linspace(2, 6, 5)
            ),
        }
        result = self.join.join(
            data=["SimMot:01", "SimChan:01", "SimChan:02"]
        )
        np.testing.assert_array_equal(
            result[0].position_counts,
            np.union1d(
                self.join.evefile.data["SimChan:01"].position_counts,
                self.join.evefile.data["SimChan:02"].position_counts,
            ),
        )

    def test_join_fills_and_masks_channel_values_with_gaps(self):
        self.join.evefile.data = {
            "SimMot:01": MockAxis(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimChan:02": MockChannel(
                data=np.random.random(5), positions=np.linspace(2, 6, 5)
            ),
        }
        result = self.join.join(
            data=["SimMot:01", "SimChan:01", "SimChan:02"]
        )
        self.assertEqual(len(result[0].data), len(result[1].data))
        self.assertEqual(len(result[0].data), len(result[2].data))
        self.assertIsInstance(result[1].data, ma.masked_array)
        self.assertIsInstance(result[2].data, ma.masked_array)
        self.assertTrue(result[1].data.mask[-1])
        self.assertTrue(result[2].data.mask[0])
        np.testing.assert_array_equal(
            result[1].position_counts,
            np.union1d(
                self.join.evefile.data["SimChan:01"].position_counts,
                self.join.evefile.data["SimChan:02"].position_counts,
            ),
        )


class TestAxisPositions(unittest.TestCase):
    def setUp(self):
        self.join = joining.AxisPositions()
        self.join.evefile = MockEveFile()

    def test_instantiate_class(self):
        pass

    def test_join_returns_only_values_for_axis_positions(self):
        self.join.evefile.data = {
            "SimMot:01": MockAxis(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimChan:01": MockChannel(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
        }
        result = self.join.join(data=["SimMot:01", "SimChan:01"])
        for item in result:
            self.assertEqual(
                len(self.join.evefile.data["SimMot:01"].data), len(item.data)
            )

    def test_join_returns_values_for_all_axis_positions(self):
        self.join.evefile.data = {
            "SimMot:01": MockAxis(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
            "SimChan:01": MockChannel(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
        }
        result = self.join.join(data=["SimMot:01", "SimChan:01"])
        for item in result:
            self.assertEqual(
                len(self.join.evefile.data["SimMot:01"].data), len(item.data)
            )

    def test_join_returns_only_values_for_axis_positions_with_gaps(self):
        self.join.evefile.data = {
            "SimChan:01": MockChannel(
                data=np.random.random(7), positions=np.linspace(0, 6, 7)
            ),
            "SimMot:01": MockAxis(
                data=np.random.random(4), positions=np.asarray([0, 2, 3, 4])
            ),
        }
        result = self.join.join(data=["SimChan:01", "SimMot:01"])
        self.assertEqual(len(result[0].data), len(result[1].data))


class TestAxisAndChannelPositions(unittest.TestCase):
    def setUp(self):
        self.join = joining.AxisAndChannelPositions()
        self.join.evefile = MockEveFile()

    def test_instantiate_class(self):
        pass

    def test_join_returns_only_values_for_intersection_positions(self):
        self.join.evefile.data = {
            "SimMot:01": MockAxis(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimChan:01": MockChannel(
                data=np.random.random(7), positions=np.linspace(2, 8, 7)
            ),
        }
        result = self.join.join(data=["SimMot:01", "SimChan:01"])
        positions = np.intersect1d(
            self.join.evefile.data["SimChan:01"].position_counts,
            self.join.evefile.data["SimMot:01"].position_counts,
        ).astype(np.int64)
        for item in result:
            self.assertEqual(len(positions), len(item.data))
        np.testing.assert_array_equal(
            result[0].data,
            self.join.evefile.data["SimMot:01"].data[2:6],
        )
        np.testing.assert_array_equal(
            result[1].data,
            self.join.evefile.data["SimChan:01"].data[0:3],
        )


class TestAxisOrChannelPositions(unittest.TestCase):
    def setUp(self):
        self.join = joining.AxisOrChannelPositions()
        self.join.evefile = MockEveFile()

    def test_instantiate_class(self):
        pass

    def test_join_returns_only_values_for_union_positions(self):
        self.join.evefile.data = {
            "SimMot:01": MockAxis(
                data=np.random.random(5), positions=np.linspace(0, 4, 5)
            ),
            "SimChan:01": MockChannel(
                data=np.random.random(7), positions=np.linspace(2, 8, 7)
            ),
        }
        result = self.join.join(data=["SimMot:01", "SimChan:01"])
        positions = np.union1d(
            self.join.evefile.data["SimChan:01"].position_counts,
            self.join.evefile.data["SimMot:01"].position_counts,
        )
        for item in result:
            self.assertEqual(len(positions), len(item.data))


class TestJoinFactory(unittest.TestCase):
    def setUp(self):
        self.factory = joining.JoinFactory()

    def test_instantiate_class(self):
        pass

    def test_get_join_returns_join(self):
        self.assertIsInstance(self.factory.get_join(), joining.Join)

    def test_get_join_with_type_returns_correct_join(self):
        self.assertIsInstance(
            self.factory.get_join(mode="ChannelPositions"),
            joining.Join,
        )

    def test_initialise_with_evefile_sets_evefile(self):
        evefile = "foo"
        factory = joining.JoinFactory(evefile=evefile)
        self.assertEqual(evefile, factory.evefile)

    def test_get_join_with_evefile_sets_evefile(self):
        self.factory.evefile = "foo"
        join = self.factory.get_join()
        self.assertEqual(self.factory.evefile, join.evefile)
