# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Low-level API Example
=====================

This is a direct translation of the original C example. You can find the C version at:
https://www.open-mpi.org/projects/hwloc/doc/v2.12.2/index.html#interface_example

In general, most users do not need this interface, unless you need specific features
that are not yet exposed to the high-level interface. In that case, please let us know
about the features that you need.

"""

import ctypes
import platform
from typing import cast

from pyhwloc.hwloc.bitmap import (
    bitmap_asprintf,
    bitmap_dup,
    bitmap_free,
    bitmap_singlify,
)
from pyhwloc.hwloc.core import (
    HWLOC_UNKNOWN_INDEX,
    GetTypeDepth,
    MemBindFlags,
    MemBindPolicy,
    ObjPtr,
    ObjType,
    alloc_membind,
    free,
    get_nbobjs_by_depth,
    get_nbobjs_by_type,
    get_obj_by_depth,
    get_obj_by_type,
    get_root_obj,
    get_type_depth,
    get_type_or_below_depth,
    obj_attr_snprintf,
    obj_type_is_cache,
    obj_type_snprintf,
    set_area_membind,
    set_cpubind,
    topology_destroy,
    topology_get_depth,
    topology_init,
    topology_load,
    topology_t,
)


def print_children(topology: topology_t, obj: ObjPtr, depth: int) -> None:
    type_buf = ctypes.create_string_buffer(32)
    attr_buf = ctypes.create_string_buffer(1024)

    obj_type_snprintf(cast(ctypes.c_char_p, type_buf), 32, obj, 0)
    print("  " * depth + type_buf.value.decode(), end="")

    if obj.contents.os_index != HWLOC_UNKNOWN_INDEX:
        print(f"#{obj.contents.os_index}", end="")

    obj_attr_snprintf(attr_buf, 1024, obj, " ", 0)
    if attr_buf.value:
        print(f"({attr_buf.value.decode()})", end="")

    print()

    for i in range(obj.contents.arity):
        child = obj.contents.children[i]
        print_children(topology, child, depth + 1)


def main() -> int:
    # Variable definitions from C code
    depth: int
    i: int
    n: int
    size: int
    levels: int
    string_buf = ctypes.create_string_buffer(128)
    topodepth: int
    m: ctypes.c_void_p
    topology = topology_t()
    cpuset = None
    obj: ObjPtr | None

    # Allocate and initialize topology object.
    topology_init(topology)

    # ... Optionally, put detection configuration here to ignore
    # some objects types, define a synthetic topology, etc....
    #
    # The default is to detect all the objects of the machine that
    # the caller is allowed to access.  See Configure Topology
    # Detection.

    # Perform the topology detection.
    topology_load(topology)

    # Optionally, get some additional topology information
    # in case we need the topology depth later.
    topodepth = topology_get_depth(topology)

    #########################################################################
    # First example:
    # Walk the topology with an array style, from level 0 (always
    # the system level) to the lowest level (always the proc level).
    #########################################################################
    for depth in range(topodepth):
        print(f"*** Objects at level {depth}")
        for i in range(get_nbobjs_by_depth(topology, depth)):
            obj = get_obj_by_depth(topology, depth, i)
            if obj:
                obj_type_snprintf(cast(ctypes.c_char_p, string_buf), 128, obj, 0)
                print(f"Index {i}: {string_buf.value.decode()}")

    #########################################################################
    # Second example:
    # Walk the topology with a tree style.
    #########################################################################
    print("*** Printing overall tree")
    print_children(topology, get_root_obj(topology), 0)

    #########################################################################
    # Third example:
    # Print the number of packages.
    #########################################################################
    depth = get_type_depth(topology, ObjType.PACKAGE)
    if depth == GetTypeDepth.UNKNOWN:
        print("*** The number of packages is unknown")
    else:
        print(f"*** {get_nbobjs_by_depth(topology, depth)} package(s)")

    #########################################################################
    # Fourth example:
    # Compute the amount of cache that the first logical processor
    # has above it.
    #########################################################################
    levels = 0
    size = 0
    obj = get_obj_by_type(topology, ObjType.PU, 0)
    while obj:
        if obj_type_is_cache(obj.contents.type):
            levels += 1
            size += obj.contents.attr.contents.cache.size
        obj = obj.contents.parent
    print(f"*** Logical processor 0 has {levels} caches totaling {size // 1024}KB")

    #########################################################################
    # Fifth example:
    # Bind to only one thread of the last core of the machine.
    #
    # First find out where cores are, or else smaller sets of CPUs if
    # the OS doesn't have the notion of a "core".
    #########################################################################
    depth = get_type_or_below_depth(topology, ObjType.CORE)

    # Get last core.
    obj = get_obj_by_depth(topology, depth, get_nbobjs_by_depth(topology, depth) - 1)
    if obj:
        # Get a copy of its cpuset that we may modify.
        cpuset = bitmap_dup(obj.contents.cpuset)

        # Get only one logical processor (in case the core is
        # SMT/hyper-threaded).
        bitmap_singlify(cpuset)

        # And try to bind ourself there.
        try:
            set_cpubind(topology, cpuset, 0)
        except Exception as e:
            cpu_str = bitmap_asprintf(obj.contents.cpuset)
            print(f"Couldn't bind to cpuset {cpu_str}: {e}")

        # Free our cpuset copy
        bitmap_free(cpuset)

    #########################################################################
    # Sixth example:
    # Allocate some memory on the last NUMA node, bind some existing
    # memory to the last NUMA node.
    #########################################################################
    # Get last node. There's always at least one.
    n = get_nbobjs_by_type(topology, ObjType.NUMANODE)
    obj = get_obj_by_type(topology, ObjType.NUMANODE, n - 1)
    assert obj is not None

    size = 1024 * 1024
    m = alloc_membind(
        topology,
        size,
        obj.contents.nodeset,
        MemBindPolicy.BIND,
        MemBindFlags.BYNODESET,
    )
    free(topology, m, size)

    # Allocate using malloc equivalent and bind
    if platform.system() == "Linux":
        m = ctypes.cast(ctypes.c_char_p(b"\x00" * size), ctypes.c_void_p)
        set_area_membind(
            topology,
            m,
            size,
            obj.contents.nodeset,
            MemBindPolicy.BIND,
            MemBindFlags.BYNODESET,
        )

    # Destroy topology object.
    topology_destroy(topology)

    return 0


if __name__ == "__main__":
    main()
