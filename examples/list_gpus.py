# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Simple script for listing GPU devices
=====================================
"""

from pyhwloc import from_this_system
from pyhwloc.hwobject import GetTypeDepth, ObjType
from pyhwloc.topology import TypeFilter

if __name__ == "__main__":
    # GPU is categorized as IO device.
    with from_this_system().set_io_types_filter(
        TypeFilter.HWLOC_TYPE_FILTER_KEEP_ALL
    ) as topo:
        # Look for OS devices (which include GPUs)
        for obj in topo.iter_objs_by_type(ObjType.HWLOC_OBJ_OS_DEVICE):
            # Check if it's a GPU device
            if obj.is_osdev_gpu():
                assert obj.depth == GetTypeDepth.HWLOC_TYPE_DEPTH_OS_DEVICE
                print(obj, ":", obj.format_attr())
