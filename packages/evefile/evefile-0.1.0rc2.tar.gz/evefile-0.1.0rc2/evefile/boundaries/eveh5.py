"""

*Low-level Python object representation of eveH5 file contents.*

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

This module provides a Python representation (in form of a hierarchy of
objects) of the HDF5 contents of an eveH5 file that can be mapped to
the :class:`EveFile <evefile.boundaries.evefile.EveFile>` interface. Being a
low-level object representation, technically speaking this module is a
resource. The corresponding facade (user-facing interface) would be the
:mod:`evefile <evefile.boundaries.evefile>` module.

While the Python h5py package already provides the low-level access and gets
used, the eveH5 module contains Python objects that are independent of an
open HDF5 file, represent the hierarchy of HDF5 items (groups and datasets),
and contain the attributes of each HDF5 item in form of a Python dictionary.
Furthermore, each object contains a reference to both, the original HDF5
file and the HDF5 item, thus making reading dataset data (and attributes) on
demand as simple as possible.

Another reason for having a separate module rather than directly using the
h5py package in different modules: modularity. If the IO framework (h5py for
the time being) is to be replaced at some point, there will be only this one
place.


Overview
========

A first overview of the classes implemented in this module and their
hierarchy is given in the UML diagram below.


.. figure:: /uml/evefile.boundaries.eveh5.*
    :align: center

    Class hierarchy of the :mod:`evefile.boundaries.eveh5` module.
    The :class:`HDF5Item` class and children represent the individual HDF5
    items on a Python level, similarly to the classes provided in the h5py
    package, but *without* requiring an open HDF5 file. Furthermore, reading
    actual data (dataset values) is deferred by default.


As such, the :class:`HDF5Item` class hierarchy shown above is pretty generic
and should work with all eveH5 versions. However, it is *not* meant as a
generic HDF5 interface, as it does make some assumptions based on the
eveH5 file structure and format.


Key aspects
===========

Despite being a low-level interface to eveH5 HDF5 files, the eveh5 module
provides a series of abstractions and special behaviour summarised below:

* Each :obj:`HDF5Item` object is independent, carrying the entire
  information necessary to obtain both, attributes and data.
* Data (and attributes) are only loaded on demand, speeding up reading a
  file and saving resources.
* :obj:`HDF5Group` objects are iterable: you can iterate over the items in
  the group. As :class:`HDF5File` inherits from :class:`HDF5Group`, this is
  true for :obj:`HDF5File` objects as well.
* To speed up reading an HDF5 file, the file is once opened and will be
  closed only after reading the entire hierarchy of HDF5 items. Similarly,
  when using the :class:`HDF5File` in other code, closing the HDF file in
  between can be prevented. In this case, call the :meth:`HDF5File.close`
  method manually once you're done.


Usage
=====

The typical entry point is an HDF5 file (an eveH5 file, to be precise)
that should be represented as hierarchy of Python objects and the
information contained potentially mapped to another hierarchy of classes.
On the Python level, this is implemented by the :class:`HDF5File` class.

Reading an HDF5 (eveH5) file is as simple as:

.. code-block::

    from evefile.boundaries import eveh5

    file = eveh5.HDF5File(filename_="test.h5")
    file.read()

Each HDF5 item present in the root group (``/``) will appear as attribute by
its name in the :obj:`HDF5File` object. Each such item is of type
:class:`HDF5Item`, more precisely either a :class:`HDF5Dataset` or a
:class:`HDF5Group`.

If a given HDF5 item is itself a group, *i.e.* a node
in the tree and hence an :obj:`HDF5Group`, containing other HDF5 items,
these will be accessible as chained attributes. Suppose your HDF5 file
would contain a dataset ``/c1/meta/PosCountTimer``. You could access this
dataset by:

.. code-block::

    file.c1.meta.PosCountTimer

The dataset itself is an :obj:`HDF5Dataset` object. Datasets are the leafs
of the tree, *i.e.* they cannot contain other items. But they can (and
usually do) contain data.

Furthermore, you can iterate over the items as with every Python iterable:

.. code-block::

    for item in file:
        print(item.name)

This would reveal the name of each item present in the root group, be it a
group or a dataset. Of course, iterating works with every :obj:`HDF5Group`
object, not only the :obj:`HDF5File` object. Getting the names of all
items of the ``c1`` group translates to:

.. code-block::

    for item in file.c1:
        print(item.name)

In both cases, the item names contain the full path within the HDF5 file,
with hierarchy levels separated by ``/``. If you are only interested in the
plain names without path or any leading slashes, use the dedicated method:

.. code-block::

    item_names = file.item_names()

This returns a list of the item names without path or any slahes.

Note that upon reading the file, neither attributes nor dataset values are
loaded from the HDF5 file. Reading attributes, here for the root group of
the file -- but identical for each HDF5 item --, is as simple as:

.. code-block::

    file.get_attributes()

Afterwards, the attributes are available as :attr:`HDF5Item.attributes`
attribute, *i.e.* a Python :class:`dict` with the keys corresponding to
the HDF5 attribute names and the values transformed into scalar strings.

In a similar fashion, if you want to access the data of a dataset,
you need to once ask for the data to be loaded from the HDF5 file. For the
``/c1/meta/PosCountTimer`` dataset mentioned above, this would translate to:

.. code-block::

    file.c1.meta.PosCountTimer.get_data()

Afterwards, you can access the data as :class:`numpy.ndarray` via the
:attr:`HDF5Dataset.data` attribute.


Classes
=======

The following classes are implemented in the module:

* :class:`HDF5Item`

  Base class for HDF5 items.

  Provides the filename, name of the item, and attributes, as well as
  mechanisms to load the attributes on demand from the original HDF5 file.

* :class:`HDF5Dataset`

  Representation of an HDF5 dataset.

  Datasets are the leafs of the hierarchical tree. They cannot contain
  other :obj:`HDF5Item` objects, but they contain data. Provides
  mechanisms to load the data on demand from the original HDF5 file.

* :class:`HDF5Group`

  Representation of an HDF5 group containing other HDF5 items.

  Groups are the nodes of the hierarchical tree. They can (and usually
  will) contain other :class:`HDF5Item` objects, but the cannot contain data.

* :class:`HDF5File`

  Representation of an HDF5 file containing other HDF5 items.

  A special :class:`HDF5Group` instance containing all items contained in an
  HDF5 (eveH5) file as hierarchy of :obj:`HDF5Item` objects. Provides
  mechanisms to load the entire contents of an HDF5 file.


Module documentation
====================

"""

