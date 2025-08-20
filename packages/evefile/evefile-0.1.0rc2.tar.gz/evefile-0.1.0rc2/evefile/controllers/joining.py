"""
.. _evedata: https://evedata.docs.radiometry.de/

*Ensure data and axes values are commensurate and compatible.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 2

For each motor axis and detector channel, in the original eveH5 file only
those values appear---together with a "position" (PosCount) value---that
have actually been set or measured. Hence, the number of values (*i.e.*,
the length of the data vector) will generally be different for different
devices. To be able to plot arbitrary data against each other,
the corresponding data vectors need to be commensurate. If this is not the
case, they need to be brought to the same dimensions (*i.e.*, "joined",
originally somewhat misleadingly termed "filled").

To be exact, being commensurate is only a necessary, but not a sufficient
criterion, as not only the shape needs to be commensurate, but the indices
(in this case the positions) be identical.

Furthermore, joining is a *modification* of the original data. Without
retaining the original data as recorded in the eveH5 file, you will lose
the information which data points were actually recorded (or axes
positions set). This is a key difference in handling joining in the
``evefile`` and `evedata`_ packages, as detailed below.


Different scenarios for data joining
====================================

There are basically two different scenarios, and currently, `evedata`_
implements only the first, while ``evefile`` will most probably need to
implement the second:

#. Plotting data

   In this case, there is always one data vector, but several possible
   axes vectors. Hence, we need only to deal with a 1..n relationship of data
   to axes.

   However, in this case, "axes" and "data" have different meanings as
   compared to motor axes and detector channels usually discussed. *I.e.*,
   axes and data can be both, motor axes and detector channels, respectively.

   Furthermore, the result of joining depends on the actually chosen set
   of "axes" and "data" and may change as soon as the user selects
   different datasets to be plotted. Hence, the original data need to be
   retained somewhere.

#. Creating the "all-knowing table"

   An arbitrary set of channels and axes (and monitors) should be joined
   in one single table for an easy overview and simple access. Besides the
   known problems of this approach (the data model underlying the
   measurements simply does not allow to be represented as a 2D table),
   it is and remains a known and important use case.

These two different scenarios may eventually result in having two
``joining`` modules in `evedata`_, one in the ``measurement`` functional
layer, and one in the ``evefile`` functional layer, identical with the one
developed here in ``evefile``.


Dealing with axes, channels, and monitors
=========================================

If you think of joining different data objects, there is one trivial case
where you only retain those values where indices exist for all the data
objects to be joined. However, as soon as you think of retaining all
indices of at least one of the data objects, you need to decide how to
deal with the other data objects and the missing values in there.

Here, it is important to distinguish between the three concepts used in
the EVE measurement program: axes, channels, and monitors. A bit of
terminology may be helpful before going into details:

axis
    A device whose values are set explicitly by the measurement program.

    The prototypical "axis" is a motor axis, but from the perspective of
    the measurement program, everything that is set explicitly during the
    measurement is represented as an axis.

channel
    A device whose values are read explicitly by the measurement program.

    The prototypical "channel" is a detector channel, but from the
    perspective of the measurement program, everything that is read
    explicitly (at defined times during the scan) by the measurement
    program qualifies as channel.

monitor
    A device whose values are monitored for changes that are recorded.

    The monitor concept originates from the underlying EPICS layer and
    provides telemetry data for everything that can potentially change its
    value, but where you are only interested in the changes.


Now for the joining of data where you need to "fill" values for datasets
that belong to one of the three classes detailed above.


Axes are assumed to retain their value
--------------------------------------

An axis is by definition (see above) a device *actively* controlled by the
measurement program. Hence, if there is no active change in the setting,
the axis is assumed to have the exact same value as set last time.
Therefore, axis values are "filled" with the last known value.

This last known value can either be the value set within a scan
explicitly, or, if present, the value from a snapshot containing this axis.


Channels cannot be interpolated at all
--------------------------------------

A channel is by definition a device whose values are read at defined times
during a scan. Hence, if you haven't recorded a value for a given position
("PosCount"), there is no way to infer this value. Therefore, if you need
to "fill" those positions, a "missing value" (``NaN`` or similar,
see ":ref:`sec-missing_values`" below for further details) is set for
these positions.


Monitors have not changed by definition
---------------------------------------

A monitor is by definition a device you are observing for changes in its
values. Hence, if no chance has been recorded (*i.e.*, no newer value is
present), the value hasn't changed. Therefore, monitor data can be
"filled" with the last known value, and in contrast to axes, we can be
certain that this is true. (For an axis, you could always argue that if
there is no read-back mechanism implemented, somebody could change its
value from outside the measurement program or actual scan).


.. note::

    So far, we have only discussed how to deal with positions in a joined
    "array" where values for axes, channels, or monitors are missing. This
    is entirely separate from the question of how to define the common
    denominator, *i.e.* the list of positions (PosCounts) values for the
    different devices should be available for. This is discussed in more
    details below.



Join modes: A bit of history
============================

Historically, there were four "fill modes" available for data: NoFill,
LastFill, NaNFill, LastNaNFill. From the `documentation of eveFile
<https://www.ahf.ptb.de/messpl/sw/python/common/eveFile/doc/html/Section
-Fillmode.html#evefile.Fillmode>`_:


NoFill
    "Use only data from positions where at least one axis and one channel
    have values."

    Actually, not a filling, but mathematically an intersection, or,
    in terms of relational databases, an ``SQL INNER JOIN``. In any case,
    data are *reduced*.

LastFill
    "Use all channel data and fill in the last known position for all axes
    without values."

    Similar to an ``SQL LEFT JOIN`` with data left and axes right,
    but additionally explicitly setting the missing axes values in the join
    to the last known axis value (or NaN if no last known axis value exists).

NaNFill
    "Use all axis data and fill in NaN for all channels without values."

    Similar to an ``SQL LEFT JOIN`` with axes left and data right. To be
    exact, the ``NULL`` values of the join operation will be replaced by
    ``NaN``.

LastNaNFill
    "Use all data and fill in NaN for all channels without values and fill
    in the last known position for all axes without values."

    Similar to an ``SQL OUTER JOIN``, but additionally explicitly setting
    the missing axes values in the join to the last known axis value (or
    NaN if no last known axis value exists) and replacing the ``NULL``
    values of the join operation by ``NaN``.


Besides using analogies from the SQL world, relational algebra is another
way of making the different join modi explicit. From the documentation of
``EveFile`` implemented in IDL by Marcus Michalsky:

    Depending on the given fill option certain data will not be present in
    the result. Let ``A`` be the set union of positions of all given axes
    and ``C`` the set union of positions of all given channels. Then the
    resulting position list will be as follows:

    .. code-block::

        'NoFill':      A ^ C (Intersection)
        'LastFill':    C
        'NaNFill':     A
        'LastNaNFill': A v C (set union)



Furthermore, for the Last*Fill modes, snapshots are inspected for axes
values that are newer than the last recorded axis in the main/standard
section or for initial axis values if an axis has not been set in the
main/standard section yet.


.. note::

    Note that **none of the fill modes guarantees that there are no NaNs**
    (or comparable null values) in the resulting data.


.. note::

    The concept of ``NaN`` is, strictly speaking, only defined for floats,
    not for other numeric types and not for strings. Hence, the previous
    mentioning of ``NaN`` is not entirely correct. See the section
    ":ref:`sec-missing_values`" below for further details.


.. important::

    The IDL Cruncher seems to use LastNaNFill combined with applying some
    "dirty" fixes to account for scans using MPSKIP and those scans
    "monitoring" a motor position via a pseudo-detector. The ``EveHDF``
    class (DS) uses LastNaNFill as a default as well but does *not* apply
    some additional post-processing.

    Shall fill modes be something to change in a viewer? And which fill
    modes are used in practice (and do we have any chance to find this out)?


.. note::

    Snapshot *positions* are never included in any joined array.
    Of course, snapshot *data* should be used for all fill modes except
    ``NoFill`` and ``NaNFill``. But it does not seem to make much sense to
    incorporate the snapshot *positions* into the joined data array.

    It may be the case with legacy interfaces, though, that including the
    PosCountTimer dataset results in a data array with all available
    position counts. This should be considered a bug, however, rather than
    a feature for most use cases. In context of one big table for all data
    recorded (including axes positions, channel readouts, options set,
    and parameters monitored), it might be the only sensible chance to get
    hand of the information contained in snapshots, however. Nevertheless,
    this would be something ``evefile`` should not be concerned about.


.. _sec-missing_values:

How to deal with missing values?
================================

Depending on the concrete situation, there may be no value available to
fill a gap in an axis. Hence, how to deal with this situation?


Numeric values
--------------

For numeric values, some kind of "NaN" (not a number) could be used.

For NumPy, only floats can have a dedicated "NaN", but no other dtype.
Hence, in case of missing values, a masked array (
:class:`numpy.ma.MaskedArray`) is used and :data:`numpy.ma.masked` set
explicitly for those missing values. For all practical purposes,
this should work similar to the :data:`numpy.nan`. In particular,
when trying to plot a :class:`numpy.ma.MaskedArray`, the masked values are
simply ignored. For further details of how to work with masked arrays,
see the :mod:`numpy.ma` documentation.


Non-numeric values
------------------

First of all: Does this situation occur in reality? Yes, there are axes
with non-numeric values. But are these axes ever joined? If so,
some textual value such as "N/A" (not available) may be used.

.. note::

    The default fill value of a :class:`numpy.ma.MaskedArray` is ``N/A``,
    and this is (only) used when calling :meth:`numpy.ma.MaskedArray.filled`.
    Otherwise, the masked values are in most cases simply ignored. For an
    overview of the default fill values of masked arrays, see the
    :attr:`numpy.ma.MaskedArray.fill_value` attribute.


How to deal with monitor data?
==============================

To the best of the knowledge of this package's author, monitor data have
never been considered for data joining, as they would first need to be
mapped to position counts before joining. However, given that a mapping of
timestamps to position counts exists (see the :mod:`timestamp_mapping
<evefile.controllers.timestamp_mapping>` module), this finally needs to be
considered.

Monitors are somewhat special, as values are recorded for each change,
together with a timestamp. Furthermore, there should *always* be a reference
value recorded at the beginning of the scan (actually as soon as the scan
is loaded into the engine, and if there are further changes in the
monitored value before the scan execution starts, currently multiple
values with the identical timestamp of "-1" are recorded, meaning that the
last of these values should be used, see the discussion in the
:mod:`timestamp_mapping <evefile.controllers.timestamp_mapping>` module
for further details).

If monitor data should appear in a joined data array, it seems most
sensible to inflate the values to all position counts eventually in the
data array, but to not consider the position counts of the (mapped)
monitor datasets for determining which position counts to use for the
joined data array. This would be kind of a "LastFill" (in the terminology
discussed above) for the monitor data using the position counts of the
final joined data array previously determined for all the other datasets
(that in turn depend on the join mode, of course).


A few comments for further development
======================================

.. important::

    The classes implemented in this module have been copied from the
    corresponding module in `evedata`_, and here particularly from the
    "measurement" functional layer. However, the needs in ``evefile`` are
    different, hence even the basic :class:`Join` class needs to be
    redesigned. Further information below. Once this has been done,
    this entire section should be removed.


* Joining should probably take into account all available attributes,
  not only ``data``, but options as well if present. This of course only
  applies to ``evefile`` if options of devices are mapped to the
  respective data objects.

* Joining should probably take into account monitors that need to be
  converted to :class:`DeviceData <evefile.entities.data.DeviceData>` before.


Join modes currently implemented
================================

Currently, the following join modes are implemented:

* :class:`ChannelPositions`

  Return values for all positions where at least one channel was recorded.

  The resulting position list is the set union of positions of all given
  channels. This means that for each position where at least one channel
  was recorded, this position is included in the list.

  This was **previously known as "LastFill" mode** and was described as "Use
  all channel data and fill in the last known position for all axes
  without values." In SQL terms (relational database), this would be
  similar to a left join with channels left and axes right, but additionally
  explicitly setting the missing axes values in the join to the last
  known axis value. If no previous axes value is available, convert the
  data into a :obj:`numpy.ma.MaskedArray` object and mask the value.
  Furthermore, for each channel where no value exists for any of the
  positions from the position list, the data are converted into a
  :obj:`numpy.ma.MaskedArray` object and the value(s) masked.

* :class:`AxisPositions`

  Return values for all positions where at least one axis was set.

  The resulting position list is the set union of positions of all given
  axes. This means that for each position where at least one axis
  was set, this position is included in the list.

  This was **previously known as "NaNFill" mode** and was described as
  "Use all axis data and fill in NaN for all channels without values."
  In SQL terms (relational database), this would be similar to a left
  join with axes left and channels right, but additionally
  explicitly setting the missing axes values in the join to the last
  known axis value. If no previous axes value is available, convert the
  data into a :obj:`numpy.ma.MaskedArray` object and mask the value.
  Furthermore, for each channel where no value exists for any of the
  positions from the position list, the data are converted into a
  :obj:`numpy.ma.MaskedArray` object and the value(s) masked.

* :class:`AxisAndChannelPositions`

  Return values for all positions where axis *and* channel values exist.

  The resulting position list is the set intersection of positions of all
  given channels and axes. This means that for each position where at least
  one axis was set *and* one channel recorded, this position is included in
  the list.

  This was **previously known as "NoFill" mode** and was described as
  "Use only data from positions where at least one axis and one channel
  have values." In SQL terms (relational database), this would be
  similar to an inner join, but additionally explicitly setting the
  missing axes values in the join to the last known axis value. If no
  previous axes value is available, convert the data into a
  :obj:`numpy.ma.MaskedArray` object and mask the value. Furthermore,
  for each channel where no value exists for any of the positions from
  the position list, the data are converted into a
  :obj:`numpy.ma.MaskedArray` object and the value(s) masked.

* :class:`AxisOrChannelPositions`

  Return values for all positions where axis *or* channel values exist.

  The resulting position list is the set union of positions of all
  given channels and axes. This means that for each position where at least
  one axis was set *or* one channel recorded, this position is included in
  the list.

  This was **previously known as "LastNaNFill" mode** and was described as
  "Use all data and fill in NaN for all channels without values and fill
  in the last known position for all axes without values." In SQL terms
  (relational database), this would be similar to an outer join,
  but additionally explicitly setting the missing axes values in the
  join to the last known axis value. If no previous axes value is
  available, convert the data into a :obj:`numpy.ma.MaskedArray` object
  and mask the value. Furthermore, for each channel where no value
  exists for any of the positions from the position list, the data are
  converted into a :obj:`numpy.ma.MaskedArray` object and the value(s)
  masked.


For developers
==============

To implement additional join modes, create a class inheriting from the
:class:`Join` base class and implement the actual joining in the private
method ``_join()``.

There is a factory class :class:`JoinFactory` that you can ask to get a
:class:`Join` object:

.. code-block::

    factory = JoinFactory()
    join = factory.get_join(mode="ChannelPositions")

This would return an :obj:`ChannelPositions` object. For further details,
see the :class:`JoinFactory` documentation.


Module documentation
====================

"""

