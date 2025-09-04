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
import ctypes

import pytest

from pyhwloc.core import (  # _obj_t_get_cpuset,
    HwLocError,
    _free,
    bitmap_asprintf,
    bitmap_dup,
    bitmap_free,
    bitmap_singlify,
    compare_types,
    get_api_version,
    get_depth_type,
    get_memory_parents_depth,
    get_nbobjs_by_depth,
    get_nbobjs_by_type,
    get_next_obj_by_depth,
    get_next_obj_by_type,
    get_obj_by_depth,
    get_obj_by_type,
    get_root_obj,
    get_type_depth,
    get_type_or_above_depth,
    get_type_or_below_depth,
    hwloc_get_type_depth_e,
    hwloc_obj_type_t,
    hwloc_type_filter_e,
    set_cpubind,
    topology_abi_check,
    topology_check,
    topology_destroy,
    topology_dup,
    topology_get_depth,
    topology_get_infos,
    topology_init,
    topology_load,
    topology_set_io_types_filter,
    topology_t,
)


def test_get_api_version() -> None:
    version = get_api_version()
    assert isinstance(version, int)
    assert version > 0


##############
# Object Types
##############


def test_compare_types() -> None:
    # Test equal types
    r = compare_types(hwloc_obj_type_t.HWLOC_OBJ_CORE, hwloc_obj_type_t.HWLOC_OBJ_CORE)
    assert r == 0
    r = compare_types(hwloc_obj_type_t.HWLOC_OBJ_PU, hwloc_obj_type_t.HWLOC_OBJ_PU)
    assert r == 0

    r = compare_types(
        hwloc_obj_type_t.HWLOC_OBJ_MACHINE, hwloc_obj_type_t.HWLOC_OBJ_CORE
    )
    assert r != 0
    r = compare_types(
        hwloc_obj_type_t.HWLOC_OBJ_CORE, hwloc_obj_type_t.HWLOC_OBJ_MACHINE
    )
    assert r != 0


###################################
# Topology Creation and Destruction
###################################


class Topology:
    def __init__(self, filters: list[hwloc_type_filter_e] = []) -> None:
        self.hdl = topology_t()
        topology_init(self.hdl)
        if filters:
            for f in filters:
                topology_set_io_types_filter(self.hdl, f)
        topology_load(self.hdl)

    def __del__(self) -> None:
        topology_destroy(self.hdl)


def test_topology_init() -> None:
    hdl = topology_t()
    topology_init(hdl)
    topology_load(hdl)
    topology_check(hdl)
    topology_abi_check(hdl)
    topology_destroy(hdl)


def test_topology_dup() -> None:
    topo = Topology()
    depth_0 = topology_get_depth(topo.hdl)
    new = topology_dup(topo.hdl)
    depth_1 = topology_get_depth(topo.hdl)
    assert depth_0 == depth_1
    topology_destroy(new)


def test_topology_get_depth() -> None:
    topo = Topology()
    depth = topology_get_depth(topo.hdl)
    assert depth >= 0
    for d in range(depth):
        n_objs = get_nbobjs_by_depth(topo.hdl, d)
        assert n_objs >= 0


def test_topology_get_infos() -> None:
    topo = topology_t()
    topology_init(topo)

    topology_set_io_types_filter(
        topo, hwloc_type_filter_e.HWLOC_TYPE_FILTER_KEEP_IMPORTANT
    )
    topology_load(topo)

    infos = topology_get_infos(topo)

    cnt = infos.contents.count
    assert cnt > 0
    names = [infos.contents.array[i].name for i in range(cnt)]
    assert b"OSName" in names

    topology_destroy(topo)


def test_error() -> None:
    with pytest.raises(HwLocError, match="error:"):
        topo = Topology()
        topology_set_io_types_filter(
            topo.hdl, hwloc_type_filter_e.HWLOC_TYPE_FILTER_KEEP_IMPORTANT
        )


#################################
# Object levels, depths and types
#################################


def test_get_type_depth() -> None:
    topo = Topology()

    # Test common object types
    machine_depth = get_type_depth(topo.hdl, hwloc_obj_type_t.HWLOC_OBJ_MACHINE)
    assert machine_depth == 0

    pu_depth = get_type_depth(topo.hdl, hwloc_obj_type_t.HWLOC_OBJ_PU)
    # PU should typically be at the deepest level
    assert pu_depth > 0

    total_depth = topology_get_depth(topo.hdl)
    assert pu_depth < total_depth


