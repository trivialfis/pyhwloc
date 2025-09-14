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
from collections import namedtuple
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterator,
    Type,
    TypeAlias,
)

from .bitmap import Bitmap as _Bitmap
from .hwloc import core as _core
from .hwobject import Object as _Object
from .hwobject import ObjType as _ObjType
from .utils import _Flags, _memview_to_mem, _or_flags, _reuse_doc

# Distance-related imports (lazy import to avoid circular dependencies)
if TYPE_CHECKING:
    from .distance import Distances

__all__ = [
    "Topology",
    "ExportXmlFlags",
    "ExportSyntheticFlags",
    "TypeFilter",
    "MemBindPolicy",
    "MemBindFlags",
]


def _from_impl(fn: Callable[[_core.topology_t], None], load: bool) -> _core.topology_t:
    hdl = _core.topology_t(0)
    try:
        _core.topology_init(hdl)
        fn(hdl)
        if load is True:
            _core.topology_load(hdl)
    except Exception:
        if hdl:
            _core.topology_destroy(hdl)
        raise
    return hdl


def _from_xml_buffer(xml_buffer: str, load: bool) -> _core.topology_t:
    return _from_impl(lambda hdl: _core.topology_set_xmlbuffer(hdl, xml_buffer), load)


def _to_bitmap(target: _Bitmap | set[int] | _Object) -> _Bitmap:
    if isinstance(target, set):
        bitmap = _Bitmap.from_sched_set(target)
    elif isinstance(target, _Object):
        ns = target.nodeset
        if ns is None:
            raise ValueError("Object has no associated NUMA nodes")
        bitmap = ns
    else:
        bitmap = target
    return bitmap


ObjPtr = _core.ObjPtr
ExportXmlFlags: TypeAlias = _core.ExportXmlFlags
ExportSyntheticFlags: TypeAlias = _core.hwloc_topology_export_synthetic_flags_e
TypeFilter: TypeAlias = _core.TypeFilter
# Memory bind type aliases
MemBindPolicy: TypeAlias = _core.MemBindPolicy
MemBindFlags: TypeAlias = _core.MemBindFlags


