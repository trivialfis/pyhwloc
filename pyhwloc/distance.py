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
High-level Interface for hwloc Hardware Distance
================================================

This module provides wrappers around hwloc distance matrices.

See `Topology Attributes: Distances, Memory Attributes and CPU Kinds
<https://www.open-mpi.org/projects/hwloc/doc/v2.12.2/topoattrs.html>`__ for an
introduction to the basic concepts.
"""
from __future__ import annotations

import ctypes
import weakref
from typing import TYPE_CHECKING

from .hwloc import core as _core
from .hwobject import Object
from .utils import _reuse_doc

if TYPE_CHECKING:
    from .topology import Topology

__all__ = ["Distances"]


class Distances:
    """High-level interface for hwloc distance matrix."""

    def __init__(
        self, hdl: _core.DistancesPtr, topo: weakref.ReferenceType[Topology]
    ) -> None:
        if not hdl:
            raise ValueError("Distance handle cannot be None")

        self._hdl = hdl
        self._topo_ref = topo

    @property
    def native_handle(self) -> _core.DistancesPtr:
        self._topo  # for validation.
        if not hasattr(self, "_hdl"):
            raise RuntimeError("This distances object has been released.")
        assert self._hdl
        return self._hdl

    @property
    def _topo(self) -> "Topology":
        ref = self._topo_ref()
        if not ref or not ref.is_loaded:
            raise RuntimeError("Topology is invalid")
        return ref

    # Core Properties
    @property
    def objects(self) -> list[Object]:
        """List of objects in this distance matrix."""
        hdl = self.native_handle

        objects = []
        nbobjs = self.nbobjs
        for i in range(nbobjs):
            obj_ptr = hdl.contents.objs[i]
            objects.append(Object(obj_ptr, self._topo_ref))

        return objects

    @property
    @_reuse_doc(_core.distances_get_name)
    def name(self) -> str | None:
        hdl = self.native_handle
        name = _core.distances_get_name(self._topo.native_handle, hdl)
        return name if name else None

    @property
    def nbobjs(self) -> int:
        """Number of objects in this distance matrix."""
        return int(self.native_handle.contents.nbobjs)

    def __setitem__(
        self, key: tuple[int, int] | tuple[Object, Object] | int, value: float
    ) -> None:
        raise RuntimeError("Distance matrices are read-only")

    # Iteration Protocols
    def __str__(self) -> str:
        name = self.name or "<unnamed>"
        return f"Distance matrix '{name}'"

    def __repr__(self) -> str:
        return f"Distance(nbobjs={self.nbobjs}, name={self.name!r})"

    # Comparison and Equality
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Distances):
            return False
        return _core.is_same_obj(self.native_handle, other.native_handle)

    def __hash__(self) -> int:
        if self._hdl is None:
            return hash(None)
        return hash(ctypes.addressof(self._hdl.contents))

    @_reuse_doc(_core.distances_obj_pair_values)
    def get_distance(self, obj1: Object, obj2: Object) -> tuple[float, float]:
        value1to2, value2to1 = _core.distances_obj_pair_values(
            self.native_handle, obj1.native_handle, obj2.native_handle
        )
        return float(value1to2), float(value2to1)

    @_reuse_doc(_core.distances_obj_index)
    def find_object_index(self, obj: Object) -> int:
        return _core.distances_obj_index(self.native_handle, obj.native_handle)

    @property
    def shape(self) -> tuple[int, int]:
        """Shape of the distance matrix (nbobjs, nbobjs)."""
        nbobjs = self.nbobjs  # This already uses native_handle
        return (nbobjs, nbobjs)

    def release(self) -> None:
        # Q: What do we do if the topo is expired?
        #
        # A: The topology class has a cleanup queue for returned distances. It calls
        # this method during its own destruction to make sure no memory is leaked.
        #
        # When the release method is called by this class, the _hdl has already been
        # deleted.
        # The `distances_release` doesn't actually use the topology, but the
        # `distances_release_remove` does. We are doing this workaround just to be safe,
        # in case of the topology is actually used in the future.
        if hasattr(self, "_hdl"):
            # If the _hdl is here, then topology must be valid.
            _core.distances_release(self._topo.native_handle, self._hdl)
            del self._hdl

    def __del__(self) -> None:
        self.release()

    def __copy__(self) -> Distances:
        # There can be only a single owner for the underlying handle.
        raise RuntimeError("The Distance class cannot be copied.")

    def __deepcopy__(self, memo: dict) -> Distances:
        raise RuntimeError("The Distance class cannot be copied.")