import functools
import logging
from contextlib import contextmanager

import h5py
import numpy as np

logger = logging.getLogger(__name__)


class HDF5Item:
    """
    Base class for HDF5 items.

    HDF5 files are hierarchically structured and contain groups and
    datasets, with a dataset always belonging to a group (and be it the
    root group). Both, groups and datasets can have attributes.

    This class provides the basic structure for both types of HDF5 items
    and is subclassed accordingly.


    Attributes
    ----------
    filename : :class:`str`
        Name of the HDF5 file the item is read from

    name : :class:`str`
        Name of the node/item within the HDF5 file

        Note that this is the full name, including its "path" through the
        hierarchy of the HDF5 file.

    attributes : :class:`dict`
        Attributes of the HDF5 item

        Attributes are *not* loaded by default, but need to be set calling
        :meth:`get_attributes` once.

        The attribute values are converted to (unicode) strings.


    Parameters
    ----------
    filename : :class:`str`
        Name of the HDF5 file the item is read from

    name : :class:`str`
        Name of the node/item within the HDF5 file


    Raises
    ------
    ValueError
        Raised if either filename or name are not provided and attributes
        are accessed.


    Examples
    --------
    Usually, you will not directly instantiate or access an :obj:`HDF5Item`
    object, but one of its subclasses. Nevertheless, it is perfectly
    possible:

    .. code-block::

        item = HDF5Item()

    Both, filename and name can be set upon instantiation:

    .. code-block::

        item = HDF5Item(filename="test.h5", name="/")

    Here ``/`` refers to the HDF5 root group that is always present.

    To set the attributes, *i.e.* read them from the HDF5 file, use the
    :meth:`get_attributes` method:

    .. code-block::

        item = HDF5Item(filename="test.h5", name="/")
        item.get_attributes()

    Note that this will raise if either filename or name are not provided.

    The idea behind obtaining the attributes: being independent of the
    HDF5 file. By directly using the h5py package, the file would always
    need to be open to access the attributes.

    """

    def __init__(self, filename="", name=""):
        self.filename = filename
        self.name = name
        self.attributes = {}
        self._hdf5_filehandle = None

    def get_attributes(self):
        """
        Get attributes from HDF5 item.

        The :attr:`attributes` attribute is set accordingly, and the
        attribute values are converted into (unicode) strings. Note that
        this should be valid for all eveH5 datasets and groups, but not
        generally for HDF5 items.

        .. note::

            As in reality, sometimes other character sets than UTF-8 or
            ASCII have been used, most probably ISO8859-1, conversion will
            check for a :class:`UnicodeDecodeError` and try ``iso8859`` as
            encoding in this case. Note, however, that technically
            speaking, eveH5 files with such character encoding are *no*
            valid HDF5 files.

        Raises
        ------
        ValueError
            Raised if either filename or name are not provided and attributes
            are accessed.

        """
        if not self.filename:
            raise ValueError("Missing attribute filename")
        if not self.name:
            raise ValueError("Missing attribute name")
        with self._hdf5_file() as file:
            try:
                self.attributes = {
                    key: value[0].decode()
                    for key, value in file[self.name].attrs.items()  # noqa
                }
            except UnicodeDecodeError:
                self.attributes = {
                    key: value[0].decode(encoding="iso8859")
                    for key, value in file[self.name].attrs.items()  # noqa
                }

    @contextmanager
    def _hdf5_file(self):
        """
        Context manager for HDF5 file.

        Opening the HDF5 file for each read operation is a massive
        overhead. Hence, if the private attribute ``_hdf5_filehandle`` is
        set, this will be returned, and only otherwise the HDF5 file
        opened and the file handle set.

        Returns
        -------
        hdf5_filehandle : :class:`h5py.File`
            (Open) file object of an HDF5 file to read from.

        """
        close_file = False
        if not self._hdf5_filehandle:
            self._hdf5_filehandle = h5py.File(self.filename, "r")
            close_file = True
        try:
            yield self._hdf5_filehandle
        finally:
            if close_file:
                self._hdf5_filehandle.close()


