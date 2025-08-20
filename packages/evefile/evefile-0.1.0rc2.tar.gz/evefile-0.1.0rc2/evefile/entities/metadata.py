"""

*Metadata classes corresponding to the data entities.*

Data without context (*i.e.* metadata) are mostly useless. Hence, to every
class (type) of data in the :mod:`evefile.entities.data` module,
there exists a corresponding metadata class in this module.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.

.. figure:: /uml/evefile.entities.metadata.*
    :align: center
    :width: 750px

    Class hierarchy of the :mod:`evefile.entities.metadata` module.
    Each concrete class in the :mod:`evefile.entities.data` module
    has a corresponding metadata class in this module.
    You may click on the image for a larger view.


A note on the :class:`AbstractDeviceMetadata` interface class: The eveH5
dataset corresponding to the :class:`TimestampMetadata` class is special in
sense of having no PV and transport type nor an id. Several options have been
considered to address this problem:

#. Moving these three attributes down the line and copying them multiple
   times (feels bad).
#. Leaving the attributes blank for the "special" dataset (feels bad, too).
#. Introduce another class in the hierarchy, breaking the parallel to the
   Data class hierarchy (potentially confusing).
#. Create a mixin class (abstract interface) with the three attributes and
   use multiple inheritance/implements.

As obvious from the UML diagram, the last option has been chosen. The name
"DeviceMetadata" clearly distinguishes actual devices from datasets not
containing data read from some instrument.


The following is not a strict inheritance hierarchy, but rather a grouped
hierarchical list of classes for quick access to their individual API
documentation:

* :class:`Metadata`

  * :class:`MonitorMetadata`
  * :class:`MeasureMetadata`

    * :class:`DeviceMetadata`
    * :class:`TimestampMetadata`
    * :class:`AxisMetadata`

    * :class:`ChannelMetadata`

      * :class:`SinglePointChannelMetadata`

        * :class:`SinglePointNormalizedChannelMetadata`

      * :class:`AverageChannelMetadata`

        * :class:`AverageNormalizedChannelMetadata`

      * :class:`IntervalChannelMetadata`

        * :class:`IntervalNormalizedChannelMetadata`


Module documentation
====================

"""

import copy
import logging

logger = logging.getLogger(__name__)