def test_get_depth_type() -> None:
    topo = Topology()
    total_depth = topology_get_depth(topo.hdl)

    # Test each depth level
    for depth in range(total_depth):
        obj_type = get_depth_type(topo.hdl, depth)
        assert isinstance(obj_type, hwloc_obj_type_t)
        assert obj_type >= 0

        # Roundtrip
        type_depth = get_type_depth(topo.hdl, obj_type)
        if type_depth >= 0:  # Skip special depth values
            assert type_depth == depth


def test_get_nbobjs_by_depth() -> None:
    topo = Topology()
    total_depth = topology_get_depth(topo.hdl)

    # Test each depth level
    for depth in range(total_depth):
        n_objs = get_nbobjs_by_depth(topo.hdl, depth)
        assert n_objs > 0  # Each level should have at least one object

        # Verify we can actually get objects at this depth
        obj = get_obj_by_depth(topo.hdl, depth, 0)
        assert obj is not None
        assert obj.contents.depth == depth

    # Test invalid depth
    invalid_depth = total_depth + 10
    n_objs = get_nbobjs_by_depth(topo.hdl, invalid_depth)
    assert n_objs == 0


def test_get_type_or_above_depth() -> None:
    topo = Topology()

    # Test with common types
    core_depth = get_type_or_above_depth(topo.hdl, hwloc_obj_type_t.HWLOC_OBJ_CORE)
    assert core_depth > 0
    # Should be a valid depth
    total_depth = topology_get_depth(topo.hdl)
    assert core_depth < total_depth

    obj_type = get_depth_type(topo.hdl, core_depth)
    assert obj_type == hwloc_obj_type_t.HWLOC_OBJ_CORE


def test_get_type_or_below_depth() -> None:
    topo = Topology()

    # Test with machine type - should find machine or something below it
    machine_depth = get_type_or_below_depth(
        topo.hdl, hwloc_obj_type_t.HWLOC_OBJ_MACHINE
    )
    assert machine_depth >= 0  # Should always find something

    # Test with core type
    core_depth = get_type_or_below_depth(topo.hdl, hwloc_obj_type_t.HWLOC_OBJ_CORE)
    assert core_depth > 0
    total_depth = topology_get_depth(topo.hdl)
    assert core_depth < total_depth

    # The returned depth should contain objects of the requested type or below
    obj_type = get_depth_type(topo.hdl, core_depth)
    assert obj_type == hwloc_obj_type_t.HWLOC_OBJ_CORE


def test_get_memory_parents_depth() -> None:
    topo = Topology()

    mem_depth = get_memory_parents_depth(topo.hdl)
    assert mem_depth >= 0
    total_depth = topology_get_depth(topo.hdl)
    assert mem_depth < total_depth


def test_depth_consistency() -> None:
    topo = Topology()
    total_depth = topology_get_depth(topo.hdl)

    # Test that get_type_depth and get_depth_type are consistent
    for depth in range(total_depth):
        obj_type = get_depth_type(topo.hdl, depth)
        type_depth = get_type_depth(topo.hdl, obj_type)

        # If type_depth is a normal depth (not special value), it should match
        if type_depth >= 0:
            assert type_depth == depth


def find_numa_depth() -> int:
    topo = Topology()
    for depth in range(10):  # reasonable upper limit
        if get_nbobjs_by_depth(topo.hdl, depth) > 0:
            obj = get_obj_by_depth(topo.hdl, depth, 0)
            if obj and obj.contents.type == hwloc_obj_type_t.HWLOC_OBJ_NUMANODE:
                numa_depth = depth
                break
    return numa_depth


def test_example() -> None:
    topo = Topology()

    depth = get_type_or_below_depth(topo.hdl, hwloc_obj_type_t.HWLOC_OBJ_CORE)

    obj = get_obj_by_depth(topo.hdl, depth, get_nbobjs_by_depth(topo.hdl, depth) - 1)
    if obj:
        # Get a copy of its cpuset that we may modify.
        cpuset = bitmap_dup(obj.contents.cpuset)

        # Get only one logical processor (in case the core is SMT/hyper-threaded).
        bitmap_singlify(cpuset)

        # And try to bind ourself there
        set_cpubind(topo.hdl, cpuset, 0)
        bitmap_str = ctypes.c_char_p()
        # int error = errno;
        bitmap_asprintf(ctypes.byref(bitmap_str), obj.contents.cpuset)
        print(bitmap_str.value)
        # printf("Couldn't bind to cpuset %s: %s\n", str, strerror(error));
        _free(bitmap_str)

        # Free our cpuset copy
        bitmap_free(cpuset)