class Topology:
    """High-level interface for the hwloc topology.

    This class provides a context manager interface for working with hardware
    topology information. It automatically handles topology initialization,
    loading, and cleanup.

    The default `Topology` constructor initializes a topology object based on the
    current system. For alternative topology sources, use the class methods:

    - :meth:`from_this_system`
    - :meth:`from_pid`
    - :meth:`from_synthetic`
    - :meth:`from_xml_file`
    - :meth:`from_xml_buffer`

    .. code-block::

        # Context manager usage (recommended)
        with Topology.from_this_system() as topo:  # Current system
            print(f"Topology depth: {topo.depth}")

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

    To use a filter, users need to call the :meth:`load` explicitly when not using the
    context manager:

    .. code-block::

        with Topology.from_this_system(load=False).set_all_types_filter(
            TypeFilter.HWLOC_TYPE_FILTER_KEEP_IMPORTANT
        ) as topo:
            # auto load when using a context manager
            pass

        topo = Topology.from_this_system(load=False).set_all_types_filter(
            TypeFilter.HWLOC_TYPE_FILTER_KEEP_IMPORTANT
        ).load() # Load the topology

    """

    def __init__(self) -> None:
        """Short hand for the :py:meth:`from_this_system`. Use the class method if you
        need to delay the load process for customization.

        """

        def _(hdl: _core.topology_t) -> None:
            pass

        hdl = _from_impl(_, True)

        self._hdl = hdl
        self._loaded = True
        # See the distance release method for more info.
        self._cleanup: list[weakref.ReferenceType["Distances"]] = []

    @classmethod
    def from_native_handle(cls, hdl: _core.topology_t, is_loaded: bool) -> Topology:
        topo = cls.__new__(cls)
        topo._hdl = hdl
        topo._loaded = is_loaded
        topo._cleanup = []
        return topo

    @classmethod
    def from_this_system(cls, *, load: bool = True) -> Topology:
        """Create a topology from this system.

        Parameters
        ----------
        load :
            Whether the object should load the topology from the system. Set to False if
            you want to apply additional filters.

        Returns
        -------
        New Topology instance for the specified process.
        """

        def _(hdl: _core.topology_t) -> None:
            pass

        hdl = _from_impl(_, load)
        return cls.from_native_handle(hdl, load)

    @classmethod
    def from_pid(cls, pid: int, *, load: bool = True) -> Topology:
        """Create a topology from a specific process ID.

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
        hdl = _from_impl(lambda hdl: _core.topology_set_pid(hdl, pid), load)
        return cls.from_native_handle(hdl, load)

    @classmethod
    def from_synthetic(cls, description: str, *, load: bool = True) -> Topology:
        """Create a topology from a synthetic description.

        Parameters
        ----------
        description
            Synthetic topology description (e.g., "node:2 core:2 pu:2")
        load :
            Whether the object should load the topology from the system. Set to False if
            you want to apply additional filters.

        Returns
        -------
        New Topology instance from the synthetic description.
        """
        hdl = _from_impl(
            lambda hdl: _core.topology_set_synthetic(hdl, description), load
        )
        return cls.from_native_handle(hdl, load)

    @classmethod
    def from_xml_file(
        cls, xml_path: os.PathLike | str, *, load: bool = True
    ) -> Topology:
        """Create a topology from a XML file.

        Parameters
        ----------
        xml_path
            Path to XML file containing topology
        load :
            Whether the object should load the topology from the system. Set to False if
            you want to apply additional filters.

        Returns
        -------
        New Topology instance loaded from XML file.
        """
        path = os.fspath(os.path.expanduser(xml_path))
        hdl = _from_impl(lambda hdl: _core.topology_set_xml(hdl, path), load)
        return cls.from_native_handle(hdl, load)

    @classmethod
    def from_xml_buffer(cls, xml_buffer: str, *, load: bool = True) -> Topology:
        """Create a topology from a XML string.

        Parameters
        ----------
        xml_buffer
            XML string containing topology
        load :
            Whether the object should load the topology from the system. Set to False if
            you want to apply additional filters.

        Returns
        -------
        New Topology instance loaded from XML string.
        """
        hdl = _from_xml_buffer(xml_buffer, load)
        return cls.from_native_handle(hdl, load)

    @_reuse_doc(_core.topology_check)
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
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        return self._hdl

    @_reuse_doc(_core.topology_export_xmlbuffer)
    def export_xml_buffer(self, flags: ExportXmlFlags | int) -> str:
        return _core.topology_export_xmlbuffer(self.native_handle, flags)

    @_reuse_doc(_core.topology_export_xml)
    def export_xml_file(
        self, path: os.PathLike | str, flags: ExportXmlFlags | int
    ) -> None:
        path = os.fspath(os.path.expanduser(path))
        _core.topology_export_xml(self.native_handle, path, flags)

    @_reuse_doc(_core.topology_export_synthetic)
    def export_synthetic(self, flags: ExportSyntheticFlags | int) -> str:
        n_bytes = 1024
        buf = ctypes.create_string_buffer(n_bytes)
        n_written = _core.topology_export_synthetic(
            self.native_handle, buf, n_bytes, flags
        )
        while n_written == n_bytes - 1:
            n_bytes = n_bytes * 2
            buf = ctypes.create_string_buffer(n_bytes)
            n_written = _core.topology_export_synthetic(
                self.native_handle, buf, n_bytes, flags
            )
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
        return _core.topology_is_thissystem(self.native_handle)

    def get_support(self) -> Any:
        """See :py:func:`pyhwloc.hwloc.core.topology_get_support`.

        Returns
        -------
        A namedtuple with the same structure as :c:struct:`hwloc_topology_support`.
        """
        support = _core.topology_get_support(self.native_handle).contents
        result: dict[str, dict[str, bool]] = {}
        for k, v in support._fields_:  # type: ignore
            result[k] = {}
            v0 = getattr(support, k)
            if v0:
                for k1, _ in v0.contents._fields_:
                    v1 = getattr(v0.contents, k1)
                    assert v1 in (0, 1)
                    result[k][k1] = bool(v1)

        TS = namedtuple("TopologySupport", list(result.keys()))  # type: ignore

        def create_child(name: str, d: dict) -> Any:
            Typ = namedtuple(name.capitalize() + "Support", d.keys())  # type: ignore
            v = Typ(**d)
            return v

        tran = {k: create_child(k, v) for k, v in result.items()}

        sup = TS(**tran)
        return sup

    @property
    @_reuse_doc(_core.topology_get_depth)
    def depth(self) -> int:
        return _core.topology_get_depth(self.native_handle)

    def destroy(self) -> None:
        """Explicitly destroy the topology and free resources."""
        while self._cleanup:
            dist_ref = self._cleanup.pop()
            dist = dist_ref()
            if dist:
                dist.release()

        if hasattr(self, "_hdl"):
            _core.topology_destroy(self.native_handle)
            self._loaded = False
            del self._hdl

    def __enter__(self) -> Topology:
        if not self.is_loaded:
            self.load()
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
        new = _core.topology_dup(self.native_handle)
        return Topology.from_native_handle(new, True)

    def __deepcopy__(self, memo: dict) -> Topology:
        return self.__copy__()

    def __getstate__(self) -> dict:
        """Serialize topology state for pickling using XML export."""
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
        self._cleanup = []

    def _checked_apply_filter(
        self, fn: Callable, type_filter: TypeFilter
    ) -> "Topology":
        # If we don't raise here, hwloc returns EBUSY: Device or resource busy, which is
        # not really helpful.
        if self.is_loaded:
            raise RuntimeError("Cannot set filter after topology is loaded")
        # Unchecked access to handle as we haven't loaded the topo yet.
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

    def get_obj_by_depth(self, depth: int, idx: int) -> _Object | None:
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
        ptr = _core.get_obj_by_depth(self.native_handle, depth, idx)
        return _Object(ptr, weakref.ref(self)) if ptr else None

    @_reuse_doc(_core.get_root_obj)
    def get_root_obj(self) -> _Object:
        return _Object(_core.get_root_obj(self.native_handle), weakref.ref(self))

    @_reuse_doc(_core.get_obj_by_type)
    def get_obj_by_type(self, obj_type: _ObjType, idx: int) -> _Object | None:
        ptr = _core.get_obj_by_type(self.native_handle, obj_type, idx)
        return _Object(ptr, weakref.ref(self)) if ptr else None

    @_reuse_doc(_core.get_nbobjs_by_depth)
    def get_nbobjs_by_depth(self, depth: int) -> int:
        return _core.get_nbobjs_by_depth(self.native_handle, depth)

    @_reuse_doc(_core.get_nbobjs_by_type)
    def get_nbobjs_by_type(self, obj_type: _ObjType) -> int:
        return _core.get_nbobjs_by_type(self.native_handle, obj_type)

    def iter_objects_by_depth(self, depth: int) -> Iterator[_Object]:
        """Iterate over all objects at specific depth.

        Parameters
        ----------
        depth
            Depth level in topology tree

        Yields
        ------
        Object instances at that depth

        """
        prev = None
        while True:
            ptr = _core.get_next_obj_by_depth(self.native_handle, depth, prev)
            if ptr is None:
                break
            obj = _Object(ptr, weakref.ref(self))
            yield obj
            prev = ptr

    @property
    def n_cores(self) -> int:
        """Get the total number of cores.

        Returns
        -------
        Number of core objects in the topology
        """
        return self.get_nbobjs_by_type(_ObjType.HWLOC_OBJ_CORE)

    def iter_objects_by_type(self, obj_type: _ObjType) -> Iterator[_Object]:
        """Iterate over all objects of specific type.

        Parameters
        ----------
        obj_type
            Type of object to iterate

        Yields
        ------
        Object instances of that type
        """
        prev = None
        while True:
            ptr = _core.get_next_obj_by_type(self.native_handle, obj_type, prev)
            if ptr is None:
                break
            obj = _Object(ptr, weakref.ref(self))
            yield obj
            prev = ptr

    def iter_all_breadth_first(self) -> Iterator[_Object]:
        """Iterate over all objects in the topology.

        Yields
        ------
        All object instances in breadth first order.
        """
        for depth in range(self.depth):
            for obj in self.iter_objects_by_depth(depth):
                yield obj

    # We can implement pre/in/post-order traversal if needed.

    def get_depth_type(self, depth: int) -> _ObjType:
        """Get the object type at specific depth.

        Parameters
        ----------
        depth
            Depth level in topology tree

        Returns
        -------
        Object type at that depth
        """
        return _core.get_depth_type(self.native_handle, depth)

    def iter_cpus(self) -> Iterator[_Object]:
        """Iterate over all processing units (CPUs).

        Yields
        ------
        All PU (processing unit) object instances
        """
        return self.iter_objects_by_type(_ObjType.HWLOC_OBJ_PU)

    def iter_cores(self) -> Iterator[_Object]:
        """Iterate over all cores.

        Yields
        ------
        All core object instances
        """
        return self.iter_objects_by_type(_ObjType.HWLOC_OBJ_CORE)

    def iter_numa_nodes(self) -> Iterator[_Object]:
        """Iterate over all NUMA nodes.

        Yields
        ------
        All NUMA node object instances
        """
        return self.iter_objects_by_type(_ObjType.HWLOC_OBJ_NUMANODE)

    def iter_packages(self) -> Iterator[_Object]:
        """Iterate over all packages (sockets).

        Yields
        ------
        All package object instances
        """
        return self.iter_objects_by_type(_ObjType.HWLOC_OBJ_PACKAGE)

    @property
    def n_cpus(self) -> int:
        """Get the total number of processing units (CPUs).

        Returns
        -------
        Number of PU objects in the topology
        """
        return self.get_nbobjs_by_type(_ObjType.HWLOC_OBJ_PU)

    @property
    def n_numa_nodes(self) -> int:
        """Get the total number of NUMA nodes.

        Returns
        -------
        Number of NUMA node objects in the topology
        """
        return self.get_nbobjs_by_type(_ObjType.HWLOC_OBJ_NUMANODE)

    @property
    def n_packages(self) -> int:
        """Get the total number of packages (sockets).

        Returns
        -------
        Number of package objects in the topology
        """
        return self.get_nbobjs_by_type(_ObjType.HWLOC_OBJ_PACKAGE)

    @property
    def n_pci_devices(self) -> int:
        """Get the total number of PCI devices.

        Returns
        -------
        Number of PCI device objects in the topology
        """
        return self.get_nbobjs_by_type(_ObjType.HWLOC_OBJ_PCI_DEVICE)

    @property
    def n_os_devices(self) -> int:
        """Get the total number of OS devices.

        Returns
        -------
        Number of OS device objects in the topology
        """
        return self.get_nbobjs_by_type(_ObjType.HWLOC_OBJ_OS_DEVICE)

    # Distance Methods
    @_reuse_doc(_core.distances_get)
    def get_distances(self, kind: int = 0) -> list["Distances"]:
        from .distance import Distances

        # Get count first
        nr = ctypes.c_uint(0)
        result: list[Distances] = []

        _core.distances_get(
            self.native_handle,
            ctypes.byref(nr),
            None,
            int(kind),
        )
        distances_ptr_ptr = (ctypes.POINTER(_core.hwloc_distances_s) * nr.value)()
        if nr.value == 0:
            return result

        _core.distances_get(
            self.native_handle,
            ctypes.byref(nr),
            distances_ptr_ptr,
            int(kind),
        )

        # Create Distance objects
        for i in range(nr.value):
            dist_handle = distances_ptr_ptr[i]
            result.append(Distances(dist_handle, weakref.ref(self)))

        # Push into the cleanup queue. We also perform some cleanups here to avoid
        # having too many references.
        still_valid = []
        for ref in self._cleanup:
            if ref() is not None:
                still_valid.append(ref)
        self._cleanup = still_valid
        self._cleanup.extend([weakref.ref(dist) for dist in result])

        return result

    # Memory Binding Methods
    def set_membind(
        self,
        target: _Bitmap | set[int] | _Object,
        policy: MemBindPolicy,
        flags: _Flags[MemBindFlags],
    ) -> None:
        """Bind the current process memory to specified NUMA nodes. The current process
        is assumed to be single-threaded.

        Parameters
        ----------
        target
            NUMA nodes to bind memory to. This can be an
            :py:class:`~pyhwloc.hwobject.Object`, a :py:class:`~pyhwloc.bitmap.Bitmap`,
            or a CPU set used by the `os.sched_*` routines (:py:class:`set` [int]).
        policy
            Memory binding policy to use
        flags
            Additional flags for memory binding.

        """
        bitmap = _to_bitmap(target)
        _core.set_membind(
            self.native_handle, bitmap.native_handle, policy, _or_flags(flags)
        )

    def get_membind(
        self, flags: _Flags[MemBindFlags] = 0
    ) -> tuple[_Bitmap, MemBindPolicy]:
        """Get current process memory binding.

        Parameters
        ----------
        flags
            Flags for getting memory binding

        Returns
        -------
        Tuple of (bitmap, policy) for current memory binding
        """
        bitmap = _Bitmap()
        policy = _core.get_membind(
            self.native_handle, bitmap.native_handle, _or_flags(flags)
        )
        return bitmap, policy

    def set_proc_membind(
        self,
        pid: int,
        target: _Bitmap | set[int] | _Object,
        policy: MemBindPolicy,
        flags: _Flags[MemBindFlags],
    ) -> None:
        """Bind specific process memory to NUMA nodes.

        Parameters
        ----------
        pid
            Process ID to bind.
        target
            NUMA nodes to bind memory to. This can be an
            :py:class:`~pyhwloc.hwobject.Object`, a :py:class:`~pyhwloc.bitmap.Bitmap`,
            or a CPU set used by the `os.sched_*` routines (:py:class:`set` [int]).
        policy
            Memory binding policy to use
        flags
            Additional flags for memory binding
        """
        bitmap = _to_bitmap(target)
        hdl = None
        try:
            hdl = _core._open_proc_handle(pid, False)
            _core.set_proc_membind(
                self.native_handle, hdl, bitmap.native_handle, policy, _or_flags(flags)
            )
        finally:
            if hdl:
                _core._close_proc_handle(hdl)

    def get_proc_membind(
        self, pid: int, flags: _Flags[MemBindFlags] = 0
    ) -> tuple[_Bitmap, MemBindPolicy]:
        """Get process memory binding.

        Parameters
        ----------
        pid
            Process ID to query.
        flags
            Flags for getting memory binding.

        Returns
        -------
        Tuple of (nodeset, policy) for process memory binding
        """
        nodeset = _Bitmap()
        hdl = None
        try:
            hdl = _core._open_proc_handle(pid)
            policy = _core.get_proc_membind(
                self.native_handle, hdl, nodeset.native_handle, _or_flags(flags)
            )
            return nodeset, policy
        finally:
            if hdl:
                _core._close_proc_handle(hdl)

    def set_area_membind(
        self,
        mem: memoryview,
        target: _Bitmap | set[int] | _Object,
        policy: MemBindPolicy,
        flags: _Flags[MemBindFlags],
    ) -> None:
        """Bind memory area to NUMA nodes.

        Parameters
        ----------
        mem
            Memory area. Use :py:func:`~pyhwloc.utils.memoryview_from_memory` to
            construct a :py:class:`memoryview` if you have pointers.
        target
            NUMA nodes to bind memory to. This can be an
            :py:class:`~pyhwloc.hwobject.Object`, a :py:class:`~pyhwloc.bitmap.Bitmap`,
            or a CPU set used by the `os.sched_*` routines (:py:class:`set` [int]).
        policy
            Memory binding policy to use.
        flags
            Additional flags for memory binding.
        """
        bitmap = _to_bitmap(target)
        addr, size = _memview_to_mem(mem)

        _core.set_area_membind(
            self.native_handle,
            addr,
            size,
            bitmap.native_handle,
            policy,
            _or_flags(flags),
        )

    def get_area_membind(
        self,
        mem: memoryview,
        flags: _Flags[MemBindFlags] = 0,
    ) -> tuple[_Bitmap, MemBindPolicy]:
        """Get memory area binding.

        Parameters
        ----------
        mem
            Memory area. Use :py:func:`~pyhwloc.utils.memoryview_from_memory` to
            construct a :py:class:`memoryview` if you have pointers.
        flags
            Flags for getting memory binding.

        Returns
        -------
        Tuple of (bitmap, policy) for memory area binding
        """
        bitmap = _Bitmap()
        addr, size = _memview_to_mem(mem)

        policy = _core.get_area_membind(
            self.native_handle, addr, size, bitmap.native_handle, _or_flags(flags)
        )
        return bitmap, policy

    # Allocator interface is not exposed. I checked popular libraries like torch, none
    # of them supports setting custom allocator in Python. We can come back to this if
    # someone asks for it.


@_reuse_doc(_core.get_api_version)
def get_api_version() -> tuple[int, int, int]:
    v = _core.get_api_version()
    major = v >> 16
    minor = (v >> 8) & 0xFF
    rev = v & 0xFF
    return major, minor, rev