class Metadata:
    """
    Metadata for the devices involved in a measurement.

    This is the base class for all data(sets) and not meant to be used
    directly. Rather, one of the individual subclasses should actually be
    used.

    This class complements the class
    :class:`evefile.entities.data.Data`.

    Attributes
    ----------
    name : :class:`str`
        Name of the device.

        Devices are uniquely identified by an ID that usually corresponds
        to the EPICS process variable (PV). However, most devices have
        "given" names as well that provide a more human-readable alternative.

    options : :class:`dict`
        (Scalar) options of the device.

        Devices can have options. Generally, there are two types of
        options: those whose values are *not* changing within a given scan
        module, and those whose values can potentially change for every
        individual position (count). The former are stored here as
        key--value pairs with the key corresponding to the option name.
        The latter are stored in the
        :attr:`evefile.entities.data.Data.options` attribute.

    Examples
    --------
    The :class:`Metadata` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the ``evefile`` package.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.name = ""
        self.options = {}
        # Note: Attributes are listed manually here for explicit ordering in
        #       string representation using self.__str__
        # Use only append or extend in subclasses!
        self._attributes = ["name"]

    def __str__(self):
        """
        Human-readable representation of the metadata.

        Returns
        -------
        output : :class:`str`
            Multiline string with one attribute per line

        """
        output = []
        attribute_name_length = max(
            len(attribute) for attribute in self._attributes
        )
        for attribute in self._attributes:
            output.append(
                f"{attribute:>{attribute_name_length}}:"
                f" {getattr(self, attribute)}"
            )
        if self.options:
            key_name_length = max(len(key) for key in self.options)
            output.append("")
            output.append("SCALAR OPTIONS")
            for key, value in self.options.items():
                output.append(f"{key:>{key_name_length}}:" f" {value}")
        return "\n".join(output)

    def copy_attributes_from(self, source=None):
        """
        Obtain attributes from another :obj:`Metadata` object.

        Sometimes, it is useful to obtain the (public) attributes from
        another :obj:`Metadata` object. Note that only public attributes are
        copied. Furthermore, a (true) copy of the attributes is obtained,
        hence the properties of source and target are actually different
        objects.

        Parameters
        ----------
        source : :class:`Metadata`
            Object to copy attributes from.

            Should typically be of the same (super)type.

        Raises
        ------
        ValueError
            Raised if no source is provided to copy attributes from.

        """
        if not source:
            raise ValueError("No source provided to copy attributes from.")
        public_attributes = [
            item
            for item in self.__dict__
            if not (item.startswith("_") or item == "metadata")
        ]
        for attribute in public_attributes:
            try:
                setattr(
                    self, attribute, copy.copy(getattr(source, attribute))
                )
            except AttributeError:
                logger.debug(
                    "Cannot set non-existing attribute %s", attribute
                )


class AbstractDeviceMetadata:
    """
    Mixin class (interface) for metadata of actual physical devices.

    Each physical device has a unique ID and can be accessed by an EPICS
    process variable (PV).


    Attributes
    ----------
    id : :class:`str`
        Unique ID of the device.

    pv : :class:`str`
        EPICS process variable (PV) used to access the physical device.

    access_mode : :class:`str`
        Method used to access the EPICS PV.

    Examples
    --------
    The :class:`AbstractDeviceMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.id = ""  # pylint: disable=invalid-name
        self.pv = ""  # pylint: disable=invalid-name
        self.access_mode = ""


class MonitorMetadata(Metadata, AbstractDeviceMetadata):
    """
    Metadata for monitor data.

    This class complements the class
    :class:`evefile.entities.data.MonitorData`.


    Examples
    --------
    The :class:`MonitorMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self._attributes.extend(["id", "pv", "access_mode"])


class MeasureMetadata(Metadata):
    """
    Metadata for data that are actually measured.

    This class complements the class
    :class:`evefile.entities.data.MeasureData`.


    Attributes
    ----------
    unit : :class:`string`
        Name of the unit corresponding to the data.


    Examples
    --------
    The :class:`MeasureMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.unit = ""
        self._attributes.append("unit")


class DeviceMetadata(MeasureMetadata, AbstractDeviceMetadata):
    """
    Metadata for device data.

    This class complements the class
    :class:`evefile.entities.data.DeviceData`.


    Examples
    --------
    The :class:`DeviceMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self._attributes.extend(["id", "pv", "access_mode"])


class AxisMetadata(MeasureMetadata, AbstractDeviceMetadata):
    """
    Metadata for axis data.

    This class complements the class
    :class:`evefile.entities.data.AxisData`.


    Examples
    --------
    The :class:`AxisMetadata` class is not meant to be used directly, as any
    entities, but rather indirectly by means of the respective facades in
    the boundaries technical layer of the ``evefile`` package.
    Hence, for the time being, there are no dedicated examples how to use
    this class. Of course, you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.deadband = 0.0
        self._attributes.extend(["id", "pv", "access_mode", "deadband"])


class ChannelMetadata(MeasureMetadata, AbstractDeviceMetadata):
    """
    Metadata for channel data.

    This class complements the class
    :class:`evefile.entities.data.ChannelData`.


    Examples
    --------
    The :class:`ChannelMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self._attributes.extend(["id", "pv", "access_mode"])