import copy
import logging
from functools import reduce

import numpy as np

import evefile.entities
import evefile.entities.data

logger = logging.getLogger(__name__)


class Join:
    """
    Base class for joining data.

    For each motor axis and detector channel, in the original eveH5 file only
    those values appear---together with a "position counter" (PosCount)
    value---that have actually been set or measured. Hence, the number of
    values (*i.e.*, the length of the data vector) will generally be different
    for different devices. To be able to plot arbitrary data against each
    other, the corresponding data vectors need to be commensurate. If this
    is not the case, they need to be brought to the same dimensions (*i.e.*,
    "joined", originally somewhat misleadingly termed "filled").

    The main "quantisation" axis of the values for a device and the
    common reference is the list of positions. Hence, to join,
    first of all the lists of positions are compared, and gaps handled
    accordingly.

    As there are different strategies how to deal with gaps in the
    positions list, generally, there are different subclasses of the
    :class:`Join` class dealing each with a particular strategy.


    Attributes
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile object the Join should be performed for.

        Although joining is carried out for a small subset of the
        data of an EveFile object, additional information from the
        EveFile object may be necessary to perform the task.

    Parameters
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile object the join should be performed for.


    Examples
    --------
    Usually, joining takes place in the :meth:`get_joined_data()
    <evefile.boundaries.evefile.EveFile.get_joined_data>`
    method.

    To join data, call :meth:`join` with a list of data objects or data
    object names, respectively:

    .. code-block::

        join = Join(evefile=my_evefile)
        # Call with data object names
        joined_data = join.join(["name1", "name2"])
        # Call with data objects
        joined_data = join.join(
            [my_evefile.data["id1"], my_evefile.data["id2"]]
        )

    """

    def __init__(self, evefile=None):
        self._channel_indices = []
        self._axes = []
        self._channels = []
        self._result_positions = None
        self.evefile = evefile

    def join(self, data=None):
        """
        Harmonise data.

        The main "quantisation" axis of the values for a device and the
        common reference is the list of positions. Hence, to join,
        first of all the lists of positions are compared, and gaps handled
        accordingly.

        As there are different strategies how to deal with gaps in the
        positions list, generally, there will be different subclasses of the
        :class:`Join` class dealing each with a particular strategy.

        Parameters
        ----------
        data : :class:`list`
            (Names of the) data objects to join.

            You can provide a list of either names or IDs of data objects or
            the data objects themselves.

        Returns
        -------
        data : :class:`list`
            Data objects with joined data values.

        Raises
        ------
        ValueError
            Raised if no evefile is present
        ValueError
            Raised if no data are provided

        """
        if not self.evefile:
            raise ValueError("Need an evefile to join data.")
        if not data:
            raise ValueError("Need data to join data.")
        data = [
            (
                self._convert_str_to_data_object(item)
                if isinstance(item, str)
                else item
            )
            for item in data
        ]
        return self._join(data=data)

    def _convert_str_to_data_object(self, name_or_id=""):
        try:
            result = self.evefile.data[name_or_id]
        except KeyError:
            result = self.evefile.get_data(name_or_id)
        return result

    def _join(self, data=None):
        self._sort_data(data)
        self._assign_result_positions()
        self._fill_axes()
        self._fill_channels()
        return self._assign_result()

    def _sort_data(self, data):
        for idx, item in enumerate(data):
            if isinstance(item, evefile.entities.data.ChannelData):
                self._channels.append(copy.copy(item))
                self._channel_indices.append(idx)
            if isinstance(item, evefile.entities.data.AxisData):
                self._axes.append(copy.copy(item))

    def _assign_result_positions(self):
        pass

    def _fill_axes(self):
        for axis in self._axes:
            if axis.metadata.id in self.evefile.snapshots:
                axis.join(
                    positions=self._result_positions,
                    snapshot=self.evefile.snapshots[axis.metadata.id],
                )
            else:
                axis.join(positions=self._result_positions, fill=True)

    def _fill_channels(self):
        for channel in self._channels:
            channel.join(positions=self._result_positions)

    def _assign_result(self):
        result = [*self._axes]
        for idx, item in enumerate(self._channels):
            result.insert(self._channel_indices[idx], item)
        return result


