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


class Object:
    """High-level interface for the hwloc object.

    Parameters
    ----------
    hdl
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
        """Get the object type."""
        return ObjType(self._hdl.contents.type)

    @property
    def subtype(self) -> str | None:
        """Get the object subtype string."""
        if self._hdl.contents.subtype:
            return self._hdl.contents.subtype.decode("utf-8")
        return None

    @property
    def os_index(self) -> int:
        """Get the OS index of this object."""
        return self._hdl.contents.os_index

    @property
    def name(self) -> str | None:
        """Get the object name."""
        if self._hdl.contents.name:
            return self._hdl.contents.name.decode("utf-8")
        return None

    @property
    def total_memory(self) -> int:
        """Get the total memory in bytes for this object."""
        return self._hdl.contents.total_memory

    @property
    def depth(self) -> int:
        """Get the depth of this object in the topology tree."""
        return self._hdl.contents.depth

    @property
    def logical_index(self) -> int:
        """Get the logical index of this object."""
        return self._hdl.contents.logical_index

    @property
    def sibling_rank(self) -> int:
        """Get the rank of this object among its siblings."""
        return self._hdl.contents.sibling_rank

    @property
    def arity(self) -> int:
        """Get the number of children of this object."""
        return self._hdl.contents.arity

    @property
    def memory_arity(self) -> int:
        """Get the number of memory children of this object."""
        return self._hdl.contents.memory_arity

    @property
    def io_arity(self) -> int:
        """Get the number of I/O children of this object."""
        return self._hdl.contents.io_arity

    @property
    def misc_arity(self) -> int:
        """Get the number of misc children of this object."""
        return self._hdl.contents.misc_arity

    @property
    def symmetric_subtree(self) -> bool:
        """Check if the subtree rooted at this object is symmetric."""
        return bool(self._hdl.contents.symmetric_subtree)

    @property
    def cpuset(self) -> bitmap_t | None:
        """Get the CPU set for this object."""
        return self._hdl.contents.cpuset

    @property
    def complete_cpuset(self) -> bitmap_t | None:
        """Get the complete CPU set for this object."""
        return self._hdl.contents.complete_cpuset

    @property
    def nodeset(self) -> bitmap_t | None:
        """Get the NUMA node set for this object."""
        return self._hdl.contents.nodeset

    @property
    def complete_nodeset(self) -> bitmap_t | None:
        """Get the complete NUMA node set for this object."""
        return self._hdl.contents.complete_nodeset

    @property
    def parent(self) -> Object | None:
        """Get the parent object."""
        if self._hdl.contents.parent:
            return Object(self._hdl.contents.parent)
        return None

    @property
    def next_sibling(self) -> Object | None:
        """Get the next sibling object."""
        if self._hdl.contents.next_sibling:
            return Object(self._hdl.contents.next_sibling)
        return None

    @property
    def prev_sibling(self) -> Object | None:
        """Get the previous sibling object."""
        if self._hdl.contents.prev_sibling:
            return Object(self._hdl.contents.prev_sibling)
        return None

    @property
    def next_cousin(self) -> Object | None:
        """Get the next cousin object."""
        if self._hdl.contents.next_cousin:
            return Object(self._hdl.contents.next_cousin)
        return None

    @property
    def prev_cousin(self) -> Object | None:
        """Get the previous cousin object."""
        if self._hdl.contents.prev_cousin:
            return Object(self._hdl.contents.prev_cousin)
        return None

    @property
    def first_child(self) -> Object | None:
        """Get the first child object."""
        if self._hdl.contents.first_child:
            return Object(self._hdl.contents.first_child)
        return None

    @property
    def last_child(self) -> Object | None:
        """Get the last child object."""
        if self._hdl.contents.last_child:
            return Object(self._hdl.contents.last_child)
        return None

    @property
    def memory_first_child(self) -> Object | None:
        """Get the first memory child object."""
        if self._hdl.contents.memory_first_child:
            return Object(self._hdl.contents.memory_first_child)
        return None

    @property
    def io_first_child(self) -> Object | None:
        """Get the first I/O child object."""
        if self._hdl.contents.io_first_child:
            return Object(self._hdl.contents.io_first_child)
        return None

    @property
    def misc_first_child(self) -> Object | None:
        """Get the first misc child object."""
        if self._hdl.contents.misc_first_child:
            return Object(self._hdl.contents.misc_first_child)
        return None

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
        current = self
        while current.prev_sibling:
            current = current.prev_sibling

        # Iterate through all siblings
        while current:
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

    def add_info(self, name: str, value: str) -> None:
        """Add info to this object.

        Parameters
        ----------
        name
            Name of the info
        value
            Value of the info
        """
        _core.obj_add_info(self._hdl, name, value)

    def __str__(self) -> str:
        """String representation of the object."""
        type_name = self.type.name.replace("HWLOC_OBJ_", "")
        parts = [f"{type_name}#{self.logical_index}"]

        if self.name:
            parts.append(f"({self.name})")
        if self.subtype:
            parts.append(f"[{self.subtype}]")

        return " ".join(parts)

    def __repr__(self) -> str:
        """Detailed representation of the object."""
        return f"Object(type={self.type.name}, logical_index={self.logical_index}, depth={self.depth})"

    def __eq__(self, other: object) -> bool:
        """Check equality based on pointer address."""
        if not isinstance(other, Object):
            return False
        return ctypes.addressof(self._hdl.contents) == ctypes.addressof(other._hdl.contents)

    def __hash__(self) -> int:
        """Hash based on pointer address."""
        return hash(ctypes.addressof(self._hdl.contents))
