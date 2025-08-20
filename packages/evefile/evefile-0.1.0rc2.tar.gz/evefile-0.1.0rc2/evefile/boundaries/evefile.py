"""

*High-level Python object representation of eveH5 file contents.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

This module provides a high-level representation of the contents of an eveH5
file. Being a high-level, user-facing object representation, technically
speaking this module is a facade. The corresponding resource
(persistence-layer-facing interface) would be the :mod:`eveh5
<evefile.boundaries.eveh5>` module.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evefile.boundaries.evefile.*
    :align: center

    Class hierarchy of the :mod:`evefile.boundaries.evefile` module,
    providing the facade (user-facing interface) for an eveH5 file.
    Basically, it inherits from :class:`evefile.entities.file.File`
    and adds behaviour. Most of this behaviour is contributed by the various
    modules of the :mod:`controllers <evefile.controllers>`
    subpackage.


Key aspects
===========

While the :mod:`evefile <evefile.boundaries.evefile>` module is the
high-level interface (facade) of the ``evefile`` package,
it is still, from a functional viewpoint, close to the actual eveH5 files,
providing a faithful representation of all information contained in an eveH5
file. Nevertheless, it is clearly an abstraction from the actual data files.
Hence, the key characteristics of the module are:

* Stable interface to eveH5 files, regardless of their version.

  * Some features may only be available for newer eveH5 versions, though.

* Powerful abstractions on the device level.

  * Options to devices appear as attributes of the device objects, not as
    separate datasets.

* Actual **data are loaded on demand**, not when loading the file.

  * This does *not* apply to the metadata of the individual datasets.
    Those are read upon reading the file.
  * Reading data on demand should save time and resources, particularly
    for larger files.
  * Often, you are only interested in a subset of the available data.


Usage
=====

Loading the contents of a data file of a measurement may be as simple as:

.. code-block::

    evefile = EveFile(filename="my_measurement_file.h5")

If you are interested in a convenient overview of the contents of the
eveH5 file just loaded, try this:

.. code-block::

    evefile.show_info()

This will output a human-readable summary of the file metadata,
log messages, and a list of datasets in the data, snapshot, and monitor
section. See the documentation of the :meth:`EveFile.show_info` method for
details.

Data are stored within a :class:`EveFile` object with their IDs rather than
the "given" names users are familiar with. Hence, to get an overview of all
the data(sets) contained in a file, use the :meth:`EveFile.get_data_names`
method:

.. code-block::

    evefile.get_data_names()

This will return a list of "given" data names.

Similarly, if you know the "given" name of a dataset or a list of datasets,
you can retrieve the corresponding :class:`Data <evefile.entities.data.Data>`
objects by using the :meth:`EveFile.get_data` method:

.. code-block::

    # Get list of datasets by name
    evefile.get_data(["name1", "name2"])

    # Get single dataset by name
    evefile.get_data("name")

To get the data marked as preferred in the scan, use the
:meth:`EveFile.get_preferred_data` method:

.. code-block::

    evefile.get_preferred_data()

This will return a list with three elements, ``[preferred_axis,
preferred_channel, preferred_normalisation_channel]``, where each of these
elements is either of type :class:`evefile.entities.data.Data` or
:obj:`None`.


Internals: What happens when reading an eveH5 file?
===================================================

Reading an eveH5 file is not as simple as reading contents of an HDF5 file
and present its contents as Python object hierarchy. At least, if you would
like to view, process, and analyse your data more conveniently, you should
not stop here. The idea behind the ``evefile`` package, and in parts behind
the :class:`EveFile` class, is to provide you as consumer of the data with
powerful abstractions and structured information. To this end, a series of
steps are necessary:

* Read the eveH5 file (actually, an HDF5 file).
* Get the correct :class:`VersionMapper
  <evefile.controllers.version_mapping.VersionMapper>` class.
* Map the file contents to the proper :mod:`data structures
  <evefile.entities.data>` provided by the ``evefile`` package.


Module documentation
====================

"""

import logging
import os

import pandas as pd

from evefile.entities.file import File
from evefile.boundaries.eveh5 import HDF5File
from evefile.controllers import version_mapping, joining


logger = logging.getLogger(__name__)


