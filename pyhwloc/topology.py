# Copyright (c) 2025, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
The Topology Interface
======================
"""
from __future__ import annotations

import ctypes
import logging
import os
import weakref
from types import TracebackType
from typing import Callable, Iterator, Type, TypeAlias

from .hwloc import core as _core
from .hwloc import lib as _lib
from .hwobject import Object, ObjType

__all__ = [
    "Topology",
    "ExportXmlFlags",
    "ExportSyntheticFlags",
    "TypeFilter",
]


def _from_xml_buffer(xml_buffer: str, load: bool) -> _core.topology_t:
    hdl = _core.topology_t(0)
    try:
        _core.topology_init(hdl)
        _core.topology_set_xmlbuffer(hdl, xml_buffer)
        if load is True:
            _core.topology_load(hdl)
    except (_lib.HwLocError, NotImplementedError) as e:
        if hdl:
            _core.topology_destroy(hdl)
        raise e

    return hdl


ObjPtr = _core.ObjPtr
ExportXmlFlags: TypeAlias = _core.hwloc_topology_export_xml_flags_e
ExportSyntheticFlags: TypeAlias = _core.hwloc_topology_export_synthetic_flags_e
TypeFilter: TypeAlias = _core.hwloc_type_filter_e


class Topology:
    """High-level interface for the hwloc topology.

    This class provides a context manager interface for working with hardware
    topology information. It automatically handles topology initialization,
    loading, and cleanup.

    The default `Topology` constructor initializes a topology object based on the
    current system. For alternative topology sources, use the class methods:

    - :meth:`from_pid`
    - :meth:`from_synthetic`
    - :meth:`from_xml_file`
    - :meth:`from_xml_buffer`

    .. code-block::

        # Context manager usage (recommended)
        with Topology() as topo:  # Current system
            print(f"Topology depth: {topo.depth}")

        # Synthetic topology
        with Topology.from_synthetic("node:2 core:2 pu:2") as topo:
            print(f"Topology depth: {topo.depth}")

        # Load from XML file
        with Topology.from_xml_file("/path/to/topology.xml") as topo:
            print(f"Topology depth: {topo.depth}")

        # Direct usage,  cleanup is recommended but not required.
        try:
            topo = Topology()
            print(f"Topology depth: {topo.depth}")
        finally:
            topo.destroy()

        # Uses automatic cleanup in the `__del__` method instead. This depends on the gc
        # and doesn't propagate exceptions raised inside the destroy method.
        topo = Topology()

    To use a filter, users need to call the :meth:`load` explicitly:

    .. code-block::

        with Topology(load=False).set_all_types_filter(
            TypeFilter.HWLOC_TYPE_FILTER_KEEP_IMPORTANT
        ).load() as topo:
            pass

    """

    def __init__(self, *, load: bool = True) -> None:
        """Initialize a new topology for the current system.

        Parameters
        ----------
        load :
            Whether the object should load the topology from the system. Set to False if
            you want to apply additional filters.
        """
        hdl = _core.topology_t()

        try:
            _core.topology_init(hdl)
            if load is True:
                _core.topology_load(hdl)
        except (_lib.HwLocError, NotImplementedError) as e:
            if hdl:
                _core.topology_destroy(hdl)
            raise e

        self._hdl = hdl
        self._loaded = load

    @classmethod
    def from_native_handle(cls, hdl: _core.topology_t, loaded: bool) -> Topology:
        topo = cls.__new__(cls)
        topo._hdl = hdl
        topo._loaded = loaded
        topo.check()
        return topo

    @classmethod
    def from_pid(cls, pid: int, *, load: bool = True) -> Topology:
        """Create topology from a specific process ID.

        Parameters
        ----------
        pid
            Process ID to get topology from
        load :
            Whether the object should load the topology from the system. Set to False if
            you want to apply additional filters.

        Returns
        -------
        New Topology instance for the specified process.
        """
        hdl = _core.topology_t(0)
        try:
            _core.topology_init(hdl)
            _core.topology_set_pid(hdl, pid)
            if load is True:
                _core.topology_load(hdl)
        except (_lib.HwLocError, NotImplementedError) as e:
            if hdl:
                _core.topology_destroy(hdl)
            raise e

        return cls.from_native_handle(hdl, load)

    @classmethod
    def from_synthetic(cls, description: str, *, load: bool = True) -> Topology:
        """Create topology from synthetic description.

        Parameters
        ----------
        description
            Synthetic topology description (e.g., "node:2 core:2 pu:2")

        Returns
        -------
        New Topology instance from the synthetic description.
        """
        hdl = _core.topology_t(0)
        try:
            _core.topology_init(hdl)
            _core.topology_set_synthetic(hdl, description)

            if load is True:
                _core.topology_load(hdl)
        except (_lib.HwLocError, NotImplementedError) as e:
            if hdl:
                _core.topology_destroy(hdl)
            raise e

        return cls.from_native_handle(hdl, load)

    @classmethod
    def from_xml_file(
        cls, xml_path: os.PathLike | str, *, load: bool = True
    ) -> Topology:
        """Create topology from XML file.

        Parameters
        ----------
        xml_path
            Path to XML file containing topology
        filters
            Optional filter for I/O objects

        Returns
        -------
        New Topology instance loaded from XML file.
        """
        path = os.fspath(os.path.expanduser(xml_path))
        hdl = _core.topology_t(0)
        try:
            _core.topology_init(hdl)
            _core.topology_set_xml(hdl, path)

            if load is True:
                _core.topology_load(hdl)
        except (_lib.HwLocError, NotImplementedError) as e:
            if hdl:
                _core.topology_destroy(hdl)
            raise e

        return cls.from_native_handle(hdl, load)

    @classmethod
    def from_xml_buffer(cls, xml_buffer: str, *, load: bool = True) -> Topology:
        """Create topology from XML string.

        Parameters
        ----------
        xml_buffer
            XML string containing topology

        Returns
        -------
        New Topology instance loaded from XML string.
        """
        hdl = _from_xml_buffer(xml_buffer, load)
        return cls.from_native_handle(hdl, load)

    def check(self) -> None:
        _core.topology_check(self._hdl)

    def load(self) -> "Topology":
        """Load the topology. No-op if it's already loaded"""
        if not self.is_loaded:
            _core.topology_load(self._hdl)
            self._loaded = True
        return self

    @property
    def native_handle(self) -> _core.topology_t:
        """Get the native hwloc topology handle."""
        if not hasattr(self, "_hdl"):
            raise RuntimeError("Topology has been destroyed")
        return self._hdl

    def export_xml_buffer(self, flags: ExportXmlFlags | int) -> str:
        "See :py:func:`~pyhwloc.hwloc.core.topology_export_xmlbuffer`."
        return _core.topology_export_xmlbuffer(self._hdl, flags)

    def export_xml_file(
        self, path: os.PathLike | str, flags: ExportXmlFlags | int
    ) -> None:
        "See :py:func:`~pyhwloc.hwloc.core.topology_export_xml`."
        path = os.fspath(os.path.expanduser(path))
        _core.topology_export_xml(self._hdl, path, flags)

    def export_synthetic(self, flags: ExportSyntheticFlags | int) -> str:
        "See :py:func:`~pyhwloc.hwloc.core.topology_export_synthetic`."
        n_bytes = 1024
        buf = ctypes.create_string_buffer(n_bytes)
        n_written = _core.topology_export_synthetic(self._hdl, buf, n_bytes, flags)
        while n_written == n_bytes - 1:
            n_bytes = n_bytes * 2
            buf = ctypes.create_string_buffer(n_bytes)
            n_written = _core.topology_export_synthetic(self._hdl, buf, n_bytes, flags)
            if n_bytes >= 8192:
                raise RuntimeError("Failed to export synthetic.")
        assert buf.value is not None
        return buf.value.decode("utf-8")

    @property
    def is_loaded(self) -> bool:
        """Check if topology is loaded and ready for use."""
        return hasattr(self, "_hdl") and self._loaded

    @property
    def is_this_system(self) -> bool:
        """Check if topology represents the current system."""
        if not self.is_loaded:
            return False
        return _core.topology_is_thissystem(self._hdl)

    @property
    def depth(self) -> int:
        """Get the depth of the topology tree."""
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        return _core.topology_get_depth(self._hdl)

    def destroy(self) -> None:
        """Explicitly destroy the topology and free resources."""
        if hasattr(self, "_hdl"):
            _core.topology_destroy(self._hdl)
            self._loaded = False
            del self._hdl

    def __enter__(self) -> Topology:
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.destroy()

    def __del__(self) -> None:
        try:
            self.destroy()
        except Exception as e:
            logging.warning(str(e))

    def __copy__(self) -> Topology:
        new = _core.topology_dup(self._hdl)
        return Topology.from_native_handle(new, loaded=True)

    def __deepcopy__(self, memo: dict) -> Topology:
        return self.__copy__()

    def __getstate__(self) -> dict:
        """Serialize topology state for pickling using XML export."""
        if not self.is_loaded:
            raise RuntimeError("Cannot pickle unloaded topology")

        # Export topology to XML for serialization
        xml_buffer = self.export_xml_buffer(0)  # Use default flags
        return {"xml_buffer": xml_buffer}

    def __setstate__(self, state: dict) -> None:
        """Restore topology state from pickle using XML import."""
        xml_buffer = state["xml_buffer"]
        assert not hasattr(self, "_hdl") and not hasattr(self, "_loaded")

        hdl = _from_xml_buffer(xml_buffer, True)
        self._hdl = hdl
        self._loaded = True

    def _checked_apply_filter(
        self, fn: Callable, type_filter: TypeFilter
    ) -> "Topology":
        # If we don't raise here, hwloc returns EBUSY: Device or resource busy, which is
        # not really helpfu.
        if self.is_loaded:
            raise RuntimeError("Cannot set filter after topology is loaded")
        fn(self._hdl, type_filter)
        return self

    def set_io_types_filter(self, type_filter: TypeFilter) -> "Topology":
        return self._checked_apply_filter(
            _core.topology_set_io_types_filter, type_filter
        )

    def set_all_types_filter(self, type_filter: TypeFilter) -> "Topology":
        return self._checked_apply_filter(
            _core.topology_set_all_types_filter, type_filter
        )

    def set_cache_types_filter(self, type_filter: TypeFilter) -> "Topology":
        return self._checked_apply_filter(
            _core.topology_set_cache_types_filter, type_filter
        )

    def set_icache_types_filter(self, type_filter: TypeFilter) -> "Topology":
        return self._checked_apply_filter(
            _core.topology_set_icache_types_filter, type_filter
        )

    def get_obj_by_depth(self, depth: int, idx: int) -> Object | None:
        """Get object at specific depth and index.

        Parameters
        ----------
        depth
            Depth level in topology tree
        idx
            Index of object at that depth

        Returns
        -------
        Object instance or None if not found
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        ptr = _core.get_obj_by_depth(self._hdl, depth, idx)
        return Object(ptr, weakref.ref(self)) if ptr else None

    def get_obj_by_depth_raw(self, depth: int, idx: int) -> ObjPtr | None:
        """Get raw object pointer at specific depth and index.

        Parameters
        ----------
        depth
            Depth level in topology tree
        idx
            Index of object at that depth

        Returns
        -------
        Raw object pointer or None if not found
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        return _core.get_obj_by_depth(self._hdl, depth, idx)

    def get_obj_by_type(self, obj_type: ObjType, idx: int) -> Object | None:
        """Get object by type and index.

        Parameters
        ----------
        obj_type
            Type of object to find
        idx
            Index of object of that type

        Returns
        -------
        Object instance or None if not found
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        ptr = _core.get_obj_by_type(self._hdl, obj_type, idx)
        return Object(ptr, weakref.ref(self)) if ptr else None

    def get_nbobjs_by_depth(self, depth: int) -> int:
        """Get number of objects at specific depth.

        Parameters
        ----------
        depth
            Depth level in topology tree

        Returns
        -------
        Number of objects at that depth
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        return _core.get_nbobjs_by_depth(self._hdl, depth)

    def get_nbobjs_by_type(self, obj_type: ObjType) -> int:
        """Get number of objects of specific type.

        Parameters
        ----------
        obj_type
            Type of object to count

        Returns
        -------
        Number of objects of that type
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        return _core.get_nbobjs_by_type(self._hdl, obj_type)

    def iter_objects_by_depth(self, depth: int) -> Iterator[Object]:
        """Iterate over all objects at specific depth.

        Parameters
        ----------
        depth
            Depth level in topology tree

        Yields
        ------
        Object instances at that depth

        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")

        prev = None
        while True:
            ptr = _core.get_next_obj_by_depth(self._hdl, depth, prev)
            if ptr is None:
                break
            obj = Object(ptr, weakref.ref(self))
            yield obj
            prev = ptr

    @property
    def n_cores(self) -> int:
        """Get the total number of cores.

        Returns
        -------
        Number of core objects in the topology
        """
        return self.get_nbobjs_by_type(ObjType.HWLOC_OBJ_CORE)

    def iter_objects_by_depth_raw(self, depth: int) -> Iterator[ObjPtr]:
        """Iterate over all raw object pointers at specific depth.

        Parameters
        ----------
        depth
            Depth level in topology tree

        Yields
        ------
        Raw object pointers at that depth
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")

        prev = None
        while True:
            obj = _core.get_next_obj_by_depth(self._hdl, depth, prev)
            if obj is None:
                break
            yield obj
            prev = obj

    def iter_objects_by_type(self, obj_type: ObjType) -> Iterator[Object]:
        """Iterate over all objects of specific type.

        Parameters
        ----------
        obj_type
            Type of object to iterate

        Yields
        ------
        Object instances of that type
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")

        prev = None
        while True:
            ptr = _core.get_next_obj_by_type(self._hdl, obj_type, prev)
            if ptr is None:
                break
            obj = Object(ptr, weakref.ref(self))
            yield obj
            prev = ptr

    def iter_all_objects(self) -> Iterator[Object]:
        """Iterate over all objects in the topology.

        Yields
        ------
        All object instances in depth-first order
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")

        for depth in range(self.depth):
            for obj in self.iter_objects_by_depth(depth):
                yield obj

    def iter_all_objects_raw(self) -> Iterator[ObjPtr]:
        """Iterate over all raw object pointers in the topology.

        Yields
        ------
        All raw object pointers in depth-first order
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")

        for depth in range(self.depth):
            for obj in self.iter_objects_by_depth_raw(depth):
                yield obj

    def get_depth_type(self, depth: int) -> ObjType:
        """Get the object type at specific depth.

        Parameters
        ----------
        depth
            Depth level in topology tree

        Returns
        -------
        Object type at that depth
        """
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        return _core.get_depth_type(self._hdl, depth)

    def iter_cpus(self) -> Iterator[Object]:
        """Iterate over all processing units (CPUs).

        Yields
        ------
        All PU (processing unit) object instances
        """
        return self.iter_objects_by_type(ObjType.HWLOC_OBJ_PU)

    def iter_cores(self) -> Iterator[Object]:
        """Iterate over all cores.

        Yields
        ------
        All core object instances
        """
        return self.iter_objects_by_type(ObjType.HWLOC_OBJ_CORE)

    def iter_numa_nodes(self) -> Iterator[Object]:
        """Iterate over all NUMA nodes.

        Yields
        ------
        All NUMA node object instances
        """
        return self.iter_objects_by_type(ObjType.HWLOC_OBJ_NUMANODE)

    def iter_packages(self) -> Iterator[Object]:
        """Iterate over all packages (sockets).

        Yields
        ------
        All package object instances
        """
        return self.iter_objects_by_type(ObjType.HWLOC_OBJ_PACKAGE)

    @property
    def n_cpus(self) -> int:
        """Get the total number of processing units (CPUs).

        Returns
        -------
        Number of PU objects in the topology
        """
        return self.get_nbobjs_by_type(ObjType.HWLOC_OBJ_PU)

    @property
    def n_numa_nodes(self) -> int:
        """Get the total number of NUMA nodes.

        Returns
        -------
        Number of NUMA node objects in the topology
        """
        return self.get_nbobjs_by_type(ObjType.HWLOC_OBJ_NUMANODE)

    @property
    def n_packages(self) -> int:
        """Get the total number of packages (sockets).

        Returns
        -------
        Number of package objects in the topology
        """
        return self.get_nbobjs_by_type(ObjType.HWLOC_OBJ_PACKAGE)

    @property
    def n_pci_devices(self) -> int:
        """Get the total number of PCI devices.

        Returns
        -------
        Number of PCI device objects in the topology
        """
        return self.get_nbobjs_by_type(ObjType.HWLOC_OBJ_PCI_DEVICE)

    @property
    def n_os_devices(self) -> int:
        """Get the total number of OS devices.

        Returns
        -------
        Number of OS device objects in the topology
        """
        return self.get_nbobjs_by_type(ObjType.HWLOC_OBJ_OS_DEVICE)

    def is_in_subtree(self, obj: Object, subtree_root: Object) -> bool:
        """Check if this object is in the subtree of another object.

        Parameters
        ----------
        obj :
            The object to check.
        subtree_root :
            Root object of the subtree to check

        Returns
        -------
        True if this object is in the subtree.
        """

        return _core.obj_is_in_subtree(self._hdl, obj.native_handle, subtree_root._hdl)
