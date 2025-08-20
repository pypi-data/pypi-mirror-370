"""
.. include:: <isopub.txt>

*Mapping eveH5 contents to the data structures of the evefile package.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 2

There are different versions of the schema underlying the eveH5 files.
Hence, mapping the contents of an eveH5 file to the data model of the
evefile package requires to get the correct mapper for the specific
version. This is the typical use case for the factory pattern.

Users of the module hence will typically only obtain a
:obj:`VersionMapperFactory` object to get the correct mappers for individual
files. Furthermore, "users" basically boils down to the :class:`EveFile
<evefile.boundaries.evefile.EveFile>` class. Therefore, users of
the `evefile` package usually do not interact directly with any of the
classes provided by this module.


Overview
========

Being version agnostic with respect to eveH5 and SCML schema versions is a
central aspect of the evefile package. This requires facilities mapping
the actual eveH5 files to the data model provided by the entities
technical layer of the evefile subpackage. The :class:`File
<evefile.boundaries.evefile.File>` facade obtains
the correct :obj:`VersionMapper` object via the
:class:`VersionMapperFactory`, providing an :class:`HDF5File
<evefile.boundaries.eveh5.HDF5File>` resource object to the
factory. It is the duty of the factory to obtain the "version" attribute
from the :obj:`HDF5File <evefile.boundaries.eveh5.HDF5File>`
object (explicitly getting the attributes of the root group of the
:obj:`HDF5File <evefile.boundaries.eveh5.HDF5File>` object).


.. figure:: /uml/evefile.controllers.version_mapping.*
    :align: center

    Class hierarchy of the :mod:`evefile.controllers.version_mapping`
    module, providing the functionality to map different eveH5 file
    schemas to the data structure provided by the :class:`EveFile
    <evefile.boundaries.evefile.EveFile>` class. The factory
    will be used to get the correct mapper for a given eveH5 file.
    For each eveH5 schema version, there exists an individual
    ``VersionMapperVx`` class dealing with the version-specific mapping.
    The idea behind the ``Mapping`` class is to provide simple mappings for
    attributes and alike that need not be hard-coded and can be stored
    externally, *e.g.* in YAML files. This would make it easier to account
    for (simple) changes.


For each eveH5 schema version, there exists an individual
``VersionMapperVx`` class dealing with the version-specific mapping. That
part of the mapping common to all versions of the eveH5 schema takes place
in the :class:`VersionMapper` parent class, *e.g.* removing the chain. The
idea behind the ``Mapping`` class is to provide simple mappings for
attributes and alike that can be stored externally, *e.g.* in YAML files.
This would make it easier to account for (simple) changes.


Mapping tasks for eveH5 schema
==============================

What follows is a summary of the different aspects, for the time being
*not* divided for the different formats (up to v7):

* Map attributes of ``/`` and ``/c1`` to the file metadata. |check|
* Convert monitor datasets from the ``device`` group to :obj:`MonitorData
  <evefile.entities.data.MonitorData>` objects. |check|

  * We probably need to create subclasses for the different monitor
    datasets, at least distinguishing between numeric and non-numeric
    values.

* Map ``/c1/meta/PosCountTimer`` to :obj:`TimestampData
  <evefile.entities.data.TimestampData>` object. |check|

* Starting with eveH5 v5: Map ``/LiveComment`` to :obj:`LogMessage
  <evefile.entities.file.LogMessage>` objects. |check|

* Filter all datasets from the ``main`` section, with different goals:

  * Map array data to :obj:`ArrayChannelData
    <evefile.entities.data.ArrayChannelData>` objects (HDF5 groups
    having an attribute ``DeviceType`` set to ``Channel``). |cross|

    * Distinguish between MCA and scope data (at least). |cross|
    * Map additional datasets in main section (and snapshot). |cross|

  * Map all axis datasets to :obj:`AxisData
    <evefile.entities.data.AxisData>` objects. |check|

    * How to distinguish between axes with and without encoders? |cross|
    * Read channels with RBV and replace axis values with RBV. |cross|

      * Most probably, the corresponding channel has the same *name*
        (not XML-ID, though!) as the axis, but with suffix ``_RBV``,
        and can thus be identified.
      * In case of axes with encoders, there may be additional datasets
        present, *e.g.*, those with suffix ``_Enc``.
      * In this case, instead of :obj:`NonencodedAxisData
        <evefile.entities.data.NonencodedAxisData>`,
        an :obj:`AxisData <evefile.entities.data.AxisData>`
        object needs to be created. (Currently, only :obj:`AxisData
        <evefile.entities.data.AxisData>` objects are created,
        what is a mistake as well...)

    * How to deal with pseudo-axes used as options in channel datasets? Do
      we need to deal with axes later? |cross|

  * Distinguish between single point and area data, and map area data to
    :obj:`AreaChannelData <evefile.entities.data.AreaChannelData>`
    objects. (|cross|)

    * Distinguish between scientific and sample cameras. |cross|
    * Which dataset is the "main" dataset for scientific cameras? |cross|

      * Starting with eve v1.39, it is ``TIFF1:chan1``, before, this is
        less clear, and there might not exist a dataset containing
        filenames with full paths, but only numbers.

    * Map sample camera datasets. |cross|

  * Map the additional data for average and interval channel data provided
    in the respective HDF5 groups to :obj:`AverageChannelData
    <evefile.entities.data.AverageChannelData>` and
    :obj:`IntervalChannelData
    <evefile.entities.data.IntervalChannelData>` objects,
    respectively. |check|
  * Map normalized channel data (and the data provided in the
    respective HDF5 groups) to :obj:`NormalizedChannelData
    <evefile.entities.data.NormalizedChannelData>`. |check|
  * Add all data objects to the :attr:`data
    <evefile.boundaries.evefile.EveFile.data>` attribute of the
    :obj:`EveFile <evefile.boundaries.evefile.EveFile>` object.
    (Has been done during mapping already.)

* Filter all datasets from the ``snapshot`` section, with different goals:

  * Map all HDF5 datasets that belong to one of the data objects in the
    :attr:`data <evefile.boundaries.evefile.EveFile.data>`
    attribute of the :obj:`EveFile
    <evefile.boundaries.evefile.EveFile>` object to their respective
    attributes.
  * Map all HDF5 datasets remaining (if any) to data objects
    corresponding to their respective data type.
  * Add all data objects to the :attr:`snapshots
    <evefile.boundaries.evefile.EveFile.snapshots>` attribute of the
    :obj:`EveFile  <evefile.boundaries.evefile.EveFile>` object.
    |cross|


Most probably, not all these tasks can be inferred from the contents of an
eveH5 file alone. In this case, additional mapping tables, eventually
perhaps even on a per-measurement-station level, are necessary.


.. admonition:: Questions to address

    * How were the log messages/live comments saved before v5?

    * How to deal with options that are monitored? Check whether they change
      for a given channel/axis and if so, expand them (“fill”) for each
      PosCount of the corresponding channel/axis, and otherwise set as
      scalar attribute?

    * How to deal with the situation that not all actual data read from eveH5
      are numeric. Of course, non-numeric data cannot be plotted. But how
      to distinguish sensibly?

      * The :mod:`evefile.entities.data` module provides some
        distinct classes for this, at least for now
        :class:`NonnumericChannelData
        <evefile.entities.data.NonnumericChannelData>`.


Module documentation
====================

"""