class ChannelPositions(Join):
    """
    Return values for all positions where at least one channel was recorded.

    The resulting position list is the set union of positions of all given
    channels. This means that for each position where at least one channel
    was recorded, this position is included in the list.

    This was **previously known as "LastFill" mode** and was described as
    "Use all channel data and fill in the last known position for all axes
    without values." In SQL terms (relational database), this would be
    similar to a left join with channels left and axes right,
    but additionally explicitly setting the missing axes values in the
    join to the last known axis value. If no previous axes value is
    available, convert the data into a :obj:`numpy.ma.MaskedArray` object
    and mask the value. Furthermore, for each channel where no value
    exists for any of the positions from the position list, the data are
    converted into a :obj:`numpy.ma.MaskedArray` object and the value(s)
    masked.

    In more detail, the following happens to each individual data object,
    separated by type of data:

    Channels:

    * The position list is the set union of positions of all given channels.
    * Positions where no value was recorded for a given channel are set as
      missing ("masked" in NumPy terminology), the resulting data array is of
      type :class:`numpy.ma.MaskedArray`.

    Axes:

    * The position list is the set union of positions of all given channels.
    * For values originally missing for an axis, the last value of the
      previous position is used.
    * If no previous value exists for a missing value, the data are
      converted into a :obj:`numpy.ma.MaskedArray` object and the values
      masked with :data:`numpy.ma.masked`.
    * The snapshots are checked for values corresponding to the axis,
      and if present, are taken into account. If there is more than one
      snapshot, always the newest snapshot previous to the current axis
      position will be used.

    Of course, as in all cases, the (integer) positions are used as common
    reference for the values of all devices.

    Attributes
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile object the join should be performed for.

        Although joining may only be carried out for a small subset of the
        data of an EveFile object, additional information from the
        EveFile object may be necessary to perform the task, *e.g.*,
        the snapshots.

    Parameters
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile the join should be performed for.


    Examples
    --------
    Usually, joining takes place in the :meth:`get_joined_data()
    <evefile.boundaries.evefile.EveFile.get_joined_data>`
    method of the :class:`EveFile <evefile.boundaries.evefile.EveFile>` class.

    To join data, call :meth:`join` with a list of data objects or data
    object names, respectively:

    .. code-block::

        join = ChannelPositions(evefile=my_evefile)
        # Call with data object names
        joined_data = join.join(["name1", "name2"])
        # Call with data objects
        joined_data = join.join(
            [my_evefile.data["id1"], my_evefile.data["id2"]]
        )

    Note that the joined data objects appear in the same order as you
    provided them or their names/IDs to the :meth:`join` method.

    """

    def _assign_result_positions(self):
        channel_positions = [item.position_counts for item in self._channels]
        self._result_positions = reduce(np.union1d, channel_positions).astype(
            np.int64
        )


