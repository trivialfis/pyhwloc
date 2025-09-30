# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause

####################################
# Retrieve distances between objects
####################################

from __future__ import annotations

import ctypes
from functools import partial

from pyhwloc.hwloc.core import (
    Distances,
    DistancesAddFlag,
    DistancesKind,
    Obj,
    ObjType,
    distances_add_commit,
    distances_add_create,
    distances_add_values,
    distances_get,
    distances_get_by_type,
    distances_obj_index,
    distances_obj_pair_values,
    distances_release_remove,
    get_obj_by_type,
    hwloc_uint64_t,
    topology_destroy,
    topology_get_depth,
    topology_init,
    topology_load,
    topology_refresh,
    topology_set_synthetic,
    topology_t,
)


def _ravel(n_objs: int, i: int, j: int) -> int:
    return i * n_objs + j


def test_distances_comprehensive() -> None:
    """A test adopted from the `tests/hwloc/hwloc_distances.c`"""
    # Initialize topology
    topo = topology_t()
    topology_init(topo)
    n_nodes = 4
    _r = partial(_ravel, n_nodes)
    topology_set_synthetic(topo, f"node:{n_nodes} core:4 pu:1")
    topology_load(topo)

    # Arrays for objects and distance values
    distances = ctypes.POINTER(Distances)()
    objs = (ctypes.POINTER(Obj) * n_nodes)()
    values = (hwloc_uint64_t * (n_nodes**2))()

    # Initial check - should have no distances
    nr = ctypes.c_uint(0)
    distances_get(
        topo,
        ctypes.byref(nr),
        ctypes.byref(distances),
        0,
    )
    # Not distance
    assert nr.value == 0
    # Inserting NUMA distances

    # Get NUMA node objects
    for i in range(n_nodes):
        obj = get_obj_by_type(topo, ObjType.NUMANODE, i)
        assert obj is not None
        objs[i] = obj

    # Create distance matrix - initialize all to 8
    for i in range(n_nodes * n_nodes):
        values[i] = 8

    # Set specific values for 2x2 matrix pattern
    values[_r(1, 0)] = 4
    values[_r(0, 1)] = 4
    values[_r(3, 2)] = 4
    values[_r(2, 3)] = 4

    # Set diagonal values to 1
    for i in range(n_nodes):
        values[_r(i, i)] = 1

    # Create distance handle
    kind = DistancesKind.VALUE_LATENCY | DistancesKind.FROM_USER
    # no name
    handle = distances_add_create(topo, "", kind)
    assert handle

    # Add distance values to the handle
    distances_add_values(
        topo,
        handle,
        n_nodes,
        objs,
        values,
    )
    # Group the objects based on distance.
    distances_add_commit(topo, handle, DistancesAddFlag.GROUP)
    # Refresh topology
    topology_refresh(topo)
    # Check topology depth
    topodepth = topology_get_depth(topo)
    assert topodepth == 5

    # Checking NUMA distances
    # Get NUMA distances
    nr = ctypes.c_uint(1)
    distances_get_by_type(
        topo,
        ObjType.NUMANODE,
        ctypes.byref(nr),
        ctypes.byref(distances),
        kind=0,
    )

    assert nr.value == 1
    assert distances and distances.contents.objs and distances.contents.values
    assert distances.contents.kind == kind

    # Test helper functions
    numa_node_2 = get_obj_by_type(topo, ObjType.NUMANODE, 2)
    assert numa_node_2 is not None
    index = distances_obj_index(distances[0], numa_node_2)
    assert index == 2

    # Test distance pair values
    numa_node_1 = get_obj_by_type(topo, ObjType.NUMANODE, 1)
    assert numa_node_1 is not None
    value1to2, value2to1 = distances_obj_pair_values(
        distances,
        numa_node_1,
        numa_node_2,
    )
    assert value1to2 == values[_r(1, 2)]
    assert value2to1 == values[_r(2, 1)]

    # Test error cases - PU objects should not be in NUMA distance matrix
    pu_obj = get_obj_by_type(topo, ObjType.PU, 0)
    assert pu_obj is not None
    pu_index = distances_obj_index(distances[0], pu_obj)
    assert pu_index == -1, "PU object should not be in NUMA distances."

    dist_values = distances.contents.values
    # Diagonal
    assert dist_values[_r(0, 0)] == 1
    assert dist_values[_r(2, 2)] == 1
    # Set values
    assert dist_values[_r(1, 0)] == 4
    assert dist_values[_r(3, 2)] == 4
    # Default
    assert dist_values[_r(1, 4)] == 8
    assert dist_values[_r(2, 1)] == 8

    distances_release_remove(topo, distances)
    topology_destroy(topo)