import datetime
import logging
import sys

from evefile import entities

logger = logging.getLogger(__name__)


class VersionMapperFactory:
    """
    Factory for obtaining the correct version mapper object.

    There are different versions of the schema underlying the eveH5 files.
    Hence, mapping the contents of an eveH5 file to the data model of the
    evefile package requires to get the correct mapper for the specific
    version. This is the typical use case for the factory pattern.


    Attributes
    ----------
    eveh5 : :class:`evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    Raises
    ------
    ValueError
        Raised if no eveh5 object is present


    Examples
    --------
    Using the factory is pretty simple. There are actually two ways how to
    set the eveh5 attribute -- either explicitly or when calling the
    :meth:`get_mapper` method of the factory:

    .. code-block::

        factory = VersionMapperFactory()
        factory.eveh5 = eveh5_object
        mapper = factory.get_mapper()

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5_object)

    In both cases, ``mapper`` will contain the correct mapper object,
    and ``eveh5_object`` contains the Python object representation of an
    eveH5 file.

    """

    def __init__(self):
        self.eveh5 = None

    def get_mapper(self, eveh5=None):
        """
        Return the correct mapper for a given eveH5 file.

        For convenience, the returned mapper has its
        :attr:`VersionMapper.source` attribute already set to the
        ``eveh5`` object used to get the mapper for.

        Parameters
        ----------
        eveh5 : :class:`evefile.boundaries.eveh5.HDF5File`
            Python object representation of an eveH5 file

        Returns
        -------
        mapper : :class:`VersionMapper`
            Mapper used to map the eveH5 file contents to evefile structures.

        Raises
        ------
        ValueError
            Raised if no eveh5 object is present

        AttributeError
            Raised if no matching :class:`VersionMapper` class can be found

        """
        if eveh5:
            self.eveh5 = eveh5
        if not self.eveh5:
            raise ValueError("Missing eveh5 object")
        version = self.eveh5.attributes["EVEH5Version"].split(".")[0]
        try:
            mapper = getattr(
                sys.modules[__name__], f"VersionMapperV{version}"
            )()
        except AttributeError as exc:
            message = f"No mapper for version {version}"
            logger.error(message)
            raise AttributeError(message) from exc
        mapper.source = self.eveh5
        return mapper