class AxisPositions(Join):
    """
    Return values for all positions where at least one axis was set.

    The resulting position list is the set union of positions of all given
    axes. This means that for each position where at least one axis
    was set, this position is included in the list.

    This was **previously known as "NaNFill" mode** and was described as
    "Use all axis data and fill in NaN for all channels without values."
    In SQL terms (relational database), this would be similar to a left
    join with axes left and channels right, but additionally
    explicitly setting the missing axes values in the join to the last
    known axis value. If no previous axes value is available, convert the
    data into a :obj:`numpy.ma.MaskedArray` object and mask the value.
    Furthermore, for each channel where no value exists for any of the
    positions from the position list, the data are converted into a
    :obj:`numpy.ma.MaskedArray` object and the value(s) masked.

    In more detail, the following happens to each individual data object,
    separated by type of data:

    Channels:

    * The position list is the set union of positions of all given axes.
    * Positions where no value was recorded for a given channel are set as
      missing ("masked" in NumPy terminology), the resulting data array is of
      type :class:`numpy.ma.MaskedArray`.

    Axes:

    * The position list is the set union of positions of all given axes.
    * For values originally missing for an axis, the last value of the
      previous position is used.
    * If no previous value exists for a missing value, the data are
      converted into a :obj:`numpy.ma.MaskedArray` object and the values
      masked with :data:`numpy.ma.masked`.
    * The snapshots are checked for values corresponding to the axis,
      and if present, are taken into account. If there is more than one
      snapshot, always the newest snapshot previous to the current axis
      position will be used.

    Of course, as in all cases, the (integer) positions are used as common
    reference for the values of all devices.

    Attributes
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile object the join should be performed for.

        Although joining may only be carried out for a small subset of the
        data of an EveFile object, additional information from the
        EveFile object may be necessary to perform the task, *e.g.*,
        the snapshots.

    Parameters
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile the join should be performed for.


    Examples
    --------
    Usually, joining takes place in the :meth:`get_joined_data()
    <evefile.boundaries.evefile.EveFile.get_joined_data>`
    method of the :class:`EveFile <evefile.boundaries.evefile.EveFile>` class.

    To join data, call :meth:`join` with a list of data objects or data
    object names, respectively:

    .. code-block::

        join = AxisPositions(evefile=my_evefile)
        # Call with data object names
        joined_data = join.join(["name1", "name2"])
        # Call with data objects
        joined_data = join.join(
            [my_evefile.data["id1"], my_evefile.data["id2"]]
        )

    Note that the joined data objects appear in the same order as you
    provided them or their names/IDs to the :meth:`join` method.

    """

    def _assign_result_positions(self):
        axis_positions = [item.position_counts for item in self._axes]
        self._result_positions = reduce(np.union1d, axis_positions).astype(
            np.int64
        )


