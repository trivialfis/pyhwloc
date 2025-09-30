# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Memory Attributes
=================

This module provides high-level interfaces for hwloc memory attributes.

"""

from __future__ import annotations

import ctypes
from copy import copy
from typing import TYPE_CHECKING, TypeAlias, Union, overload

from .bitmap import Bitmap as _Bitmap
from .hwloc import core as _core
from .hwobject import Object as _Object
from .hwobject import _object
from .utils import _Flags, _or_flags, _reuse_doc, _TopoRefMixin

if TYPE_CHECKING:
    from .utils import _TopoRef

__all__ = [
    "MemAttr",
    "MemAttrs",
    "MemAttrFlag",
    "LocalNumaNodeFlag",
    "MemAttrId",
]

MemAttrFlag: TypeAlias = _core.MemAttrFlag
LocalNumaNodeFlag: TypeAlias = _core.LocalNumaNodeFlag
MemAttrId: TypeAlias = _core.MemAttrId

_Initiator: TypeAlias = Union[_Object, _Bitmap, set[int]]


@overload
def _sched_set(initiator: _Initiator) -> _Bitmap | _Object: ...


@overload
def _sched_set(initiator: None) -> None: ...


def _sched_set(initiator: _Initiator | None) -> _Bitmap | _Object | None:
    """Function to help keep the converted bitmap alive."""
    if isinstance(initiator, set):
        bitmap_ref = _Bitmap.from_sched_set(initiator)
        initiator = bitmap_ref
    return initiator


@overload
def _initiator_loc(initiator: _Initiator) -> _core.Location: ...


@overload
def _initiator_loc(initiator: None) -> None: ...


def _initiator_loc(
    initiator: _Initiator | None,
) -> _core.Location | None:
    if isinstance(initiator, _Object):
        initiator_loc = _core.Location()
        initiator_loc.type = _core.LocationType.OBJECT
        initiator_loc.location = _core.hwloc_location_u()
        initiator_loc.location.object = initiator.native_handle
        return initiator_loc

    if isinstance(initiator, _Bitmap):
        initiator_loc = _core.Location()
        initiator_loc.type = _core.LocationType.CPUSET
        initiator_loc.location = _core.hwloc_location_u()
        initiator_loc.location.cpuset = initiator.native_handle
        return initiator_loc

    if initiator is not None:
        raise TypeError(
            "Invalid initiator, expecting a CPU set or an object, or None, "
            f"got {type(initiator)}."
        )
    return None


class MemAttr(_TopoRefMixin):
    """High-level interface for a single memory attribute.

    Memory attributes describe characteristics like bandwidth, latency, or capacity of
    memory nodes. This class provides methods to query values and find optimal targets
    or initiators for memory operations.

    """

    def __init__(self, attr_id: _core.hwloc_memattr_id_t, topo: _TopoRef) -> None:
        self._attr_id = attr_id
        self._topo_ref = topo

    @property
    def native_handle(self) -> _core.hwloc_memattr_id_t:
        """The memory attribute ID."""
        return self._attr_id

    @property
    @_reuse_doc(_core.memattr_get_name)
    def name(self) -> str:
        """The name of this memory attribute."""
        return _core.memattr_get_name(self._topo.native_handle, self._attr_id)

    @property
    @_reuse_doc(_core.memattr_get_flags)
    def flags(self) -> int:
        """The flags for this memory attribute."""
        return _core.memattr_get_flags(self._topo.native_handle, self._attr_id)

    @property
    def needs_initiator(self) -> bool:
        """The value returned for this memory attribute depends on the given
        initiator. For instance Bandwidth and Latency, but not Capacity.

        """
        return bool(self.flags & _core.MemAttrFlag.NEED_INITIATOR)

    @property
    def higher_first(self) -> bool:
        """The best nodes for this memory attribute are those with the higher
        values. For instance Bandwidth.

        """
        return bool(self.flags & _core.MemAttrFlag.HIGHER_FIRST)

    @property
    def lower_first(self) -> bool:
        """The best nodes for this memory attribute are those with the lower values. For
        instance Latency.

        """
        return bool(self.flags & _core.MemAttrFlag.LOWER_FIRST)

    @_reuse_doc(_core.memattr_get_value)
    def get_value(
        self, target_node: _Object, initiator: _Initiator | None = None
    ) -> int:
        initiator = _sched_set(initiator)
        initiator_loc = _initiator_loc(initiator)
        return _core.memattr_get_value(
            self._topo.native_handle,
            self._attr_id,
            target_node.native_handle,
            ctypes.byref(initiator_loc) if initiator_loc is not None else None,
        )

    @_reuse_doc(_core.memattr_set_value)
    def set_value(
        self,
        target_node: _Object,
        value: int,
        initiator: _Initiator | None = None,
    ) -> None:
        initiator = _sched_set(initiator)
        initiator_loc = _initiator_loc(initiator)
        _core.memattr_set_value(
            self._topo.native_handle,
            self.native_handle,
            target_node.native_handle,
            ctypes.byref(initiator_loc) if initiator_loc is not None else None,
            value,
        )

    @_reuse_doc(_core.memattr_get_best_target)
    def get_best_target(
        self, initiator: _Initiator | None = None
    ) -> tuple[_Object, int]:
        initiator = _sched_set(initiator)
        initiator_loc = _initiator_loc(initiator)
        # ::HWLOC_LOCATION_TYPE_OBJECT is currently unused internally by hwloc
        best_target, value = _core.memattr_get_best_target(
            self._topo.native_handle,
            self._attr_id,
            ctypes.byref(initiator_loc) if initiator_loc is not None else None,
        )

        return _object(best_target, self._topo_ref), value

    @_reuse_doc(_core.memattr_get_best_initiator)
    def get_best_initiator(self, target_node: _Object) -> tuple[_Object | _Bitmap, int]:
        best_initiator, value = _core.memattr_get_best_initiator(
            self._topo.native_handle,
            self._attr_id,
            target_node.native_handle,
        )

        if best_initiator.type == _core.LocationType.OBJECT:
            obj = _object(best_initiator.location.object, self._topo_ref)
            return obj, value
        else:
            bitmap = _Bitmap.from_native_handle(
                best_initiator.location.cpuset, own=False
            )
            return copy(bitmap), value

    @_reuse_doc(_core.memattr_get_targets)
    def get_targets(
        self, initiator: _Initiator | None = None
    ) -> list[tuple[_Object, int]]:
        initiator = _sched_set(initiator)
        initiator_loc = _initiator_loc(initiator)

        # First call to get the number of targets
        nr = ctypes.c_uint(0)
        _core.memattr_get_targets(
            self._topo.native_handle,
            self._attr_id,
            ctypes.byref(initiator_loc) if initiator_loc is not None else None,
            ctypes.byref(nr),
            None,
            None,
        )

        if nr.value == 0:
            return []

        targets_array = (_core.obj_t * nr.value)()
        values_array = (_core.hwloc_uint64_t * nr.value)()

        # Second call to get the actual data
        _core.memattr_get_targets(
            self._topo.native_handle,
            self._attr_id,
            ctypes.byref(initiator_loc) if initiator_loc is not None else None,
            ctypes.byref(nr),
            targets_array,
            values_array,
        )

        result = []
        for i in range(nr.value):
            target_obj = _object(targets_array[i], self._topo_ref)
            value = int(values_array[i])
            result.append((target_obj, value))

        return result

    @_reuse_doc(_core.memattr_get_initiators)
    def get_initiators(
        self,
        target_node: _Object,
    ) -> list[tuple[_Object | _Bitmap, int]]:
        # First call to get the number of initiators
        nrlocs = ctypes.c_uint(0)
        _core.memattr_get_initiators(
            self._topo.native_handle,
            self.native_handle,
            target_node.native_handle,
            ctypes.byref(nrlocs),
            None,
            None,
        )

        if nrlocs.value == 0:
            return []

        # Allocate arrays for initiators and values
        initiators_array = (_core.Location * nrlocs.value)()
        values_array = (_core.hwloc_uint64_t * nrlocs.value)()

        # Second call to get the actual data
        _core.memattr_get_initiators(
            self._topo.native_handle,
            self.native_handle,
            target_node.native_handle,
            ctypes.byref(nrlocs),
            initiators_array,
            values_array,
        )

        result: list[tuple[_Object | _Bitmap, int]] = []
        for i in range(nrlocs.value):
            if initiators_array[i].type == _core.LocationType.OBJECT:
                initiator_obj = _object(
                    initiators_array[i].location.object, self._topo_ref
                )
                value = int(values_array[i])
                result.append((initiator_obj, value))
            else:
                assert initiators_array[i].type == _core.LocationType.CPUSET
                bitmap = _Bitmap.from_native_handle(
                    initiators_array[i].location.cpuset, own=False
                )
                value = int(values_array[i])
                result.append((copy(bitmap), value))

        return result

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"MemAttr({self.name})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MemAttr):
            return False
        return self.native_handle.value == other.native_handle.value


class MemAttrs(_TopoRefMixin):
    """Accessor for memory attributes."""

    def __init__(self, topo: _TopoRef) -> None:
        self._topo_ref = topo

    def get(self, identifier: str | int | _core.MemAttrId) -> MemAttr:
        """Get a memory attribute by name or ID."""
        if isinstance(identifier, str):
            # Look up by name
            attr_id = _core.memattr_get_by_name(
                self._topo.native_handle,
                identifier.encode("utf-8"),
            )
        else:
            # Use as ID directly
            attr_id = int(identifier)

        return MemAttr(_core.hwloc_memattr_id_t(attr_id), self._topo_ref)

    @_reuse_doc(_core.memattr_register)
    def register(self, name: str, flags: _Flags[MemAttrFlag] = 0) -> MemAttr:
        attr_id = _core.memattr_register(
            self._topo.native_handle, name, _or_flags(flags)
        )
        return MemAttr(attr_id, self._topo_ref)

    @_reuse_doc(_core.get_local_numanode_objs)
    def get_local_numa_nodes(
        self, initiator: _Initiator, flags: _Flags[LocalNumaNodeFlag] = 0
    ) -> list[_Object]:
        if initiator is None:
            raise TypeError("Initiator cannot be None")

        # Keep reference to bitmap if we create one
        initiator = _sched_set(initiator)
        initiator_loc = _initiator_loc(initiator)

        # First call to get the number of local nodes
        nr = ctypes.c_uint(0)
        _core.get_local_numanode_objs(
            self._topo.native_handle,
            ctypes.byref(initiator_loc),
            ctypes.byref(nr),
            None,
            _or_flags(flags),
        )

        if nr.value == 0:
            return []

        # Allocate array for nodes
        nodes_array = (_core.obj_t * nr.value)()

        # Second call to get the actual data
        _core.get_local_numanode_objs(
            self._topo.native_handle,
            ctypes.byref(initiator_loc),
            ctypes.byref(nr),
            nodes_array,
            _or_flags(flags),
        )

        result = []
        for i in range(nr.value):
            node_obj = _object(nodes_array[i], self._topo_ref)
            result.append(node_obj)

        return result