class HDF5Dataset(HDF5Item):
    """
    Representation of an HDF5 dataset.

    In HDF5, a dataset is the "leaf" of the tree, *i.e.* it does not have
    any children, only a parent (group). Datasets have both, data and
    attributes. Data can be of arbitrary type, not only numeric, and are
    represented as :class:`numpy.array`.


    Raises
    ------
    ValueError
        Raised if either filename or name are not provided and data are
        obtained from HDF5 file.


    Examples
    --------
    HDF5 datasets are HDF5 items with data. Hence, instantiating the class
    is identical to instantiating an :obj:`HDFItem` object:

    .. code-block::

        dataset = HDF5Dataset()

    Both, filename and name can be set upon instantiation:

    .. code-block::

        dataset = HDF5Dataset(filename="test.h5", name="/test")

    Here ``/test`` refers to a hypothetical HDF5 dataset ``test`` present
    in the root group ``/`` of the HDF5 file.

    To set the attributes, *i.e.* read them from the HDF5 file, use the
    :meth:`get_attributes` method:

    .. code-block::

        dataset = HDF5Dataset(filename="test.h5", name="/test")
        dataset.get_attributes()

    Note that this will raise if either filename or name are not provided.

    To set the data, *i.e.* read the data of the dataset from the HDF5
    file, use the :meth:`get_data` method:

    .. code-block::

        dataset = HDF5Dataset(filename="test.h5", name="/test")
        dataset.get_data()

    Several subsequent calls to the :meth:`get_data` method will *not* read
    the data from the HDF5 file more than once for efficiency purposes.

    The idea behind obtaining the attributes and data this way: being
    independent of the HDF5 file. By directly using the h5py package,
    the file would always need to be open to access the attributes.

    """

    def __init__(self, filename="", name=""):
        super().__init__(filename=filename, name=name)
        self._data = np.ndarray([0])
        self._dtype = None
        self._shape = None

    @property
    def data(self):
        """
        Data of the HDF5 dataset.

        Can be numeric, but generally of any type numpy supports.

        .. note::

            Data are only loaded on demand, *i.e.* first access,
            for performance reasons. However, accessing the :attr:`data`
            property automatically triggers a load as long as no data have
            been set before.

        Returns
        -------
        data : :class:`numpy.ndarray`
            Data of the HDF5 dataset

        """
        self.get_data()
        return self._data

    @data.setter
    def data(self, data=None):
        self._data = data

    @property
    def dtype(self):
        """
        Data type (NumPy dtype) of the dataset.

        The dtype of a given dataset can be read without reading the data,
        should hence be a cheap operation. Knowing the dtype, however,
        is sometimes important to know how to further process the given
        HDF5 dataset.

        Returns
        -------
        dtype : :class:`numpy.dtype`
            NumPy dtype object of the dataset

        """
        if not self._dtype:
            if not self.filename:
                raise ValueError("Missing attribute filename")
            if not self.name:
                raise ValueError("Missing attribute name")
            with self._hdf5_file() as file:
                self._dtype = file[self.name].dtype
        return self._dtype

    @property
    def shape(self):
        """
        Shape of the dataset.

        The shape of a given dataset can be read without reading the data,
        should hence be a cheap operation. Knowing the shape, however,
        is sometimes important to know how to further process the given
        HDF5 dataset.

        Returns
        -------
        shape : :class:`tuple`
            Shape of the dataset

        """
        if not self._shape:
            if not self.filename:
                raise ValueError("Missing attribute filename")
            if not self.name:
                raise ValueError("Missing attribute name")
            with self._hdf5_file() as file:
                self._shape = file[self.name].shape
        return self._shape

    def get_data(self):
        """
        Get data from HDF5 dataset.

        The :attr:`data` attribute is set accordingly. Note that getting
        data means opening the actual HDF5 file. Hence, if the
        :attr:`data` attribute has nonzero length, no data are read from
        the HDF5 file, as it is silently assumed that a read process took
        place beforehand. This may be relevant particularly for larger
        datasets.

        Raises
        ------
        ValueError
            Raised if either filename or name are not provided and attributes
            are accessed.

        """
        if self._data.size > 0:
            return
        if not self.filename:
            raise ValueError("Missing attribute filename")
        if not self.name:
            raise ValueError("Missing attribute name")
        with self._hdf5_file() as file:
            self._data = file[self.name][...]