class AxisAndChannelPositions(Join):
    """
    Return values for all positions where axis *and* channel values exist.

    The resulting position list is the set intersection of positions of all
    given channels and axes. This means that for each position where at least
    one axis was set *and* one channel recorded, this position is included in
    the list.

    This was **previously known as "NoFill" mode** and was described as
    "Use only data from positions where at least one axis and one channel
    have values." In SQL terms (relational database), this would be
    similar to an inner join, but additionally explicitly setting the
    missing axes values in the join to the last known axis value. If no
    previous axes value is available, convert the data into a
    :obj:`numpy.ma.MaskedArray` object and mask the value. Furthermore,
    for each channel where no value exists for any of the positions from
    the position list, the data are converted into a
    :obj:`numpy.ma.MaskedArray` object and the value(s) masked.

    In more detail, the following happens to each individual data object,
    separated by type of data:

    Channels:

    * The position list is the set intersection of positions of all given
      axes and channels.
    * Positions where no value was recorded for a given channel are set as
      missing ("masked" in NumPy terminology), the resulting data array is of
      type :class:`numpy.ma.MaskedArray`.

    Axes:

    * The position list is the set intersection of positions of all given
      axes and channels.
    * For values originally missing for an axis, the last value of the
      previous position is used.
    * If no previous value exists for a missing value, the data are
      converted into a :obj:`numpy.ma.MaskedArray` object and the values
      masked with :data:`numpy.ma.masked`.
    * The snapshots are checked for values corresponding to the axis,
      and if present, are taken into account. If there is more than one
      snapshot, always the newest snapshot previous to the current axis
      position will be used.

    Of course, as in all cases, the (integer) positions are used as common
    reference for the values of all devices.

    Attributes
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile object the join should be performed for.

        Although joining may only be carried out for a small subset of the
        data of an EveFile object, additional information from the
        EveFile object may be necessary to perform the task, *e.g.*,
        the snapshots.

    Parameters
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile the join should be performed for.


    Examples
    --------
    Usually, joining takes place in the :meth:`get_joined_data()
    <evefile.boundaries.evefile.EveFile.get_joined_data>`
    method of the :class:`EveFile <evefile.boundaries.evefile.EveFile>` class.

    To join data, call :meth:`join` with a list of data objects or data
    object names, respectively:

    .. code-block::

        join = AxisAndChannelPositions(evefile=my_evefile)
        # Call with data object names
        joined_data = join.join(["name1", "name2"])
        # Call with data objects
        joined_data = join.join(
            [my_evefile.data["id1"], my_evefile.data["id2"]]
        )

    Note that the joined data objects appear in the same order as you
    provided them or their names/IDs to the :meth:`join` method.

    """

    def _assign_result_positions(self):
        positions = [item.position_counts for item in self._axes]
        positions.extend([item.position_counts for item in self._channels])
        self._result_positions = reduce(np.intersect1d, positions).astype(
            np.int64
        )