class VersionMapper:
    """
    Mapper for mapping the eveH5 file contents to evefile structures.

    This is the base class for all version-dependent mappers. Given that
    there are different versions of the eveH5 schema, each version gets
    handled by a distinct mapper subclass.

    To get an object of the appropriate class, use the
    :class:`VersionMapperFactory` factory.


    Attributes
    ----------
    source : :class:`evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    destination : :class:`evefile.boundaries.evefile.EveFile`
        High(er)-level evefile structure representing an eveH5 file

    datasets2map_in_main : :class:`list`
        Names of the datasets in the main section not yet mapped.

        In order to not have to check all datasets several times,
        this list contains only those datasets not yet mapped. Hence,
        every private mapping method removes those names from the list it
        handled successfully.

    datasets2map_in_snapshot : :class:`list`
        Names of the datasets in the snapshot section not yet mapped.

        In order to not have to check all datasets several times,
        this list contains only those datasets not yet mapped. Hence,
        every private mapping method removes those names from the list it
        handled successfully.

    datasets2map_in_monitor : :class:`list`
        Names of the datasets in the monitor section not yet mapped.

        Note that the monitor section is usually termed "device".

        In order to not have to check all datasets several times,
        this list contains only those datasets not yet mapped. Hence,
        every private mapping method removes those names from the list it
        handled successfully.

    Raises
    ------
    ValueError
        Raised if either source or destination are not provided


    Examples
    --------
    Although the :class:`VersionMapper` class is *not* meant to be used
    directly, its use is prototypical for all the concrete mappers:

    .. code-block::

        mapper = VersionMapper()
        mapper.map(source=eveh5, destination=evefile)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5)
        mapper.map(destination=evefile)


    """

    def __init__(self):
        self.source = None
        self.destination = None
        self.datasets2map_in_main = []
        self.datasets2map_in_snapshot = []
        self.datasets2map_in_monitor = []
        self._main_group = None
        self._snapshot_group = None
        self._monitor_group = None

    def map(self, source=None, destination=None):
        """
        Map the eveH5 file contents to evefile structures.

        Parameters
        ----------
        source : :class:`evefile.boundaries.eveh5.HDF5File`
            Python object representation of an eveH5 file

        destination : :class:`evefile.boundaries.evefile.EveFile`
            High(er)-level evefile structure representing an eveH5 file

        Raises
        ------
        ValueError
            Raised if either source or destination are not provided

        """
        if source:
            self.source = source
        if destination:
            self.destination = destination
        self._check_prerequisites()
        self._set_dataset_names()
        self._map()

    @staticmethod
    def get_hdf5_dataset_importer(dataset=None, mapping=None):
        """
        Get an importer object for HDF5 datasets with properties set.

        Data are loaded on demand, not already when initially loading the
        eveH5 file. Hence, the need for a mechanism to provide the relevant
        information where to get the relevant data from and how. Different
        versions of the underlying eveH5 schema differ even in whether all
        data belonging to one :obj:`Data` object are located in one HDF5
        dataset or spread over multiple HDF5 datasets. In the latter case,
        individual importers are necessary for the separate HDF5 datasets.

        As the :class:`VersionMapper` class deals with each HDF5 dataset
        individually, some fundamental settings for the
        :class:`HDF5DataImporter
        <evefile.entities.data.HDF5DataImporter>` are readily
        available. Additionally, the ``mapping`` parameter provides the
        information necessary to create the correct information in the
        :attr:`HDF5DataImporter.mapping
        <evefile.entities.data.HDF5DataImporter.mapping>` attribute.

        .. important::
            The keys in the dictionary provided via the ``mapping``
            parameter are **integers, not strings**, as usual for
            dictionaries. This allows to directly use the keys for
            indexing the tuple returned by ``numpy.dtype.names``. To be
            explicit, here is an example:

            .. code-block::

                dataset = HDF5Dataset()
                importer_mapping = {
                    0: "milliseconds",
                    1: "data",
                }
                importer = self.get_hdf5_dataset_importer(
                    dataset=dataset, mapping=importer_mapping
                )

            Of course, in reality you will not just instantiate an empty
            :obj:`HDF5Dataset <evefile.boundaries.eveh5.HDF5Dataset>`
            object, but have one available within your mapper.


        Parameters
        ----------
        dataset : :class:`evefile.boundaries.eveh5.HDF5Dataset`
            Representation of an HDF5 dataset.

        mapping : :class:`dict`
            Table mapping HDF5 dataset columns to data class attributes.

            **Note**: The keys in this dictionary are *integers*,
            not strings, as usual for dictionaries. This allows to directly
            use the keys for indexing the tuple returned by
            ``numpy.dtype.names``.

        Returns
        -------
        importer : :class:`evefile.entities.data.HDF5DataImporter`
            HDF5 dataset importer

        """
        if mapping is None:
            mapping = {}
        importer = entities.data.HDF5DataImporter()
        importer.source = dataset.filename
        importer.item = dataset.name
        for key, value in mapping.items():
            importer.mapping[dataset.dtype.names[key]] = value
        return importer

    @staticmethod
    def get_dataset_name(dataset=None):
        """
        Get the name of an HDF5 dataset.

        The name here refers to the last part of the path within the HDF5
        file, *i.e.* the part after the last slash.


        Parameters
        ----------
        dataset : :class:`evedata.evefile.boundaries.eveh5.HDF5Dataset`
            Representation of an HDF5 dataset.

        Returns
        -------
        name : :class:`str`
            Name of the HDF5 dataset

        """
        return dataset.name.rsplit("/", maxsplit=1)[1]

    @staticmethod
    def set_basic_metadata(hdf5_item=None, dataset=None):
        """
        Set the basic metadata of a dataset from an HDF5 item.

        The metadata attributes ``id``, ``name``, ``access_mode``,
        and ``pv`` are set.

        Parameters
        ----------
        hdf5_item : :class:`evedata.evefile.boundaries.eveh5.HDF5Item`
            Representation of an HDF5 item.

        dataset : :class:`evedata.evefile.entities.data.Data`
            Data object the metadata should be set for

        """
        dataset.metadata.id = hdf5_item.name.split("/")[-1]  # noqa
        dataset.metadata.name = hdf5_item.attributes["Name"]
        dataset.metadata.access_mode, dataset.metadata.pv = (  # noqa
            hdf5_item.attributes
        )["Access"].split(":", maxsplit=1)
        if "Unit" in hdf5_item.attributes:
            dataset.metadata.unit = hdf5_item.attributes["Unit"]

    def _check_prerequisites(self):
        if not self.source:
            raise ValueError("Missing source to map from.")
        if not self.destination:
            raise ValueError("Missing destination to map to.")

    def _set_dataset_names(self):
        pass

    def _map(self):
        self._map_file_metadata()
        # Note: The sequence of method calls can be crucial, as the mapper
        #       contains a list of datasets still to be mapped, and each
        #       mapped dataset is removed from this list.
        self._map_timestamp_dataset()
        self._map_monitor_datasets()
        self._map_axis_datasets()
        self._map_0d_datasets()
        self._map_snapshot_datasets()

    def _map_file_metadata(self):
        pass

    def _map_timestamp_dataset(self):
        pass

    def _map_monitor_datasets(self):
        for name in self.datasets2map_in_monitor:
            monitor = getattr(self._monitor_group, name)
            dataset = entities.data.MonitorData()
            importer_mapping = {
                0: "milliseconds",
                1: "data",
            }
            importer = self.get_hdf5_dataset_importer(
                dataset=monitor, mapping=importer_mapping
            )
            dataset.importer.append(importer)
            self.set_basic_metadata(hdf5_item=monitor, dataset=dataset)
            self.destination.monitors[self.get_dataset_name(monitor)] = (
                dataset
            )

    def _map_axis_datasets(self):
        mapped_datasets = []
        for name in self.datasets2map_in_main:
            item = getattr(self._main_group, name)
            if item.attributes["DeviceType"] == "Axis":
                self._map_axis_dataset(hdf5_dataset=item)
                mapped_datasets.append(self.get_dataset_name(item))
        for item in mapped_datasets:
            self.datasets2map_in_main.remove(item)

    def _map_axis_dataset(self, hdf5_dataset=None, section="data"):
        # TODO: Check whether axis has an encoder (how? mapping?)
        dataset = entities.data.AxisData()
        importer_mapping = {
            0: "position_counts",
            1: "data",
        }
        importer = self.get_hdf5_dataset_importer(
            dataset=hdf5_dataset, mapping=importer_mapping
        )
        dataset.importer.append(importer)
        self.set_basic_metadata(hdf5_item=hdf5_dataset, dataset=dataset)
        self._assign_axis_dataset(dataset, hdf5_dataset, section)

    def _assign_axis_dataset(
        self, dataset=None, hdf5_dataset=None, section=""
    ):
        getattr(self.destination, section)[
            self.get_dataset_name(hdf5_dataset)
        ] = dataset

    def _map_0d_datasets(self):
        pass

    def _map_snapshot_datasets(self):
        mapped_datasets = []
        for name in self.datasets2map_in_snapshot:
            item = getattr(self._snapshot_group, name)
            if item.attributes["DeviceType"] == "Axis":
                self._map_axis_dataset(hdf5_dataset=item, section="snapshots")
                mapped_datasets.append(self.get_dataset_name(item))
            elif item.attributes["DeviceType"] == "Channel":
                self._map_channel_snapshot_dataset(hdf5_dataset=item)
                mapped_datasets.append(self.get_dataset_name(item))
        for item in mapped_datasets:
            self.datasets2map_in_snapshot.remove(item)

    def _map_channel_snapshot_dataset(self, hdf5_dataset=None):
        dataset = entities.data.ChannelData()
        importer_mapping = {
            0: "position_counts",
            1: "data",
        }
        importer = self.get_hdf5_dataset_importer(
            dataset=hdf5_dataset, mapping=importer_mapping
        )
        dataset.importer.append(importer)
        self.set_basic_metadata(hdf5_item=hdf5_dataset, dataset=dataset)
        self.destination.snapshots[self.get_dataset_name(hdf5_dataset)] = (
            dataset
        )