class HDF5Group(HDF5Item):
    # noinspection PyUnresolvedReferences
    """
    Representation of an HDF5 group containing other HDF5 items.

    HDF5 is a hierarchical data format (hence the name), *i.e.* a tree
    consisting of groups as nodes and datasets as leafs. Datasets are
    represented by the :class:`HDF5Dataset` class, groups by this class.
    Groups can contain other groups as well as datasets, and groups can
    have attributes, as any other HDF5 item. An HDF5 file is basically a
    group, and at the same time the root node. For representing entire HDF5
    files, there is a special class :class:`HDF5File` providing
    convenience methods to read files and convert them into a hierarchy of
    :obj:`HDF5Item` objects.

    The class is implemented as iterable, *i.e.* you can iterate over all
    items (:obj:`HDF5Item` objects) as you would with every other Python
    iterable. See the examples section for further details.


    Attributes
    ----------
    item : :class:`HDF5Item`
        Item of a group

        All items added to a collection using the method :meth:`add_item`
        will appear as attribute of the object. As this is dynamic,
        however, no concrete attributes can be described here.


    Examples
    --------
    HDF5 groups are HDF5 items acting as nodes, *i.e.* items that can
    contain other items. Hence, instantiating the class is identical to
    instantiating an :obj:`HDFItem` object:

    .. code-block::

        group = HDF5Group()

    Both, filename and name can be set upon instantiation:

    .. code-block::

        group = HDF5Group(filename="test.h5", name="/test")

    Here ``/test`` refers to a hypothetical HDF5 group ``test`` present
    in the root group ``/`` of the HDF5 file.

    To set the attributes, *i.e.* read them from the HDF5 file, use the
    :meth:`get_attributes` method:

    .. code-block::

        group = HDF5Group(filename="test.h5", name="/test")
        group.get_attributes()

    Note that this will raise if either filename or name are not provided.

    To add an item to the group, you first need to have an item, and only
    afterwards you can add it to the group:

    .. code-block::

        dataset = HDF5Dataset(filename="test.h5", name="/test/foo")

        group = HDF5Group(filename="test.h5", name="/test")
        group.add_item(dataset)

    Items of a group are set as attributes in the object, with their name
    corresponding to the last part of the item name (after the last slash).
    Hence, you can access these attributes as any other attribute:

    .. code-block::

        dataset = HDF5Dataset(filename="test.h5", name="/test/foo")
        group = HDF5Group(filename="test.h5", name="/test")
        group.add_item(dataset)

        item = group.test

    Here, ``item`` would contain the dataset added before to the group.

    Furthermore, groups are iterable, allowing for a very pythonic way of
    accessing the items of a group:

    .. code-block::

        dataset = HDF5Dataset(filename="test.h5", name="/test/foo")
        subgroup = HDF5Group(filename="test.h5", name="/test/bar")
        group = HDF5Group(filename="test.h5", name="/test")
        group.add_item(dataset)
        group.add_item(subgroup)

        for item in group:
            print(item.name)

    This would return the names (here: ``/test/foo`` and ``/test/bar``) of
    the items of the group.

    Similarly, you can use list comprehensions to act upon all items of a
    group. Getting a list of the names, rather than printing them, would be:

    .. code-block::

        [item for item in group]

    Note, however, that in both cases, you get the names with the full path
    within the HDF5 file. If you were interested in just the names, there is
    a convenience method for you:

    .. code-block::

        group.item_names()

    In the same scenario as above, this would return a list with the names
    ``foo`` and ``bar``, without path and leading slash.

    """

    def __init__(self, filename="", name=""):
        super().__init__(filename=filename, name=name)
        self._items = {}

    def __iter__(self):
        """
        Iterate over the items of the group.

        Returns
        -------
        item : :class:`HDF5Item`
            Item of the group

        """
        yield from self._items.values()

    def add_item(self, item):
        """
        Add an item to the group.

        Parameters
        ----------
        item : :class:`HDF5Item`
            The item to be added to the group.

            The item will be accessible as attribute of the group, using
            the last part of the name of the item in :attr:`HDF5Item.name`
            as name for the attribute.

        """
        name = item.name.split("/")[-1]
        setattr(self, name, item)
        self._items[name] = item

    def item_names(self):
        """
        Names of the items in the group.

        Of course, you could simply iterate over the object and access the
        ``name`` attribute of each item in a list comprehension and get the
        same. However, due to the internal implementation of the iterator,
        this convenience method should be much faster, besides being
        convenient. Furthermore, the ``name`` attribute always contains the
        entire path within the HDF5 file, while the names returned here are
        just the names, without path and leading ``/``.

        Returns
        -------
        item_names : :class:`list`
            Names of the items in the group

        """
        return list(self._items.keys())


