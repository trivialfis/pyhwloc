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

from pyhwloc.core import (
    HwLocError,
    _free,
    bitmap_alloc,
    bitmap_asprintf,
    bitmap_dup,
    bitmap_free,
    bitmap_set,
    bitmap_singlify,
    bridge_covers_pcibus,
    compare_types,
    cpukinds_get_by_cpuset,
    cpukinds_get_info,
    cpukinds_get_nr,
    cpukinds_register,
    get_api_version,
    get_depth_type,
    get_memory_parents_depth,
    get_nbobjs_by_depth,
    get_next_bridge,
    get_obj_by_depth,
    get_root_obj,
    get_type_depth,
    get_type_or_above_depth,
    get_type_or_below_depth,
    hwloc_info_s,
    hwloc_infos_s,
    hwloc_obj_attr_u,
    hwloc_obj_type_t,
    hwloc_topology_export_xml_flags_e,
    hwloc_type_filter_e,
    obj_attr_snprintf,
    obj_type_snprintf,
    set_cpubind,
    topology_abi_check,
    topology_check,
    topology_destroy,
    topology_dup,
    topology_export_xmlbuffer,
    topology_get_depth,
    topology_get_infos,
    topology_init,
    topology_load,
    topology_set_io_types_filter,
    topology_t,
    type_sscanf,
    type_sscanf_as_depth,
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


def test_get_root_obj() -> None:
    """Test the get_root_obj function. Some additional checks for exposed structs."""
    topo = Topology()

    # Get the root object
    root_obj = get_root_obj(topo.hdl)

    # Root object should not be None
    assert root_obj is not None

    # Root object should be at depth 0
    assert root_obj.contents.depth == 0

    # Root object should be of type MACHINE
    assert root_obj.contents.type == hwloc_obj_type_t.HWLOC_OBJ_MACHINE

    buf = ctypes.create_string_buffer(1024)
    length = obj_type_snprintf(buf, 256, root_obj, 1)
    assert buf.value.decode("utf-8") == "Machine" and len("Machine") == length
    obj_attr_snprintf(buf, 1024, root_obj, b"\n", 1)
    assert buf.value.decode("utf-8").find("DMIChassisType") != -1

    # Root object should have no parent
    parent = ctypes.cast(root_obj.contents.parent, ctypes.c_void_p)
    assert parent.value is None

    # Root object should be the same as getting object at depth 0, index 0
    depth_0_obj = get_obj_by_depth(topo.hdl, 0, 0)
    assert depth_0_obj is not None
    assert root_obj.contents.type == depth_0_obj.contents.type
    assert root_obj.contents.depth == depth_0_obj.contents.depth

    # Root should have children (unless it's a very simple topology)
    total_depth = topology_get_depth(topo.hdl)
    if total_depth > 1:
        assert root_obj.contents.arity > 0
        assert root_obj.contents.first_child is not None

        # First child should have root as parent
        first_child = root_obj.contents.first_child
        assert (
            ctypes.cast(root_obj, ctypes.c_void_p).value
            == ctypes.cast(first_child.contents.parent, ctypes.c_void_p).value
        )

    # Root object should have valid cpuset and nodeset
    assert root_obj.contents.cpuset is not None
    assert root_obj.contents.nodeset is not None


#############################################################
# Converting between Object Types and Attributes, and Strings
#############################################################


def test_type_sscanf_functions() -> None:
    topo = Topology()

    # Test parsing basic object type strings
    test_cases = ["Machine", "Package", "Core", "PU", "L1Cache", "L2Cache", "L3Cache"]

    for type_str in test_cases:
        # Test type_sscanf without attributes
        obj_type, attr = type_sscanf(type_str)
        assert isinstance(obj_type, hwloc_obj_type_t)
        assert attr is not None
        # The depth should be reliable. Other info like size is set to 0 for some reason
        if obj_type == hwloc_obj_type_t.HWLOC_OBJ_L1CACHE:
            assert attr.cache.depth == 1
        if obj_type == hwloc_obj_type_t.HWLOC_OBJ_L2CACHE:
            assert attr.cache.depth == 2
        if obj_type == hwloc_obj_type_t.HWLOC_OBJ_L3CACHE:
            assert attr.cache.depth == 3
        # Test type_sscanf_as_depth
        obj_type_depth, depth = type_sscanf_as_depth(type_str, topo.hdl)
        assert isinstance(obj_type_depth, hwloc_obj_type_t)
        assert isinstance(depth, int)

        assert obj_type == obj_type_depth

    # Test invalid string
    with pytest.raises(HwLocError):
        type_sscanf("FooBar")


def test_hwloc_obj_attr_u_union() -> None:
    # Test creating and accessing the union
    attr_union = hwloc_obj_attr_u()

    # Test cache attributes
    attr_union.cache.size = 32768  # 32KB cache
    attr_union.cache.depth = 1  # L1 cache
    attr_union.cache.linesize = 64  # 64-byte cache lines
    attr_union.cache.associativity = 8  # 8-way associative
    attr_union.cache.type = 0  # hwloc_obj_cache_type_t.HWLOC_OBJ_CACHE_UNIFIED

    assert attr_union.cache.size == 32768
    assert attr_union.cache.depth == 1
    assert attr_union.cache.linesize == 64
    assert attr_union.cache.associativity == 8
    assert attr_union.cache.type == 0

    # Test PCI device attributes
    attr_union.pcidev.domain = 0
    attr_union.pcidev.bus = 1
    attr_union.pcidev.dev = 0
    attr_union.pcidev.func = 0
    attr_union.pcidev.vendor_id = 0x10DE  # NVIDIA
    attr_union.pcidev.device_id = 0x1234
    attr_union.pcidev.class_id = 0x0300  # Display controller

    assert attr_union.pcidev.domain == 0
    assert attr_union.pcidev.bus == 1
    assert attr_union.pcidev.dev == 0
    assert attr_union.pcidev.func == 0
    assert attr_union.pcidev.vendor_id == 0x10DE
    assert attr_union.pcidev.device_id == 0x1234
    assert attr_union.pcidev.class_id == 0x0300


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


#####################
# Finding I/O objects
#####################


def test_bridge_covers_pcibus() -> None:
    """Test the bridge_covers_pcibus function."""
    # Create a topology with I/O devices enabled
    topo = Topology([hwloc_type_filter_e.HWLOC_TYPE_FILTER_KEEP_IMPORTANT])

    # Use prev=None to find the first bridge.
    bridge = get_next_bridge(topo.hdl, None)
    assert bridge is not None

    # Test with bridge attributes if the bridge has PCI attributes
    assert bridge.contents.attr
    bridge_attr = bridge.contents.attr.contents
    assert bridge_attr.bridge.depth >= 0

    # Test that a bridge covers its own bus range
    # For a valid bridge, it should cover some bus range
    result = bridge_covers_pcibus(bridge, 0, 0)
    assert isinstance(result, int)

    # Test with clearly invalid domain/bus combinations
    result_invalid = bridge_covers_pcibus(bridge, 0xFFFF, 0xFFFF)
    assert isinstance(result_invalid, int)


def test_topology_export_xmlbuffer() -> None:
    topo = Topology()
    result = topology_export_xmlbuffer(
        topo.hdl, hwloc_topology_export_xml_flags_e.HWLOC_TOPOLOGY_EXPORT_XML_FLAG_V2
    )
    assert """<!DOCTYPE topology SYSTEM "hwloc2.dtd">""" in result


####################
# Kinds of CPU cores
####################


def test_cpukinds_get_info() -> None:
    """Test the cpukinds_get_nr function."""
    topo = Topology()

    nr_kinds = cpukinds_get_nr(topo.hdl, 0)
    assert isinstance(nr_kinds, int)
    assert nr_kinds >= 0


def test_cpukinds_register_and_get_functions() -> None:
    topo = Topology()

    # Get initial number of CPU kinds
    initial_nr_kinds = cpukinds_get_nr(topo.hdl, 0)

    # Create a test cpuset (use first CPU)
    test_cpuset = bitmap_alloc()
    bitmap_set(test_cpuset, 0)  # Set CPU 0

    # Create test info
    test_info = hwloc_info_s()
    test_info.name = b"TestCPUKind"
    test_info.value = b"TestValue"

    infos = hwloc_infos_s()
    infos.array = ctypes.pointer(test_info)
    infos.count = 1

    # Register a new CPU kind
    cpukinds_register(topo.hdl, test_cpuset, 100, infos)

    # Verify the number of kinds increased
    new_nr_kinds = cpukinds_get_nr(topo.hdl, 0)
    assert new_nr_kinds == initial_nr_kinds + 1

    # Test cpukinds_get_by_cpuset
    kind_index = cpukinds_get_by_cpuset(topo.hdl, test_cpuset, 0)
    assert isinstance(kind_index, int)
    assert kind_index >= 0

    # Test cpukinds_get_info
    cpuset, efficiency, ninfos = cpukinds_get_info(topo.hdl, kind_index, 0)
    assert cpuset is not None
    assert isinstance(efficiency, int)
    assert efficiency == 100 or efficiency == -1
    assert ninfos.contents is not None

    bitmap_free(cpuset)
    bitmap_free(test_cpuset)

    assert any(
        ninfos.contents.array[i].name == b"TestCPUKind"
        for i in range(ninfos.contents.count)
    )
    assert any(
        ninfos.contents.array[i].value == b"TestValue"
        for i in range(ninfos.contents.count)
    )


def test_cpukinds_register_empty_infos() -> None:
    topo = Topology()

    # Get initial number of CPU kinds
    initial_nr_kinds = cpukinds_get_nr(topo.hdl, 0)

    # Create a test cpuset (use CPU 1 if available, otherwise CPU 0)
    test_cpuset = bitmap_alloc()
    bitmap_set(test_cpuset, 1)

    # Register a CPU kind with no infos
    cpukinds_register(topo.hdl, test_cpuset, 50, None)

    # Verify the number of kinds increased
    new_nr_kinds = cpukinds_get_nr(topo.hdl, 0)
    assert new_nr_kinds == initial_nr_kinds + 1

    bitmap_free(test_cpuset)