class VersionMapperV5(VersionMapper):
    """
    Mapper for mapping eveH5 v5 file contents to evefile structures.

    More description comes here...

    .. important::
        EveH5 files of version v5 and earlier do *not* contain a date and
        time for the end of the measurement. Hence, the corresponding
        attribute :attr:`File.metadata.end
        <evefile.entities.file.Metadata.end>` is set to the UNIX
        start date (1970-01-01T00:00:00). Thus, with these files,
        it is *not* possible to automatically calculate the duration of
        the measurement.

        Note, however, that using the :attr:`File.position_timestamps
        <evefile.entities.file.File.position_timestamps>` attribute and
        taking the timestamp for the last recorded position count,
        one could infer the duration of the measurement, and hence set the
        time for the end of the measurement.


    Attributes
    ----------
    source : :class:`evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    destination : :class:`evefile.boundaries.evefile.File`
        High(er)-level evefile structure representing an eveH5 file

    Raises
    ------
    ValueError
        Raised if either source or destination are not provided


    Examples
    --------
    Mapping a given eveH5 file to the evefile structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV5()
        mapper.map(source=eveh5, destination=evefile)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5)
        mapper.map(destination=evefile)

    """

    def _set_dataset_names(self):
        super()._set_dataset_names()
        # TODO: Move up to VersionMapperV4
        if hasattr(self.source.c1, "main"):
            self._main_group = self.source.c1.main
            self.datasets2map_in_main = [
                self.get_dataset_name(item)
                for item in self.source.c1.main
                if self.get_dataset_name(item)
                not in ["normalized", "averagemeta", "standarddev"]
            ]
        if hasattr(self.source.c1, "snapshot"):
            self._snapshot_group = self.source.c1.snapshot
            self.datasets2map_in_snapshot = [
                self.get_dataset_name(item)
                for item in self.source.c1.snapshot
            ]
        if hasattr(self.source, "device"):
            self._monitor_group = self.source.device
            self.datasets2map_in_monitor = [
                self.get_dataset_name(item) for item in self._monitor_group
            ]

    def _map(self):
        super()._map()
        self._map_log_messages()

    def _map_file_metadata(self):
        root_mappings = {
            "eveh5_version": "EVEH5Version",
            "eve_version": "Version",
            "xml_version": "XMLversion",
            "measurement_station": "Location",
            "description": "Comment",
        }
        for key, value in root_mappings.items():
            if value in self.source.attributes:
                setattr(
                    self.destination.metadata,
                    key,
                    self.source.attributes[value],
                )
        c1_mappings = {
            "preferred_axis": "preferredAxis",
            "preferred_channel": "preferredChannel",
            "preferred_normalisation_channel": "preferredNormalizationChannel",
        }
        for key, value in c1_mappings.items():
            if value in self.source.c1.attributes:
                setattr(
                    self.destination.metadata,
                    key,
                    self.source.c1.attributes[value],
                )
        if "StartTimeISO" not in self.source.attributes:
            self.destination.metadata.start = datetime.datetime.strptime(
                f"{self.source.attributes['StartDate']} "
                f"{self.source.attributes['StartTime']}",
                "%d.%m.%Y %H:%M:%S",
            )
            self.destination.metadata.end = datetime.datetime(1970, 1, 1)

    def _map_timestamp_dataset(self):
        # TODO: Move up to VersionMapperV2 (at least the earliest one)
        timestampdata = self.source.c1.meta.PosCountTimer
        dataset = entities.data.TimestampData()
        importer_mapping = {
            0: "position_counts",
            1: "data",
        }
        importer = self.get_hdf5_dataset_importer(
            dataset=timestampdata, mapping=importer_mapping
        )
        dataset.importer.append(importer)
        dataset.metadata.unit = timestampdata.attributes["Unit"]
        self.destination.position_timestamps = dataset

    def _map_log_messages(self):
        if not hasattr(self.source, "LiveComment"):
            return
        self.source.LiveComment.get_data()
        for message in self.source.LiveComment.data:
            log_message = entities.file.LogMessage()
            log_message.from_string(message.decode())
            self.destination.log_messages.append(log_message)

    def _map_0d_datasets(self):
        """
        Mapping of 0D datasets.

        There are three types of 0D datasets: SinglePoint, Interval,
        Average. Each of these three types can additionally be normalized.

        Usually, for normalized datasets the data used for normalizing are
        available in the ``main`` group of the eveH5 file. Not so for
        interval channel data, however: Here, the data used for
        normalizing are *not* saved, *i.e.*, there is no corresponding
        dataset in the ``main`` group of the eveH5 file. Therefore,
        in this particular case, ``normalizing_data`` are *not* mapped.

        """
        datasets = list(self.datasets2map_in_main)
        interval_datasets = [
            item
            for item in datasets
            if getattr(self.source.c1.main, item).attributes["Detectortype"]
            == "Interval"
        ]
        for hdf5_name in interval_datasets:
            self._map_interval_dataset(hdf5_name=hdf5_name, normalized=False)
            datasets.remove(hdf5_name)
        average_datasets = []
        if hasattr(self.source.c1, "main") and hasattr(
            self.source.c1.main, "averagemeta"
        ):
            average_datasets = {
                item.name.split("__")[0].split("/")[-1]
                for item in self.source.c1.main.averagemeta
                if item.name.count("__") == 1
            }
        for hdf5_name in average_datasets:
            self._map_average_dataset(hdf5_name=hdf5_name, normalized=False)
            datasets.remove(hdf5_name)
        normalized_datasets = []
        if hasattr(self.source.c1, "main") and hasattr(
            self.source.c1.main, "normalized"
        ):
            normalized_datasets = [
                self.get_dataset_name(item)
                for item in self.source.c1.main.normalized
            ]
            normalized_interval_datasets = [
                self.get_dataset_name(item)
                for item in self.source.c1.main.normalized
                if getattr(
                    self.source.c1.main.normalized,
                    self.get_dataset_name(item),
                ).attributes["Detectortype"]
                == "Interval"
            ]
            for hdf5_name in normalized_interval_datasets:
                normalized_datasets.remove(hdf5_name)
                self._map_interval_dataset(
                    hdf5_name=hdf5_name, normalized=True
                )
            if hasattr(self.source.c1.main, "averagemeta"):
                average_datasets = {
                    item.name.split("__")[0].split("/")[-1]
                    for item in self.source.c1.main.averagemeta
                }
            normalized_average_datasets = [
                self.get_dataset_name(item)
                for item in self.source.c1.main.normalized
                if self.get_dataset_name(item).split("__")[0]
                in average_datasets
            ]
            for hdf5_name in normalized_average_datasets:
                normalized_datasets.remove(hdf5_name)
                datasets.remove(hdf5_name.split("__")[0])
                self._map_average_dataset(
                    hdf5_name=hdf5_name, normalized=True
                )
        for hdf5_name in datasets:
            self._map_singlepoint_dataset(hdf5_name, normalized_datasets)

    def _map_singlepoint_dataset(
        self, hdf5_name=None, normalized_datasets=None
    ):
        importer_mapping = {
            0: "position_counts",
            1: "data",
        }
        importer = self.get_hdf5_dataset_importer(
            dataset=getattr(self.source.c1.main, hdf5_name),
            mapping=importer_mapping,
        )
        normalize_data = [
            item
            for item in normalized_datasets
            if item.startswith(f"{hdf5_name}__")
        ]
        if normalize_data:
            dataset = entities.data.SinglePointNormalizedChannelData()
            dataset.importer.append(importer)
            importer_mapping = {
                1: "normalized_data",
            }
            importer = self.get_hdf5_dataset_importer(
                dataset=getattr(
                    self.source.c1.main.normalized, normalize_data[0]
                ),
                mapping=importer_mapping,
            )
            dataset.importer.append(importer)
            importer_mapping = {
                1: "normalizing_data",
            }
            normalizing_data = normalize_data[0].split("__")[1]
            importer = self.get_hdf5_dataset_importer(
                dataset=getattr(self.source.c1.main, normalizing_data),
                mapping=importer_mapping,
            )
            dataset.importer.append(importer)
            dataset.metadata.normalize_id = normalizing_data
        else:
            dataset = entities.data.SinglePointChannelData()
            dataset.importer.append(importer)
        self.set_basic_metadata(
            hdf5_item=getattr(self.source.c1.main, hdf5_name),
            dataset=dataset,
        )
        self.destination.data[hdf5_name] = dataset
        self.datasets2map_in_main.remove(hdf5_name)

    def _map_interval_dataset(self, hdf5_name=None, normalized=False):
        importer_mapping = {
            0: "position_counts",
            1: "data",
        }
        if normalized:
            importer = self.get_hdf5_dataset_importer(
                dataset=getattr(self.source.c1.main.normalized, hdf5_name),
                mapping=importer_mapping,
            )
            dataset = entities.data.IntervalNormalizedChannelData()
        else:
            importer = self.get_hdf5_dataset_importer(
                dataset=getattr(self.source.c1.main, hdf5_name),
                mapping=importer_mapping,
            )
            dataset = entities.data.IntervalChannelData()
        dataset.importer.append(importer)
        importer_mapping = {
            1: "counts",
        }
        importer = self.get_hdf5_dataset_importer(
            dataset=getattr(
                self.source.c1.main.standarddev, f"{hdf5_name}__Count"
            ),
            mapping=importer_mapping,
        )
        dataset.importer.append(importer)
        importer_mapping = {
            2: "std",
        }
        trigger_interval_std = getattr(
            self.source.c1.main.standarddev,
            f"{hdf5_name}__TrigIntv-StdDev",
        )
        importer = self.get_hdf5_dataset_importer(
            dataset=trigger_interval_std,
            mapping=importer_mapping,
        )
        dataset.importer.append(importer)
        dataset.metadata.trigger_interval = trigger_interval_std.data[
            "TriggerIntv"
        ][0]
        if normalized:
            importer_mapping = {
                1: "normalized_data",
            }
            importer = self.get_hdf5_dataset_importer(
                dataset=getattr(
                    self.source.c1.main.normalized, f"{hdf5_name}"
                ),
                mapping=importer_mapping,
            )
            dataset.importer.append(importer)
            self.set_basic_metadata(
                hdf5_item=getattr(self.source.c1.main.normalized, hdf5_name),
                dataset=dataset,
            )
        else:
            self.set_basic_metadata(
                hdf5_item=getattr(self.source.c1.main, hdf5_name),
                dataset=dataset,
            )
            self.datasets2map_in_main.remove(hdf5_name)
        self.destination.data[hdf5_name] = dataset

    def _map_average_dataset(self, hdf5_name=None, normalized=False):
        if normalized:
            basename = hdf5_name.split("__")[0]
            dataset = entities.data.AverageNormalizedChannelData()
        else:
            basename = hdf5_name
            dataset = entities.data.AverageChannelData()
        importer_mapping = {
            0: "position_counts",
            1: "data",
        }
        importer = self.get_hdf5_dataset_importer(
            dataset=getattr(self.source.c1.main, basename),
            mapping=importer_mapping,
        )
        dataset.importer.append(importer)
        if hasattr(self.source.c1.main.averagemeta, f"{hdf5_name}__Attempts"):
            importer_mapping = {
                1: "attempts",
            }
            importer = self.get_hdf5_dataset_importer(
                dataset=getattr(
                    self.source.c1.main.averagemeta, f"{hdf5_name}__Attempts"
                ),
                mapping=importer_mapping,
            )
            dataset.importer.append(importer)
            dataset.metadata.max_attempts = getattr(
                self.source.c1.main.averagemeta,
                f"{hdf5_name}__Attempts",
            ).data["MaxAttempts"][0]
            dataset.metadata.low_limit = getattr(
                self.source.c1.main.averagemeta,
                f"{hdf5_name}__Limit-MaxDev",
            ).data["Limit"][0]
            dataset.metadata.max_deviation = getattr(
                self.source.c1.main.averagemeta,
                f"{hdf5_name}__Limit-MaxDev",
            ).data["maxDeviation"][0]
        if normalized:
            importer_mapping = {
                1: "normalized_data",
            }
            importer = self.get_hdf5_dataset_importer(
                dataset=getattr(self.source.c1.main.normalized, hdf5_name),
                mapping=importer_mapping,
            )
            dataset.importer.append(importer)
            importer_mapping = {
                1: "normalizing_data",
            }
            importer = self.get_hdf5_dataset_importer(
                dataset=getattr(
                    self.source.c1.main, hdf5_name.split("__")[1]
                ),
                mapping=importer_mapping,
            )
            dataset.importer.append(importer)
        self.set_basic_metadata(
            hdf5_item=getattr(self.source.c1.main, basename),
            dataset=dataset,
        )
        dataset.metadata.n_averages = getattr(
            self.source.c1.main.averagemeta,
            f"{hdf5_name}__AverageCount",
        ).data["AverageCount"][0]
        self.destination.data[basename] = dataset
        self.datasets2map_in_main.remove(basename)
        if hdf5_name in self.datasets2map_in_main:
            self.datasets2map_in_main.remove(hdf5_name)


