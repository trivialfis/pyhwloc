# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
The Object Interface
====================

Python interface of the hwloc_obj type.

"""

from __future__ import annotations

import ctypes
import weakref
from enum import IntEnum
from typing import TYPE_CHECKING, Iterator, TypeAlias

from .bitmap import Bitmap
from .hwloc import core as _core
from .utils import _Flags, _or_flags, _reuse_doc

if TYPE_CHECKING:
    from .topology import Topology

__all__ = [
    "Object",
    "ObjType",
    "ObjOsdevType",
    "ObjSnprintfFlag",
    "GetTypeDepth",
    "compare_types",
    "ObjTypeCmp",
]


ObjType: TypeAlias = _core.ObjType
ObjOsdevType: TypeAlias = _core.ObjOsdevType
ObjSnprintfFlag: TypeAlias = _core.ObjSnprintfFlag
GetTypeDepth: TypeAlias = _core.GetTypeDepth


class Object:
    """High-level interface for the hwloc object. Only the topology can return
    objects. User should not use the constructor.

    Parameters
    ----------
    hdl :
        Raw pointer to hwloc object

    """

    def __init__(
        self, hdl: _core.ObjPtr, topology: weakref.ReferenceType["Topology"]
    ) -> None:
        assert hdl
        self._hdl = hdl
        self._topo_ref = topology

    @property
    def native_handle(self) -> _core.ObjPtr:
        """Get the raw object pointer."""
        if not self._topo_ref or not self._topo_ref().is_loaded:  # type: ignore
            raise RuntimeError("Topology is invalid")
        return self._hdl

    @property
    def _topo(self) -> "Topology":
        if not self._topo_ref or not self._topo_ref().is_loaded:  # type: ignore
            raise RuntimeError("Topology is invalid")
        v = self._topo_ref()
        assert v is not None
        return v

    @property
    def type(self) -> ObjType:
        """Type of object."""
        return ObjType(self.native_handle.contents.type)

    @property
    def subtype(self) -> str | None:
        """Subtype string to better describe the type field."""
        if self.native_handle.contents.subtype:
            return self.native_handle.contents.subtype.decode("utf-8")
        return None

    @property
    def os_index(self) -> int:
        """OS-provided physical index number."""
        return self.native_handle.contents.os_index

    @property
    def name(self) -> str | None:
        """Object-specific name if any."""
        if self.native_handle.contents.name:
            return self.native_handle.contents.name.decode("utf-8")
        return None

    @property
    def total_memory(self) -> int:
        """Total memory (in bytes) in NUMA nodes below this object."""
        return self.native_handle.contents.total_memory

    # - Begin accessors for attr
    def is_numa_node(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_NUMANODE

    def is_group(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_GROUP

    def is_pci_device(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_PCI_DEVICE

    def is_bridge(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_BRIDGE

    def is_os_device(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_OS_DEVICE

    def is_package(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_PACKAGE

    def is_machine(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_MACHINE

    def is_osdev_type(self, typ: int) -> bool:
        if not self.is_os_device():
            return False

        attr = self.attr
        if attr is None:
            return False
        osdev_types = attr.types
        return bool(osdev_types & typ)

    def is_osdev_gpu(self) -> bool:
        return self.is_osdev_type(ObjOsdevType.HWLOC_OBJ_OSDEV_GPU)

    def is_osdev_storage(self) -> bool:
        return self.is_osdev_type(ObjOsdevType.HWLOC_OBJ_OSDEV_STORAGE)

    # Kinds of object Type
    @_reuse_doc(_core.obj_type_is_normal)
    def is_normal(self) -> bool:
        return _core.obj_type_is_normal(self.type)

    @_reuse_doc(_core.obj_type_is_io)
    def is_io(self) -> bool:
        return _core.obj_type_is_io(self.type)

    @_reuse_doc(_core.obj_type_is_memory)
    def is_memory(self) -> bool:
        return _core.obj_type_is_memory(self.type)

    @_reuse_doc(_core.obj_type_is_cache)
    def is_cache(self) -> bool:
        return _core.obj_type_is_cache(self.type)

    @_reuse_doc(_core.obj_type_is_dcache)
    def is_dcache(self) -> bool:
        return _core.obj_type_is_dcache(self.type)

    @_reuse_doc(_core.obj_type_is_icache)
    def is_icache(self) -> bool:
        return _core.obj_type_is_icache(self.type)

    # fixme: We might want to create a class hierarchy insetad
    @property
    def attr(self) -> ctypes.Structure | None:
        """Get attributes of this object. The return type depends on the type of this
        object as the underlying type is a C union :c:union:`hwloc_obj_attr_u`. We have
        a number of methods for commonly used attributes like the :py:meth:`is_normal`,
        but don't have a proper wrapper for the entire union yet.

        All pyhwloc structs can be properly printed in Python. To get an overview of the
        object attributes, you can print the result from this method, or use the
        :py:meth:`format_attr`.

        """
        attr = self.native_handle.contents.attr
        if not attr:
            return None
        # FIXME: Am I getting this right? I looked into the `hwloc_obj_attr_snprintf`
        # implementation, but it doesn't use the group. Also, if the bridge upstream is
        # HWLOC_OBJ_BRIDGE_PCI, this union can be converted to PCIe?
        if self.is_cache():
            return attr.contents.cache

        typ = self.type
        match typ:
            case ObjType.HWLOC_OBJ_NUMANODE:
                return attr.contents.numanode
            # cache has been handled
            case ObjType.HWLOC_OBJ_GROUP:
                return attr.contents.group
            case ObjType.HWLOC_OBJ_PCI_DEVICE:
                return attr.contents.pcidev
            case ObjType.HWLOC_OBJ_BRIDGE:
                return attr.contents.bridge
            case ObjType.HWLOC_OBJ_OS_DEVICE:
                return attr.contents.osdev
            case _:
                return None

    def format_attr(
        self,
        sep: str = ", ",
        flags: _Flags[
            ObjSnprintfFlag
        ] = ObjSnprintfFlag.HWLOC_OBJ_SNPRINTF_FLAG_OLD_VERBOSE,
    ) -> str | None:
        """Print the attributes."""
        n_bytes = 1024
        buf = ctypes.create_string_buffer(n_bytes)
        _core.obj_attr_snprintf(buf, n_bytes, self.native_handle, sep, _or_flags(flags))
        if not buf.value:
            return None
        return buf.value.decode("utf-8")

    # - End accessors for attr

    @property
    def depth(self) -> int:
        """Vertical index in the hierarchy."""
        return self.native_handle.contents.depth

    @property
    def logical_index(self) -> int:
        """Horizontal index in the whole list of similar objects."""
        return self.native_handle.contents.logical_index

    @property
    def next_cousin(self) -> Object | None:
        """Next object of same type and depth."""
        if self.native_handle.contents.next_cousin:
            return Object(self.native_handle.contents.next_cousin, self._topo_ref)
        return None

    @property
    def prev_cousin(self) -> Object | None:
        """Previous object of same type and depth."""
        if self.native_handle.contents.prev_cousin:
            return Object(self.native_handle.contents.prev_cousin, self._topo_ref)
        return None

    @property
    def parent(self) -> Object | None:
        """Parent object, None if root (Machine object)."""
        if self.native_handle.contents.parent:
            return Object(self.native_handle.contents.parent, self._topo_ref)
        return None

    @property
    def sibling_rank(self) -> int:
        """Index in parent's children array."""
        return self.native_handle.contents.sibling_rank

    @property
    def next_sibling(self) -> Object | None:
        """Next object below the same parent."""
        if self.native_handle.contents.next_sibling:
            return Object(self.native_handle.contents.next_sibling, self._topo_ref)
        return None

    @property
    def prev_sibling(self) -> Object | None:
        """Previous object below the same parent."""
        if self.native_handle.contents.prev_sibling:
            return Object(self.native_handle.contents.prev_sibling, self._topo_ref)
        return None

    @property
    def arity(self) -> int:
        """Number of normal children."""
        return self.native_handle.contents.arity

    #   struct hwloc_obj **children;

    @property
    def first_child(self) -> Object | None:
        """First normal child."""
        if self.native_handle.contents.first_child:
            return Object(self.native_handle.contents.first_child, self._topo_ref)
        return None

    @property
    def last_child(self) -> Object | None:
        """Last normal child."""
        if self.native_handle.contents.last_child:
            return Object(self.native_handle.contents.last_child, self._topo_ref)
        return None

    @property
    def symmetric_subtree(self) -> bool:
        """Set if the subtree of normal objects below this object is symmetric."""
        return bool(self.native_handle.contents.symmetric_subtree)

    @property
    def memory_arity(self) -> int:
        """Number of Memory children."""
        return self.native_handle.contents.memory_arity

    @property
    def memory_first_child(self) -> Object | None:
        """First Memory child."""
        if self.native_handle.contents.memory_first_child:
            return Object(
                self.native_handle.contents.memory_first_child, self._topo_ref
            )
        return None

    @property
    def io_arity(self) -> int:
        """Number of I/O children."""
        return self.native_handle.contents.io_arity

    @property
    def io_first_child(self) -> Object | None:
        """First I/O child."""
        if self.native_handle.contents.io_first_child:
            return Object(self.native_handle.contents.io_first_child, self._topo_ref)
        return None

    @property
    def misc_arity(self) -> int:
        """Number of Misc children."""
        return self.native_handle.contents.misc_arity

    @property
    def misc_first_child(self) -> Object | None:
        """First Misc child."""
        if self.native_handle.contents.misc_first_child:
            return Object(self.native_handle.contents.misc_first_child, self._topo_ref)
        return None

    @property
    def cpuset(self) -> Bitmap | None:
        """CPUs covered by this object."""
        cpuset = self.native_handle.contents.cpuset
        return Bitmap.from_native_handle(cpuset, own=False) if cpuset else None

    @property
    def complete_cpuset(self) -> Bitmap | None:
        """The complete CPU set of processors of this object."""
        complete_cpuset = self.native_handle.contents.complete_cpuset
        return (
            Bitmap.from_native_handle(complete_cpuset, own=False)
            if complete_cpuset
            else None
        )

    @property
    def nodeset(self) -> Bitmap | None:
        """NUMA nodes covered by this object or containing this object."""
        nodeset = self.native_handle.contents.nodeset
        return Bitmap.from_native_handle(nodeset, own=False) if nodeset else None

    @property
    def complete_nodeset(self) -> Bitmap | None:
        """The complete NUMA node set of this object."""
        complete_nodeset = self.native_handle.contents.complete_nodeset
        return (
            Bitmap.from_native_handle(complete_nodeset, own=False)
            if complete_nodeset
            else None
        )

    # struct hwloc_infos_s infos
    # void *userdata

    @property
    def gp_index(self) -> int:
        "Global persistent index."
        return int(self.native_handle.contents.gp_index)

    def iter_children(self) -> Iterator[Object]:
        """Iterate over all children of this object."""
        child = self.first_child
        while child:
            yield child
            # fixme: Should we use `get_next_child` instead?
            child = child.next_sibling

    def iter_memory_children(self) -> Iterator[Object]:
        """Iterate over all memory children of this object."""
        child = self.memory_first_child
        while child:
            yield child
            child = child.next_sibling

    def iter_io_children(self) -> Iterator[Object]:
        """Iterate over all I/O children of this object."""
        child = self.io_first_child
        while child:
            yield child
            child = child.next_sibling

    def iter_misc_children(self) -> Iterator[Object]:
        """Iterate over all misc children of this object."""
        child = self.misc_first_child
        while child:
            yield child
            child = child.next_sibling

    def iter_siblings(self) -> Iterator[Object]:
        """Iterate over all siblings of this object (including self)."""
        # Go to first sibling
        current: Object | None = self
        assert current is not None

        while current.prev_sibling is not None:
            current = current.prev_sibling

        # Iterate through all siblings
        while current is not None:
            yield current
            current = current.next_sibling

    @_reuse_doc(_core.obj_get_info_by_name)
    def get_info_by_name(self, name: str) -> str | None:
        return _core.obj_get_info_by_name(self.native_handle, name)

    # Looking at Ancestor and Child Objects

    @_reuse_doc(_core.get_common_ancestor_obj)
    def common_ancestor_obj(self, other: Object) -> Object:
        if self.depth < 0 or other.depth < 0:
            raise ValueError("This function only works with objects in the main tree.")
        return Object(
            _core.get_common_ancestor_obj(
                self._topo.native_handle, self.native_handle, other.native_handle
            ),
            self._topo_ref,
        )

    @_reuse_doc(_core.get_ancestor_obj_by_depth)
    def get_ancestor_obj_by_depth(self, depth: int) -> Object | None:
        obj = _core.get_ancestor_obj_by_depth(
            self._topo.native_handle, depth, self.native_handle
        )
        if obj is None:
            return None
        return Object(
            obj,
            self._topo_ref,
        )

    @_reuse_doc(_core.get_ancestor_obj_by_type)
    def get_ancestor_obj_by_type(self, obj_type: ObjType) -> Object | None:
        obj = _core.get_ancestor_obj_by_type(
            self._topo.native_handle, obj_type, self.native_handle
        )
        if obj is None:
            return None
        return Object(
            obj,
            self._topo_ref,
        )

    @_reuse_doc(_core.obj_is_in_subtree)
    def is_in_subtree(self, subtree_root: Object) -> bool:
        return _core.obj_is_in_subtree(
            self._topo.native_handle, self.native_handle, subtree_root.native_handle
        )

    # End -- Looking at Ancestor and Child Objects

    def __str__(self) -> str:
        type_name = self.type.name.replace("HWLOC_OBJ_", "")
        parts = [f"{type_name}#{self.logical_index}"]

        if self.name:
            parts.append(f"({self.name})")
        if self.subtype:
            parts.append(f"[{self.subtype}]")

        return " ".join(parts)

    def __repr__(self) -> str:
        return (
            f"Object(type={self.type.name}, "
            f"logical_index={self.logical_index}, "
            f"depth={self.depth})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality based on pointer address."""
        if not isinstance(other, Object):
            return False
        return _core.is_same_obj(self.native_handle, other.native_handle)

    def __hash__(self) -> int:
        """Hash based on pointer address."""
        return hash(ctypes.addressof(self.native_handle.contents))


class ObjTypeCmp(IntEnum):
    """Result from :py:func:`~pyhwloc.hwobject.compare_types`."""

    UNORDERED = _core.HWLOC_TYPE_UNORDERED
    INCLUDE = -1
    EQUAL = 0
    INCLUDED_BY = 1


def compare_types(type1: ObjType | Object, type2: ObjType | Object) -> ObjTypeCmp:
    """See the relationship between two object types. If the returned enum is
    ``INCLUDE``, it implies that `type1` objects **usually** include `type2`
    objects. The reverse is indicated by the ``INCLUDED_BY``.

    """
    if isinstance(type1, Object):
        type1 = type1.type
    if isinstance(type2, Object):
        type2 = type2.type
    r = _core.compare_types(type1, type2)
    if r == _core.HWLOC_TYPE_UNORDERED:
        return ObjTypeCmp.UNORDERED
    if r < 0:
        return ObjTypeCmp.INCLUDE
    if r > 0:
        return ObjTypeCmp.INCLUDED_BY
    return ObjTypeCmp.EQUAL
