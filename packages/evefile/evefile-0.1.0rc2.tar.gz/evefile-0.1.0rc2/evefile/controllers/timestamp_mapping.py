"""
*Mapping time stamps of monitors to position counts.*

.. admonition:: Points to discuss further (without claiming to be complete)

    * Mapping MonitorData to MeasureData

      Monitor data (with time in milliseconds as primary axis) need to be
      mapped to measured data (with position counts as primary axis).
      Mapping position counts to time stamps is trivial (lookup), but *vice
      versa* is not unique and the algorithm generally needs to be decided
      upon. There is an age-long discussion on this topic (`#5295 note 3
      <https://redmine.ahf.ptb.de/issues/5295#note-3>`_). For a current
      discussion see `#7722 <https://redmine.ahf.ptb.de/issues/7722>`_.

      Besides the question of how to best map one to the other (that needs to
      be discussed, decided, clearly documented and communicated,
      and eventually implemented): This mapping should most probably take
      place in the controllers technical layer of the measurement functional
      layer. The individual :class:`MonitorData
      <evefile.entities.data.MonitorData>` class cannot do the
      mapping without having access to the mapping table.


For a detailed discussion/summary of the current state of affairs regarding
the algorithm and its specification, see `#7722
<https://redmine.ahf.ptb.de/issues/7722>`_. In short:

* Monitors corresponding to motor axes should be mapped to the *next* position.
* Monitors corresponding to detector channels should be mapped to the
  *previous* position.
* For monitors corresponding to devices, there is no sensible decision
  possible.

Just to make things slightly more entertaining, up to eveH5 v7, monitor
datasets do *not* provide any hint which type (axis, channel, device) they
belong to. Hence, this decision can not be made sensibly. For safety
reasons, mapping monitors to the previous position seems sensible, as the
event could have occurred in the readout phase of the detectors (the
position is incremented after moving the axes and before triggering the
detector readout and start of nested scan modules).

The :class:`TimestampData <evefile.entities.data.TimestampData>`
class got a method :meth:`get_position()
<evefile.entities.data.TimestampData.get_position>` to return
position counts for given timestamps. Currently, the idea is to have one
method handling both, scalars and lists/arrays of values, returning the same
data type, respectively.

This means that for a given :obj:`EveFile
<evefile.boundaries.evefile.EveFile>` object, the controller carrying out
the mapping knows to ask the :obj:`TimestampData
<evefile.entities.data.TimestampData>` object via its :meth:`get_position()
<evefile.entities.data.TimestampData.get_position>` method for the position
counts corresponding to a given timestamp.

Special cases that need to be addressed either here or during import of the
data of a monitor:

* Multiple values with timestamp ``-1``, *i.e.* *before* the scan has been
  started.

  Probably the best solution here would be to skip all values except of the
  last (newest) with the special timestamp ``-1``. See `#7688, note 10
  <https://redmine.ahf.ptb.de/issues/7688#note-10>`_ for details.

  For future developments of the measurement engine, it may be sensible to
  record timestamps for the monitor data in actual timestamps rather than
  milliseconds after the start of the scan (and in turn include actual
  timestamps in the PosCountTimer dataset as well). As monitor data will be
  recorded starting with a scan loaded into the engine, this would allow
  for using these data for actual telemetry of the conditions of the
  setup/beamline/machine.

* Multiple (identical) values with identical timestamp

  Not clear whether this situation can actually occur, but if so,
  most probably in this case only one value should be contained in the data.
  See `#7688, note 11 <https://redmine.ahf.ptb.de/issues/7688#note-11>`_ for
  details.

* Ignoring snapshot position counts

  It does not make sense to map monitor data to position counts of
  snapshots, as those position counts should *not* show up in any data
  array.

Furthermore, a requirement is that the original monitor data are retained
when converting timestamps to position counts. This most probably means to
create a new :obj:`MeasureData <evefile.entities.data.MeasureData>` object.
This is the case for the additional :obj:`DeviceData
<evefile.entities.data.DeviceData>` class as subclass of :obj:`MeasureData
<evefile.entities.data.MeasureData>`. The next question: Where to place
these new objects in the :class:`EveFile <evefile.boundaries.evefile.EveFile>`
(facade) class?


Module documentation
====================

"""