class VersionMapperV6(VersionMapperV5):
    """
    Mapper for mapping eveH5 v6 file contents to evefile structures.

    The only difference to the previous version v5: Times for start *and
    now even end* of a measurement are available and are mapped
    as :obj:`datetime.datetime` objects onto the
    :attr:`File.metadata.start
    <evefile.entities.file.Metadata.start>` and
    :attr:`File.metadata.end <evefile.entities.file.Metadata.end>`
    attributes, respectively.

    .. note::
        Previous to v6 eveH5 files, no end date/time of the measurement
        was available, hence no duration of the measurement can be
        calculated.

    Attributes
    ----------
    source : :class:`evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    destination : :class:`evefile.boundaries.evefile.File`
        High(er)-level evefile structure representing an eveH5 file

    Raises
    ------
    ValueError
        Raised if either source or destination are not provided


    Examples
    --------
    Mapping a given eveH5 file to the evefile structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV6()
        mapper.map(source=eveh5, destination=evefile)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5)
        mapper.map(destination=evefile)

    """

    def _map_file_metadata(self):
        super()._map_file_metadata()
        date_mappings = {
            "start": "StartTimeISO",
            "end": "EndTimeISO",
        }
        for key, value in date_mappings.items():
            setattr(
                self.destination.metadata,
                key,
                datetime.datetime.fromisoformat(
                    self.source.attributes[value]
                ),
            )


