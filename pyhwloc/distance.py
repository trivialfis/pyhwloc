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
"""High-level interface for hwloc hardware distance functionality.

This module provides Pythonic wrappers around hwloc distance matrices,
making it easier to work with hardware topology distance information.

See `Topology Attributes: Distances, Memory Attributes and CPU Kinds
<https://www.open-mpi.org/projects/hwloc/doc/v2.12.2/topoattrs.html>`__ for an
introduction to the basic concepts.
"""
from __future__ import annotations

import ctypes
import weakref
from typing import TYPE_CHECKING, Iterator, Sequence

from .hwloc import core as _core
from .hwobject import Object

if TYPE_CHECKING:
    from .topology import Topology

__all__ = ["Distance", "Kind", "Transform", "AddFlag"]


# Type aliases for distance-related enums
Kind = _core.hwloc_distances_kind_e
Transform = _core.hwloc_distances_transform_e
AddFlag = _core.hwloc_distances_add_flag_e


class Distance:
    """High-level interface for hwloc distance matrix.

    Provides a Pythonic wrapper around hwloc_distances_s structure with
    automatic memory management, matrix-like access, and integration with
    the Object and Topology classes.

    Parameters
    ----------
    handle
        Raw pointer to hwloc_distances_s structure
    topology
        Topology instance that owns this distance matrix

    Examples
    --------
    >>> with Topology.from_synthetic("node:2 core:2") as topo:
    ...     distances = topo.get_distances()
    ...     if distances:
    ...         matrix = distances[0]
    ...         print(f"Distance matrix: {matrix.name}")
    ...         print(f"Objects: {len(matrix.objects)}")
    ...         # Access distance between first two objects
    ...         if len(matrix.objects) >= 2:
    ...             dist = matrix[0, 1]  # or matrix[obj1, obj2]
    """

    def __init__(
        self, hdl: _core.DistancesPtr, topo: weakref.ReferenceType[Topology]
    ) -> None:
        """Initialize Distance matrix wrapper.

        Parameters
        ----------
        hdl
            Raw pointer to hwloc_distances_s structure
        topo
            Weak reference to topology instance for object creation and validation

        Raises
        ------
        ValueError
            If handle is None or invalid
        RuntimeError
            If topology is not loaded or has been destroyed
        """
        if hdl is None:
            raise ValueError("Distance handle cannot be None")

        self._hdl = hdl
        self._topo_ref = topo

    @property
    def native_handle(self) -> _core.DistancesPtr:
        if not self._topo_ref or not self._topo_ref().is_loaded:  # type: ignore
            raise RuntimeError("Topology is invalid")
        assert self._hdl
        return self._hdl

    @property
    def _topo(self) -> "Topology":
        if not self._topo_ref or not self._topo_ref().is_loaded:  # type: ignore
            raise RuntimeError("Topology is invalid")
        v = self._topo_ref()
        assert v is not None
        return v

    # Core Properties
    @property
    def objects(self) -> list[Object]:
        """List of objects in this distance matrix."""
        handle = self.native_handle  # This performs all validation

        objects = []
        nbobjs = handle.contents.nbobjs
        for i in range(nbobjs):
            obj_ptr = handle.contents.objs[i]
            objects.append(Object(obj_ptr, self._topo_ref))

        return objects

    @property
    def values(self) -> Sequence[float]:
        """Distance values as a flat sequence (row-major order)."""
        handle = self.native_handle  # This performs all validation

        nbobjs = handle.contents.nbobjs
        total_values = nbobjs * nbobjs
        values_ptr = handle.contents.values

        return [float(values_ptr[i]) for i in range(total_values)]

    @property
    def kind(self) -> Kind:
        """Kind of distance (latency, bandwidth, hops, etc.)."""
        assert False, "kind is or'd"
        return self.native_handle.contents.kind
        return Kind(self.native_handle.contents.kind)

    @property
    def name(self) -> str | None:
        """Name of this distance matrix, if any."""
        handle = self.native_handle  # This performs all validation
        topology = self._topo_ref()  # We know it's valid from native_handle

        name = _core.distances_get_name(topology.native_handle, handle)  # type: ignore[union-attr]
        return name if name else None

    @property
    def nbobjs(self) -> int:
        """Number of objects in this distance matrix."""
        return int(self.native_handle.contents.nbobjs)

    # Matrix Access Interface
    def __getitem__(self, key: tuple[int, int] | tuple[Object, Object] | int) -> float:
        """Get distance value by matrix coordinates or objects.

        Parameters
        ----------
        key
            Matrix coordinates (i, j), object pair, or flat index

        Returns
        -------
        Distance value

        Examples
        --------
        >>> matrix[0, 1]  # Distance from object 0 to object 1
        >>> matrix[obj1, obj2]  # Distance between two objects
        >>> matrix[5]  # Flat index access
        """
        handle = self.native_handle  # This performs all validation

        if isinstance(key, tuple) and len(key) == 2:
            i, j = key

            # Handle Object instances
            if isinstance(i, Object):
                i = self.find_object_index(i)
                if i == -1:
                    raise ValueError("First object not found in distance matrix")

            if isinstance(j, Object):
                j = self.find_object_index(j)
                if j == -1:
                    raise ValueError("Second object not found in distance matrix")

            # Convert to flat index
            nbobjs = self.nbobjs
            if not (0 <= i < nbobjs and 0 <= j < nbobjs):
                raise IndexError(
                    f"Index ({i}, {j}) out of bounds for matrix of size {nbobjs}x{nbobjs}"
                )

            flat_index = i * nbobjs + j

        elif isinstance(key, int):
            flat_index = key
            total_values = self.nbobjs**2
            if not (0 <= flat_index < total_values):
                raise IndexError(
                    f"Flat index {flat_index} out of bounds for matrix with {total_values} values"
                )

        else:
            raise TypeError("Key must be (i, j) tuple, (Object, Object) tuple, or int")

        return float(handle.contents.values[flat_index])

    def __setitem__(
        self, key: tuple[int, int] | tuple[Object, Object] | int, value: float
    ) -> None:
        """Set distance value (if matrix is modifiable)."""
        # For now, we'll make distance matrices read-only since hwloc
        # distance matrices are typically provided by the system
        raise NotImplementedError("Distance matrices are read-only")

    # Iteration Protocols
    def __iter__(self) -> Iterator[Object]:
        """Iterate over objects in the distance matrix."""
        return iter(self.objects)

    def __len__(self) -> int:
        """Number of objects in the distance matrix."""
        return self.nbobjs

    def __str__(self) -> str:
        name = self.name or "<unnamed>"
        return f"Distance matrix '{name}' ({self.nbobjs} objects, kind={self.kind})"

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"Distance(nbobjs={self.nbobjs}, kind={self.kind}, name={self.name!r})"

    # Comparison and Equality
    def __eq__(self, other: object) -> bool:
        """Check equality based on handle address."""
        if not isinstance(other, Distance):
            return False
        return (
            self._hdl is not None
            and other._hdl is not None
            and ctypes.addressof(self._hdl.contents)
            == ctypes.addressof(other._hdl.contents)
        )

    def __hash__(self) -> int:
        """Hash based on handle address."""
        if self._hdl is None:
            return hash(None)
        return hash(ctypes.addressof(self._hdl.contents))

    # Helper Methods
    def get_distance(self, obj1: Object, obj2: Object) -> tuple[float, float]:
        """Get bidirectional distance between two objects.

        Parameters
        ----------
        obj1, obj2
            Objects to get distance between

        Returns
        -------
        Distance from obj1 to obj2, and obj2 to obj1
        """
        handle = self.native_handle  # This performs all validation

        # Use the core helper function for efficiency
        try:
            value1to2, value2to1 = _core.distances_obj_pair_values(
                handle, obj1.native_handle, obj2.native_handle
            )
            return (float(value1to2), float(value2to1))
        except Exception:
            raise ValueError("Objects not found in distance matrix or error occurred")

    def find_object_index(self, obj: Object) -> int:
        """Find index of object in distance matrix.

        Parameters
        ----------
        obj
            Object to find

        Returns
        -------
        Index of object, or -1 if not found
        """
        return _core.distances_obj_index(self.native_handle, obj.native_handle)

    # Transformation Methods
    def transform(self, transform_type: Transform, **kwargs: object) -> None:
        """Apply transformation to distance matrix.

        Parameters
        ----------
        transform_type
            Type of transformation to apply
        **kwargs
            Additional transformation parameters
        """
        handle = self.native_handle  # This performs all validation
        topology = self._topo_ref()  # We know it's valid from native_handle

        _core.distances_transform(
            topology.native_handle,  # type: ignore[union-attr]
            handle,
            transform_type,
            ctypes.c_void_p(0),  # transform_attr (not used for basic transforms)
            0,  # flags
        )

    @property
    def shape(self) -> tuple[int, int]:
        """Shape of the distance matrix (nbobjs, nbobjs)."""
        nbobjs = self.nbobjs  # This already uses native_handle
        return (nbobjs, nbobjs)

    def release(self) -> None:
        if hasattr(self, "_hdl"):
            # fixme: what do we do if the topo is expired?
            # topo is not used in the release call (used by the release_remove, though).
            _core.distances_release(None, self._hdl)
            del self._hdl

    def __copy__(self) -> Distance:
        # There can be only a single owner for the underlying handle.
        raise RuntimeError("The Distance class cannot be copied.")

    def __deepcopy__(self, memo: dict) -> Distance:
        raise RuntimeError("The Distance class cannot be copied.")
