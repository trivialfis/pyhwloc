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
The Object Interface
====================

Python interface of the hwloc_obj type.

"""
from __future__ import annotations

import ctypes
from typing import Iterator

from .hwloc import core as _core
from .hwloc.bitmap import bitmap_t

__all__ = ["Object", "ObjType"]


ObjType = _core.hwloc_obj_type_t
ObjOsdevType = _core.hwloc_obj_osdev_type_e
ObjSnprintfFlag = _core.hwloc_obj_snprintf_flag_e
GetTypeDepth = _core.hwloc_get_type_depth_e


class Object:
    """High-level interface for the hwloc object. Only the topology can return
    objects. User should not use the constructor.

    Parameters
    ----------
    hdl :
        Raw pointer to hwloc object

    """

    def __init__(self, hdl: _core.ObjPtr) -> None:
        if hdl is None:
            raise ValueError("Object pointer cannot be None")
        self._hdl = hdl

    @property
    def native_handle(self) -> _core.ObjPtr:
        """Get the raw object pointer."""
        return self._hdl

    @property
    def type(self) -> ObjType:
        """Type of object."""
        return ObjType(self._hdl.contents.type)

    @property
    def subtype(self) -> str | None:
        """Subtype string to better describe the type field."""
        if self._hdl.contents.subtype:
            return self._hdl.contents.subtype.decode("utf-8")
        return None

    @property
    def os_index(self) -> int:
        """OS-provided physical index number."""
        return self._hdl.contents.os_index

    @property
    def name(self) -> str | None:
        """Object-specific name if any."""
        if self._hdl.contents.name:
            return self._hdl.contents.name.decode("utf-8")
        return None

    @property
    def total_memory(self) -> int:
        """Total memory (in bytes) in NUMA nodes below this object."""
        return self._hdl.contents.total_memory

    # - Begin accessors for attr
    @property
    def is_numa_node(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_NUMANODE

    @property
    def is_cache(self) -> bool:
        return self.type in (
            ObjType.HWLOC_OBJ_L1CACHE,
            ObjType.HWLOC_OBJ_L2CACHE,
            ObjType.HWLOC_OBJ_L3CACHE,
            ObjType.HWLOC_OBJ_L4CACHE,
            ObjType.HWLOC_OBJ_L5CACHE,
            ObjType.HWLOC_OBJ_L1ICACHE,
            ObjType.HWLOC_OBJ_L2ICACHE,
            ObjType.HWLOC_OBJ_L3ICACHE,
            ObjType.HWLOC_OBJ_MEMCACHE,
        )

    @property
    def is_group(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_GROUP

    @property
    def is_pci_device(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_PCI_DEVICE

    @property
    def is_bridge(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_BRIDGE

    @property
    def is_os_device(self) -> bool:
        return self.type == ObjType.HWLOC_OBJ_OS_DEVICE

    def is_osdev_type(self, typ: int) -> bool:
        if not self.is_os_device:
            return False

        attr = self.attr
        if attr is None:
            return False
        osdev_types = attr.types
        return bool(osdev_types & typ)

    @property
    def is_osdev_gpu(self) -> bool:
        return self.is_osdev_type(ObjOsdevType.HWLOC_OBJ_OSDEV_GPU)

    @property
    def attr(self) -> ctypes.Structure | None:
        typ = self.type
        attr = self._hdl.contents.attr
        if not attr:
            return None
        # FIXME: Am I getting this right? I looked into the `hwloc_obj_attr_snprintf`
        # implementation, but it doesn't use the group. Also, if the bridge upstream is
        # HWLOC_OBJ_BRIDGE_PCI, this union can be converted to PCIe?
        match typ:
            case ObjType.HWLOC_OBJ_NUMANODE:
                return attr.contents.numanode
            case (
                ObjType.HWLOC_OBJ_L1CACHE
                | ObjType.HWLOC_OBJ_L2CACHE
                | ObjType.HWLOC_OBJ_L3CACHE
                | ObjType.HWLOC_OBJ_L4CACHE
                | ObjType.HWLOC_OBJ_L5CACHE
                | ObjType.HWLOC_OBJ_L1ICACHE
                | ObjType.HWLOC_OBJ_L2ICACHE
                | ObjType.HWLOC_OBJ_L3ICACHE
                | ObjType.HWLOC_OBJ_MEMCACHE
            ):
                return attr.contents.cache
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

    def attr_str(
        self,
        flags: int = ObjSnprintfFlag.HWLOC_OBJ_SNPRINTF_FLAG_OLD_VERBOSE,
    ) -> str | None:
        n_bytes = 1024
        buf = ctypes.create_string_buffer(n_bytes)
        _core.obj_attr_snprintf(buf, n_bytes, self.native_handle, b", ", flags)
        if not buf.value:
            return None
        return buf.value.decode("utf-8")
    # - End accessors for attr

    @property
    def depth(self) -> int:
        """Vertical index in the hierarchy."""
        return self._hdl.contents.depth

    @property
    def logical_index(self) -> int:
        """Horizontal index in the whole list of similar objects."""
        return self._hdl.contents.logical_index

    @property
    def next_cousin(self) -> Object | None:
        """Next object of same type and depth."""
        if self._hdl.contents.next_cousin:
            return Object(self._hdl.contents.next_cousin)
        return None

    @property
    def prev_cousin(self) -> Object | None:
        """Previous object of same type and depth."""
        if self._hdl.contents.prev_cousin:
            return Object(self._hdl.contents.prev_cousin)
        return None

    @property
    def parent(self) -> Object | None:
        """Parent object, None if root (Machine object)."""
        if self._hdl.contents.parent:
            return Object(self._hdl.contents.parent)
        return None

    @property
    def sibling_rank(self) -> int:
        """Index in parent's children array."""
        return self._hdl.contents.sibling_rank

    @property
    def next_sibling(self) -> Object | None:
        """Next object below the same parent."""
        if self._hdl.contents.next_sibling:
            return Object(self._hdl.contents.next_sibling)
        return None

    @property
    def prev_sibling(self) -> Object | None:
        """Previous object below the same parent."""
        if self._hdl.contents.prev_sibling:
            return Object(self._hdl.contents.prev_sibling)
        return None

    @property
    def arity(self) -> int:
        """Number of normal children."""
        return self._hdl.contents.arity

    #   struct hwloc_obj **children;

    @property
    def first_child(self) -> Object | None:
        """First normal child."""
        if self._hdl.contents.first_child:
            return Object(self._hdl.contents.first_child)
        return None

    @property
    def last_child(self) -> Object | None:
        """Last normal child."""
        if self._hdl.contents.last_child:
            return Object(self._hdl.contents.last_child)
        return None

    @property
    def symmetric_subtree(self) -> bool:
        """Set if the subtree of normal objects below this object is symmetric."""
        return bool(self._hdl.contents.symmetric_subtree)

    @property
    def memory_arity(self) -> int:
        """Number of Memory children."""
        return self._hdl.contents.memory_arity

    @property
    def memory_first_child(self) -> Object | None:
        """First Memory child."""
        if self._hdl.contents.memory_first_child:
            return Object(self._hdl.contents.memory_first_child)
        return None

    @property
    def io_arity(self) -> int:
        """Number of I/O children."""
        return self._hdl.contents.io_arity

    @property
    def io_first_child(self) -> Object | None:
        """First I/O child."""
        if self._hdl.contents.io_first_child:
            return Object(self._hdl.contents.io_first_child)
        return None

    @property
    def misc_arity(self) -> int:
        """Number of Misc children."""
        return self._hdl.contents.misc_arity

    @property
    def misc_first_child(self) -> Object | None:
        """First Misc child."""
        if self._hdl.contents.misc_first_child:
            return Object(self._hdl.contents.misc_first_child)
        return None

    @property
    def cpuset(self) -> bitmap_t | None:
        """CPUs covered by this object."""
        return self._hdl.contents.cpuset

    @property
    def complete_cpuset(self) -> bitmap_t | None:
        """The complete CPU set of processors of this object."""
        return self._hdl.contents.complete_cpuset

    @property
    def nodeset(self) -> bitmap_t | None:
        """NUMA nodes covered by this object or containing this object."""
        return self._hdl.contents.nodeset

    @property
    def complete_nodeset(self) -> bitmap_t | None:
        """The complete NUMA node set of this object."""
        return self._hdl.contents.complete_nodeset

    # struct hwloc_infos_s infos
    # void *userdata

    def gp_index(self) -> int:
        "Global persistent index."
        return int(self._hdl.contents.gp_index)

    def iter_children(self) -> Iterator[Object]:
        """Iterate over all children of this object."""
        child = self.first_child
        while child:
            yield child
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

    def get_info_by_name(self, name: str) -> str | None:
        """Get info value by name.

        Parameters
        ----------
        name
            Name of the info to retrieve

        Returns
        -------
        Info value or None if not found
        """
        return _core.obj_get_info_by_name(self._hdl, name)

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
        return ctypes.addressof(self._hdl.contents) == ctypes.addressof(
            other._hdl.contents
        )

    def __hash__(self) -> int:
        """Hash based on pointer address."""
        return hash(ctypes.addressof(self._hdl.contents))