class EveFile(File):
    """
    High-level Python object representation of eveH5 file contents.

    This class serves as facade to the entire ``evefile`` package and provides
    a rather high-level representation of the contents of an individual
    eveH5 file.

    Individual measurements are saved in HDF5 files using a particular
    schema (eveH5). Besides file-level metadata, there are log messages
    and the actual data.

    The data are organised in three functionally different sections: data,
    snapshots, and monitors. While the "data" section contains the data of
    motor axes moved and detector channels read out during the scan,
    the "snapshot" section contains values at distinct times (usually at
    the very beginning of a scan), usually of more devices than used in
    the scan. The "monitors" section contains data of all those devices
    monitored during the scan, meaning that only changes in values are
    recorded, together with their timestamp (rather than position count).

    Values from axes contained in the "snapshot" section are used for data
    joining, while all other values can be regarded as either options
    of individual devices or telemetry data for the setup. All values from
    the "monitors" section are strictly telemetry data for the setup.


    Attributes
    ----------
    metadata : :class:`evefile.entities.file.Metadata`
        File metadata

    log_messages : :class:`list`
        Log messages from an individual measurement

        Each item in the list is an instance of
        :class:`evefile.entities.file.LogMessage`.

    data : :class:`dict`
        Data recorded from the devices involved in the scan.

        The keys of the dictionary are the (guaranteed to be unique) HDF
        dataset names, not the "given" names usually familiar to the users.
        Use the :meth:`get_data` method to retrieve data objects by their
        "given" name.

        Each item is an instance of
        :class:`evefile.entities.data.Data`.

    snapshots : :class:`dict`
        Device data recorded as snapshot during a measurement.

        Only those device data that are not options belonging to any of
        the devices in the :attr:`data` attribute are stored here.

        The keys of the dictionary are the (guaranteed to be unique) HDF
        dataset names, not the "given" names usually familiar to the users.

        Each item is an instance of
        :class:`evefile.entities.data.Data`.

    monitors : :class:`dict`
        Device data monitored during a measurement.

        The keys of the dictionary are the (guaranteed to be unique) HDF
        dataset names, not the "given" names usually familiar to the users.

        Each item is an instance of
        :class:`evefile.entities.data.MonitorData`.

    position_timestamps : :class:`evefile.entities.data.TimestampData`
        Timestamps for each individual position.

        Monitors have timestamps (milliseconds since start of the scan)
        rather than positions as primary quantisation axis. This object
        provides a mapping between timestamps and positions and can be used
        to map monitor data to positions.


    Parameters
    ----------
    filename : :class:`str`
        Name of the file to be loaded.


    Raises
    ------
    ValueError
        Raised if no filename is provided.

    FileNotFoundError
        Raised if provided file could not be found.


    Examples
    --------
    Loading the contents of a data file of a measurement may be as simple as:

    .. code-block::

        evefile = EveFile(filename="my_measurement_file.h5")

    """

    def __init__(self, filename="", load=True):
        super().__init__()
        self.filename = filename
        self._join_factory = joining.JoinFactory(evefile=self)
        if load:
            if not filename:
                raise ValueError("No filename given")
            if not os.path.exists(filename):
                raise FileNotFoundError(f"File {filename} does not exist.")
            self._read_and_map_eveh5_file()

    @property
    def filename(self):
        """
        Name of the file to be loaded.

        Returns
        -------
        filename : :class:`str`
            Name of the file to be loaded.

        """
        return self.metadata.filename

    @filename.setter
    def filename(self, filename=""):
        self.metadata.filename = filename

    def _read_and_map_eveh5_file(self):
        eveh5 = HDF5File()
        eveh5.read_attributes = True
        eveh5.close_file = False
        eveh5.read(filename=self.metadata.filename)
        mapper_factory = version_mapping.VersionMapperFactory()
        mapper = mapper_factory.get_mapper(eveh5)
        mapper.map(source=eveh5, destination=self)
        eveh5.close()

    def get_data(self, name=None):
        """
        Retrieve data objects by name.

        While generally, you can get the data objects by accessing the
        :attr:`data <evefile.entities.file.File.data>` attribute directly,
        there, they are stored using their HDF5 dataset name as key.
        Usually, however, data are accessed by their "given" name.

        Parameters
        ----------
        name : :class:`str` | :class:`list`
            Name or list of names of data to retrieve

        Returns
        -------
        data : :class:`evefile.entities.data.Data` | :class:`list`
            Data object(s) corresponding to the name(s).

            In case of a list of data objects, each object is of type
            :class:`evefile.entities.data.Data`.

        """
        data = []
        names = {item.metadata.name: key for key, item in self.data.items()}
        if isinstance(name, (list, tuple)):
            for item in name:
                data.append(self.data[names[item]])
        else:
            data.append(self.data[names[name]])
        if len(data) == 1:
            data = data[0]
        return data

    def get_data_names(self):
        """
        Retrieve "given" names of data objects.

        Data are stored in the :attr:`data <evefile.entities.file.File.data>`
        attribute using their HDF5 dataset name as key. Usually, however,
        data are accessed by their "given" name.

        This method returns a list of all "given" names of the datasets
        stored in :attr:`data <evefile.entities.file.File.data>`.

        Returns
        -------
        data : :class:`list`
            List of names of the data object(s) in :attr:`data`.

        """
        names = [item.metadata.name for key, item in self.data.items()]
        return names

    def get_preferred_data(self):
        """
        Retrieve data objects marked as preferred.

        Within a scan, a preferred motor axis, a preferred detector
        channel, and a preferred channel for normalisation can be
        named explicitly. The preferred axis and channel are used for
        plotting within the eve GUI during measurement.

        .. note::

            The datasets returned are guaranteed to be commensurate
            and compatible and can hence directly be plotted against each
            other. This is due to the fact that preferred axis and channel
            currently must come from the same scan module of a scan.

        Returns
        -------
        data : :class:`list`
            Data objects corresponding to the preference settings.

            A list with three elements:

            #. preferred axis
            #. preferred channel
            #. preferred normalisation channel

            If the preference has been set in the scan description,
            the item in the list is of type
            :class:`evefile.entities.data.MeasureData`, otherwise
            :obj:`None`.

        """
        output = [None, None, None]
        if self.metadata.preferred_axis:
            output[0] = self.data[self.metadata.preferred_axis]
        if self.metadata.preferred_channel:
            output[1] = self.data[self.metadata.preferred_channel]
        if self.metadata.preferred_normalisation_channel:
            output[2] = self.data[
                self.metadata.preferred_normalisation_channel
            ]
        return output

    def get_joined_data(self, data=None, mode="AxisOrChannelPositions"):
        """
        Retrieve data objects with commensurate dimensions.

        For details on joining see the :mod:`joining
        <evefile.controllers.joining>` module.

        Parameters
        ----------
        data : :class:`list`
            (Names/IDs of) data objects whose data should be joined.

            You can provide either names or IDs or the actual data objects.

            If no data are given, by default all data available will be
            joined.

            Default: :obj:`None`

        mode : :class:`str`
            Name of the join mode to be used. This must be a mode
            understood by the :class:`JoinFactory
            <evefile.controllers.joining.JoinFactory>`.

            Default: "AxisOrChannelPositions"

        Returns
        -------
        data : :class:`list`
            List of data objects.

            Each item in the list is of type
            :class:`evefile.entities.data.MeasureData`.

        """
        if not data:
            data = list(self.data.values())
        joiner = self._join_factory.get_join(mode=mode)
        return joiner.join(data)

    def get_dataframe(self, data=None, mode="AxisOrChannelPositions"):
        """
        Retrieve Pandas DataFrame with given data objects as columns.

        Internally, the :meth:`get_joined_data` method will be called with
        the data provided. If the ``data`` parameter is omitted,
        all datasets will be used.

        The names of the columns of the returned DataFrame are the names (not
        IDs) of the respective datasets.

        .. important::

            While working with a Pandas DataFrame may seem convenient,
            you're loosing basically all the relevant metadata of the
            datasets. Hence, this method is rather a convenience method to
            be backwards-compatible to older interfaces, but it is
            explicitly *not* suggested for extensive use.


        Parameters
        ----------
        data : :class:`list`
            (Names/IDs of) data objects whose data should be joined.

            You can provide either names or IDs or the actual data objects.

            If no data are given, by default all data available will be
            joined.

            Default: :obj:`None`

        mode : :class:`str`
            Name of the join mode to be used. This must be a mode
            understood by the :class:`JoinFactory
            <evefile.controllers.joining.JoinFactory>`.

            Default: "AxisOrChannelPositions"

        Returns
        -------
        dataframe : :class:`pandas.DataFrame`
            Pandas DataFrame containing the given data objects as columns.

            The names of the columns are the names (not IDs) of the
            respective datasets.

        """
        if not data:
            data = list(self.data.values())
        joined_data = self.get_joined_data(data=data, mode=mode)
        dataframe = pd.DataFrame(
            {item.metadata.name: item.data for item in joined_data}
        )
        dataframe.index.name = "position"
        return dataframe

    def show_info(self):
        """
        Print basic information regarding the contents of the loaded file.

        Often, it is convenient to get a brief overview of the contents of
        a file after it has been loaded. The output of this method
        currently contains the following sections:

        * metadata
        * log messages
        * data
        * snapshots
        * monitors

        The output could look similar to the following:

        .. code-block:: none

            METADATA
                                   filename: file.h5
                              eveh5_version: 7
                                eve_version: 2.0
                                xml_version: 9.2
                        measurement_station: Unittest
                                      start: 2024-06-03 12:01:32
                                        end: 2024-06-03 12:01:37
                                description:
                                 simulation: False
                             preferred_axis: SimMot:01
                          preferred_channel: SimChan:01
            preferred_normalisation_channel: SimChan:01

            LOG MESSAGES
            20250812T09:06:05: Lorem ipsum

            DATA
            foo (SimMot:01) <AxisData>
            bar (SimChan:01) <SinglePointChannelData>

            SNAPSHOTS
            bar (SimChan:01) <AxisData>
            bazfoo (SimChan:03) <AxisData>
            foo (SimMot:01) <AxisData>

            MONITORS

        """
        print("METADATA")
        print(self.metadata)
        print("\nLOG MESSAGES")
        for message in self.log_messages:
            print(message)
        print("\nDATA")
        for item in self.data.values():
            print(item)
        print("\nSNAPSHOTS")
        for item in self.snapshots.values():
            print(item)
        print("\nMONITORS")
        for item in self.monitors.values():
            print(item)