class AxisOrChannelPositions(Join):
    """
    Return values for all positions where axis *or* channel values exist.

    The resulting position list is the set union of positions of all
    given channels and axes. This means that for each position where at least
    one axis was set *or* one channel recorded, this position is included in
    the list.

    This was **previously known as "LastNaNFill" mode** and was described as
    "Use all data and fill in NaN for all channels without values and fill
    in the last known position for all axes without values." In SQL terms
    (relational database), this would be similar to an outer join,
    but additionally explicitly setting the missing axes values in the
    join to the last known axis value. If no previous axes value is
    available, convert the data into a :obj:`numpy.ma.MaskedArray` object
    and mask the value. Furthermore, for each channel where no value
    exists for any of the positions from the position list, the data are
    converted into a :obj:`numpy.ma.MaskedArray` object and the value(s)
    masked.

    In more detail, the following happens to each individual data object,
    separated by type of data:

    Channels:

    * The position list is the set union of positions of all given axes
      and channels.
    * Positions where no value was recorded for a given channel are set as
      missing ("masked" in NumPy terminology), the resulting data array is of
      type :class:`numpy.ma.MaskedArray`.

    Axes:

    * The position list is the set union of positions of all given axes
      and channels.
    * For values originally missing for an axis, the last value of the
      previous position is used.
    * If no previous value exists for a missing value, the data are
      converted into a :obj:`numpy.ma.MaskedArray` object and the values
      masked with :data:`numpy.ma.masked`.
    * The snapshots are checked for values corresponding to the axis,
      and if present, are taken into account. If there is more than one
      snapshot, always the newest snapshot previous to the current axis
      position will be used.

    Of course, as in all cases, the (integer) positions are used as common
    reference for the values of all devices.

    Attributes
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile object the join should be performed for.

        Although joining may only be carried out for a small subset of the
        data of an EveFile object, additional information from the
        EveFile object may be necessary to perform the task, *e.g.*,
        the snapshots.

    Parameters
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile the join should be performed for.


    Examples
    --------
    Usually, joining takes place in the :meth:`get_joined_data()
    <evefile.boundaries.evefile.EveFile.get_joined_data>`
    method of the :class:`EveFile <evefile.boundaries.evefile.EveFile>` class.

    To join data, call :meth:`join` with a list of data objects or data
    object names, respectively:

    .. code-block::

        join = AxisOrChannelPositions(evefile=my_evefile)
        # Call with data object names
        joined_data = join.join(["name1", "name2"])
        # Call with data objects
        joined_data = join.join(
            [my_evefile.data["id1"], my_evefile.data["id2"]]
        )

    Note that the joined data objects appear in the same order as you
    provided them or their names/IDs to the :meth:`join` method.

    """

    def _assign_result_positions(self):
        positions = [item.position_counts for item in self._axes]
        positions.extend([item.position_counts for item in self._channels])
        self._result_positions = reduce(np.union1d, positions).astype(
            np.int64
        )