class HDF5File(HDF5Group):
    """
    Representation of an HDF5 file containing other HDF5 items.

    Technically speaking, an HDF5 file is nothing else than a
    :obj:`HDF5Group` object of the root group (``/``). However, the class
    provides convenience methods for reading an HDF5 file and converting it
    into a hierarchical structure of :obj:`HDF5Item` objects.

    Attributes
    ----------
    read_attributes : :class:`bool`
        Whether to automatically read the attributes.

        Sometimes, it is convenient to automatically load the attributes
        of each HDF5 item when importing an HDF5 file.

        Default: False

    close_file : :class:`bool`
        Whether to close the HDF5 file after read.

        For performance reasons, particularly in context of the
        :class:`EveFile <evefile.boundaries.evefile.EveFile>`
        class, it may be sensible to leave the HDF5 file open and close it
        only afterwards.

        In such case, you are responsible for closing the file yourself.
        Use the :meth:`close` method for convenience.

    Raises
    ------
    ValueError
        Raised if filename is not provided and data are obtained from HDF5
        file.


    Examples
    --------
    HDF5 files are basically HDF5 groups serving as root group and
    containing typically a hierarchy of other HDF5 items (both, groups and
    datasets). The same holds true for the :class:`HDF5File` class serving
    as root group and containing each and every HDF5 item contained in the
    file read.

    To read an HDF5 file and create a hierarchy of :obj:`HDF5Item` objects
    corresponding to the HDF5 items in the file, instantiate the object and
    call its :meth:`read` method:

    .. code-block::

        file = HDF5File()
        file.read("test.h5")

    This will read the file ``test.h5`` and create the corresponding
    hierarchy of :obj:`HDF5Group` and :obj:`HDF5Dataset` items. Note that
    neither attributes nor data (in case of datasets) are read. This can
    (and needs to) be done manually afterwards for each :obj:`HDF5Item`
    object.

    Instead of providing the HDF5 file name as a parameter to the
    :meth:`read` method, you can set it beforehand in the :obj:`HDF5File`
    object, as usual even during instantiation of the object:

    .. code-block::

        file = HDF5File(filename="test.h5")
        file.read()

    Note that the :attr:`name` attribute of the :obj:`HDF5File` object will
    automatically be set to ``/`` to reflect the root node.

    If you would like to read the attributes for each HDF5 item along with
    the item itself, tell the :obj:`HDF5File` object to do so:

    .. code-block::

        file = HDF5File(filename="test.h5")
        file.read_attributes = True
        file.read()

    This will not only add the items to the :obj:`HDF5File` object, but at
    the same time read and add their attributes.

    """

    def __init__(self):
        super().__init__()
        self.name = "/"
        self.read_attributes = False
        self.close_file = True
        self._hdf5_items = {}

    def read(self, filename=""):
        """
        Read contents of an HDF5 (eveH5) file and create hierarchy of items.

        The hierarchical structure of the HDF5 file is represented as
        hierarchy of :obj:`HDF5Item` objects, namely :obj:`HDF5Group` for
        groups (nodes) and :obj:`HDF5Dataset` for datasets (leafs).

        .. note::

            Only the corresponding items will be created, but neither their
            attributes nor data read.

        Parameters
        ----------
        filename : :class:`str`
            Name of the HDF5 (eveH5) file to read.

            If not provided, but set as attribute :attr:`filename`,
            the latter will be used. Takes precedence of the attribute
            :attr:`filename`.

        Raises
        ------
        ValueError
            Raised if filename is not provided and data are obtained from
            HDF5 file.

        """
        if filename:
            self.filename = filename
        if not self.filename:
            raise ValueError("Missing attribute filename")

        self._hdf5_filehandle = h5py.File(self.filename, "r")

        if self.read_attributes:
            self.get_attributes()

        self._get_hdf5_items()
        self._set_hdf5_items()

        if self._hdf5_file() and self.close_file:
            self._hdf5_filehandle.close()

    def _get_hdf5_items(self):
        """
        Get a list of all items of the HDF5 file including their type.

        The item type is set to the corresponding class of this module,
        for easier instantiating of the objects later on.

        For getting the names and types of each item, the visitor pattern
        provided by the h5py package is used. This should be much faster
        than any iteration on the Python side, as this mainly works on the
        HDF5 (*i.e.*, C++) side.
        """

        def inspect(name, item):
            if isinstance(item, h5py.Group):
                item_type = HDF5Group
            else:
                item_type = HDF5Dataset
            self._hdf5_items[name] = item_type

        with self._hdf5_file() as file:
            file.visititems(inspect)

    def _set_hdf5_items(self):
        """
        Create the hierarchy of HDF5 items.

        This method assumes the list of items to be sorted in a way that it
        is safe to sequentially iterate through and create the appropriate
        items. This assumption should be justified given the way how the
        visitor pattern is implemented in h5py.

        """
        for name, node_type in self._hdf5_items.items():
            item = node_type(filename=self.filename, name=f"/{name}")
            item._hdf5_filehandle = self._hdf5_filehandle  # noqa
            if self.read_attributes:
                item.get_attributes()
            if "/" not in name:
                self.add_item(item)
            else:
                parent = "/".join(name.split("/")[:-1])
                node = functools.reduce(getattr, parent.split("/"), self)
                node.add_item(item)

    def close(self):
        """
        Close open HDF5 file.

        For performance reasons, particularly in context of the
        :class:`EveFile <evefile.boundaries.evefile.EveFile>`
        class, it may be sensible to leave the HDF5 file open and close it
        only afterwards.

        In such case, you are responsible for closing the file yourself.
        Use this method for convenience.

        """
        if self._hdf5_filehandle:
            self._hdf5_filehandle.close()


if __name__ == "__main__":
    import timeit

    NUMBER = 10
    h5 = HDF5File()
    h5.read_attributes = True
    h5.close_file = False
    FILENAME = "/messung/euvr/daten/2024/KW32_24/TOPPAN/00092.h5"
    time = timeit.timeit(
        "h5.read(FILENAME); h5.close()", number=NUMBER, globals=globals()
    )
    print(time / NUMBER)

    import cProfile

    cProfile.run("h5.read(FILENAME); h5.close()")