class VersionMapperV7(VersionMapperV6):
    """
    Mapper for mapping eveH5 v7 file contents to evefile structures.

    The only difference to the previous version v6: the attribute
    ``Simulation`` has beem added on the file root level and is mapped
    as a Boolean value onto the :attr:`File.metadata.simulation
    <evefile.entities.file.Metadata.simulation>` attribute.

    Attributes
    ----------
    source : :class:`evefile.boundaries.eveh5.HDF5File`
        Python object representation of an eveH5 file

    destination : :class:`evefile.boundaries.evefile.File`
        High(er)-level evefile structure representing an eveH5 file

    Raises
    ------
    ValueError
        Raised if either source or destination are not provided


    Examples
    --------
    Mapping a given eveH5 file to the evefile structures is the same for
    each of the mappers:

    .. code-block::

        mapper = VersionMapperV7()
        mapper.map(source=eveh5, destination=evefile)

    Usually, you will obtain the correct mapper from the
    :class:`VersionMapperFactory`. In this case, the returned mapper has
    its :attr:`source` attribute already set for convenience:

    .. code-block::

        factory = VersionMapperFactory()
        mapper = factory.get_mapper(eveh5=eveh5)
        mapper.map(destination=evefile)

    """

    def _map_file_metadata(self):
        super()._map_file_metadata()
        if self.source.attributes["Simulation"] == "yes":
            self.destination.metadata.simulation = True