class TimestampMetadata(MeasureMetadata):
    """
    Metadata for the special dataset mapping timestamps to positions.

    This class complements the class
    :class:`evefile.entities.data.TimestampData`.


    Examples
    --------
    The :class:`TimestampMetadata` class is not meant to be used directly,
    as any entities, but rather indirectly by means of the respective
    facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class SinglePointChannelMetadata(ChannelMetadata):
    """
    Metadata for channels with numeric 0D data.

    This class complements the class
    :class:`evefile.entities.data.SinglePointChannelData`.


    Examples
    --------
    The :class:`SinglePointChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """


class AverageChannelMetadata(ChannelMetadata):
    """
    Metadata for channels with averaged numeric 0D data.

    This class complements the class
    :class:`evefile.entities.data.AverageChannelData`.


    Attributes
    ----------
    n_averages : :class:`int`
        Number of averages

    low_limit : :class:`float`
        Minimum value for first reading of the channel

        If set, the value of the channel is read and needs to be larger
        than this minimum value to start the comparison phase.

    max_attempts : :class:`float`
        Maximum number of attempts for reading the channel data.

    max_deviation : :class:`float`
        Maximum deviation allowed between two values in the comparison phase.

        If the :attr:`low_limit` is set, as soon as the value of the
        channel is larger than the low limit, the comparison phase starts.
        Here, two subsequent channel readouts need to be within the
        boundary set by :attr:`max_deviation`.

        However, no more than :attr:`max_attempts` channel readouts are done.


    Examples
    --------
    The :class:`AverageChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.n_averages = 0
        self.low_limit = 0.0
        self.max_attempts = 0
        self.max_deviation = 0.0
        self._attributes.extend(
            ["n_averages", "low_limit", "max_attempts", "max_deviation"]
        )


class IntervalChannelMetadata(ChannelMetadata):
    """
    Metadata for channels with numeric 0D data measured in a time interval.

    This class complements the class
    :class:`evefile.entities.data.IntervalChannelData`.


    Attributes
    ----------
    trigger_interval : :class:`float`
        The interval/rate measurements are taken in seconds


    Examples
    --------
    The :class:`IntervalChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.trigger_interval = 0.0
        self._attributes.append("trigger_interval")


class NormalizedChannelMetadata:
    """
    Mixin class (interface) for metadata of normalized channel data.

    Attributes
    ----------
    normalize_id : :class:`str`
        Unique ID of the channel used to normalize the data


    Examples
    --------
    The :class:`NormalizedChannelMetadata` class is not meant to be used
    directly, as any entities, but rather indirectly by means of the
    respective facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self.normalize_id = ""


class SinglePointNormalizedChannelMetadata(
    ChannelMetadata, NormalizedChannelMetadata
):
    """
    Metadata for channels with normalized numeric 0D data.

    This class complements the class
    :class:`evefile.entities.data.SinglePointNormalizedChannelData`.


    Examples
    --------
    The :class:`SinglePointNormalizedChannelMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self._attributes.extend(["normalize_id"])


class AverageNormalizedChannelMetadata(
    ChannelMetadata, NormalizedChannelMetadata
):
    """
    Metadata for channels with normalized averaged numeric 0D data.

    This class complements the class
    :class:`evefile.entities.data.AverageNormalizedChannelData`.


    Examples
    --------
    The :class:`AverageNormalizedChannelMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self._attributes.extend(["normalize_id"])


class IntervalNormalizedChannelMetadata(
    ChannelMetadata, NormalizedChannelMetadata
):
    """
    Metadata for channels with normalized interval-measured numeric 0D data.

    This class complements the class
    :class:`evefile.entities.data.IntervalNormalizedChannelData`.


    Examples
    --------
    The :class:`IntervalNormalizedChannelMetadata` class is not meant
    to be used directly, as any entities, but rather indirectly by means
    of the respective facades in the boundaries technical layer of the
    ``evefile`` package. Hence, for the time being,
    there are no dedicated examples how to use this class. Of course,
    you can instantiate an object as usual.

    """

    def __init__(self):
        super().__init__()
        self._attributes.extend(["normalize_id"])