class JoinFactory:
    """
    Factory for getting the correct join object.

    For background on the need for joining, see the documentation of the
    entire :mod:`joining <evefile.controllers.joining>` module, and
    of the :class:`Join <evefile.controllers.joining.Join>` class.

    Given a decision which type of join you would like to apply to
    your data, this factory class allows you to get the correct
    join instance without hassle. And you can even change your mind
    in between and don't have to change any code---the whole idea behind
    factories.

    Attributes
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile the join should be performed for.


    Parameters
    ----------
    evefile : :class:`evefile.boundaries.evefile.EveFile`
        EveFile the join should be performed for.


    Examples
    --------
    Getting a join object is as simple as calling a single method
    on the factory object:

    .. code-block::

        factory = JoinFactory()
        join = factory.get_join(mode="ChannelPositions")

    This will provide you with the appropriate :obj:`ChannelPositions`
    instance.

    As joins need a :class:`EveFile
    <evefile.boundaries.evefile.EveFile>` object,
    you can set one to the factory, and it will get added automatically to
    the join instance for you:

    .. code-block::

        factory = JoinFactory(evefile=my_evefile)
        join = factory.get_join(mode="ChannelPositions")

    Thus, when used from within a :class:`EveFile
    <evefile.boundaries.evefile.EveFile>` object,
    set the :attr:`evefile` attribute to ``self``.

    """

    def __init__(self, evefile=None):
        self.evefile = evefile

    def get_join(self, mode="Join"):
        """
        Obtain a :class:`Join` instance for a particular mode.

        If no mode is provided, this defaults to the base class. As the
        :class:`Join` does not implement any functionality, this is
        rather useless.

        If the :attr:`evefile` attribute is set, it is automatically set
        in the :obj:`Join` instance returned.

        Parameters
        ----------
        mode : :class:`str`
            Join mode to return a :class:`Join` instance for.

            Default: "Join"

        Returns
        -------
        join : :class:`Join`
            Join instance

        """
        instance = globals()[mode](evefile=self.evefile)
        return instance
