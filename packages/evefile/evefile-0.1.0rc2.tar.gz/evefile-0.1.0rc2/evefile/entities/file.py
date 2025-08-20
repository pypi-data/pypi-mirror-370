"""

*Entities representing an eveH5 file on the entire file level.*

While the entities in this module represent the contents of an eveH5 file,
they clearly abstract from the internal structure of these files.
Furthermore, there are different versions of the underlying schema
(*i.e.*, organisation) of these files, and the entities abstract away from
these differences as well. The key concept is to provide users of the
``evefile`` interface with useful abstractions allowing to conveniently
access all the data present in an eveH5 file.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evefile.entities.file.*
    :align: center

    Class hierarchy of the :mod:`evefile.entities.file` module. The
    :class:`File` class is sort of the central interface to the entire
    subpackage, as this class provides a faithful representation of all
    information available from a given eveH5 file. To this end,
    it incorporates instances of classes of the other modules of the
    subpackage. Furthermore, "Scan" inherits from the identically named
    facade of the scan functional layer and contains the full information
    of the SCML file (if the SCML file is present in the eveH5 file).


Module documentation
====================

"""

import datetime
import logging

logger = logging.getLogger(__name__)


class File:
    """
    Representation of all information available from a given eveH5 file.

    Individual measurements are saved in HDF5 files using a particular
    schema (eveH5). Besides file-level metadata, there are log messages
    and the actual data.

    The data are organised in three functionally different sections: data,
    snapshots, and monitors.


    Attributes
    ----------
    metadata : :class:`Metadata`
        File metadata

    log_messages : :class:`list`
        Log messages from an individual measurement

        Each item in the list is an instance of :class:`LogMessage`.

    data : :class:`dict`
        Data recorded from the devices involved in the scan.

        Each item is an instance of
        :class:`evefile.entities.data.Data`.

    snapshots : :class:`dict`
        Device data recorded as snapshot during a measurement.

        Each item is an instance of
        :class:`evefile.entities.data.Data`.

    monitors : :class:`dict`
        Device data monitored during a measurement.

        Each item is an instance of
        :class:`evefile.entities.data.Data`.

    position_timestamps : :class:`evefile.entities.data.TimestampData`
        Timestamps for each individual position.

        Monitors have timestamps (milliseconds since start of the scan)
        rather than positions as primary quantisation axis. This object
        provides a mapping between timestamps and positions and can be used
        to map monitor data to positions.


    Examples
    --------
    The :class:`File` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the ``evefile`` package.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.metadata = Metadata()
        self.log_messages = []
        self.data = {}
        self.snapshots = {}
        self.monitors = {}
        self.position_timestamps = None


class Metadata:
    """
    Metadata of a given eveH5 file.

    As measurements result in individual files, there is a series of
    crucial metadata of such a measurement on this global level.


    Attributes
    ----------
    filename : :class:`str`
        Name (full path) of the eveH5 file.

    eveh5_version : :class:`str`
        Version of the eveH5 schema.

    eve_version : :class:`str`
        Version of the eve engine used to record the data.

    xml_version : :class:`str`
        Version of the schema used for the scan description (SCML/XML)

    measurement_station : :class:`str`
        Name of the measurement station used to record the data.

    start : :class:`datetime.datetime`
        Timestamp of the start of the measurement

    end : :class:`datetime.datetime`
        Timestamp of the end of the measurement

    description : :class:`str`
        User-entered description of the entire scan.

    simulation : :class:`bool`
        Flag signalling whether the measurement was a simulation.

        Default: ``False``

    preferred_axis : :class:`string`
        Name of the axis marked as preferred in the scan description.

        Default: ""

    preferred_channel : :class:`string`
        Name of the channel marked as preferred in the scan description.

        Default: ""

    preferred_normalisation_channel : :class:`string`
        Name of the channel marked as preferred for normalising.

        Default: ""

    Examples
    --------
    The :class:`Metadata` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the ``evefile`` package.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    Nevertheless, as you may use the class indirectly, one important feature
    should be highlighted here: the string representation used if you just
    apply :func:`print` to an object of the class:

    .. code-block::

        print(Metadata())

    The output of an (empty) object would look as follows:

    .. code-block:: bash

                               filename:
                          eveh5_version:
                            eve_version:
                            xml_version:
                    measurement_station:
                                  start: 2025-08-07 10:57:16.849298
                                    end: 2025-08-07 10:57:16.849307
                            description:
                             simulation: False
                         preferred_axis:
                      preferred_channel:
        preferred_normalisation_channel:

    This can be used to get a convenient overview of the metadata contained
    in a loaded eveH5 file.

    """

    def __init__(self):
        self.filename = ""
        self.eveh5_version = ""
        self.eve_version = ""
        self.xml_version = ""
        self.measurement_station = ""
        self.start = datetime.datetime.now()
        self.end = datetime.datetime.now()
        self.description = ""
        self.simulation = False
        self.preferred_axis = ""
        self.preferred_channel = ""
        self.preferred_normalisation_channel = ""

    def __str__(self):
        """
        Human-readable representation of the metadata.

        Returns
        -------
        output : :class:`str`
            Multiline string with one attribute per line

        """
        output = []
        # Note: Attributes are listed manually here for explicit ordering
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
        attribute_name_length = max(
            len(attribute) for attribute in attributes
        )
        for attribute in attributes:
            output.append(
                f"{attribute:>{attribute_name_length}}:"
                f" {getattr(self, attribute)}"
            )
        return "\n".join(output)


class LogMessage:
    """
    Log message from an individual measurement.

    Operators can enter log messages during a measurement using the
    eve-gui. In such case, the respective message appears in the eveH5
    file together with a timestamp.


    Attributes
    ----------
    timestamp : :class:`datetime.datetime`
        Timestamp of the log message

    message : :class:`str`
        Actual content of the log message.


    Examples
    --------
    The :class:`Scan` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the ``evefile`` package.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        self.timestamp = datetime.datetime.now()
        self.message = ""

    def from_string(self, string=""):
        """
        Set attributes from string.

        In eveH5 files up to v7, the log messages are single strings with
        the ISO timestamp at the beginning, followed by the actual message.
        Timestamp and message are separated by ": ".

        This method separates both parts and converts the timestamp into an
        actual :obj:`datetime.datetime` object, consistent with the
        :attr:`timestamp` attribute.

        Parameters
        ----------
        string : :class:`str`
            Log message consisting of timestamp and actual message.

        """
        timestamp, message = string.split(": ", maxsplit=1)
        self.timestamp = datetime.datetime.fromisoformat(timestamp)
        self.message = message

    def __str__(self):
        """
        Human-readable representation of the log message.

        Returns
        -------
        output : :class:`str`
            String containing timestamp and log message

        """
        return f"{self.timestamp.isoformat()}: {self.message}"
