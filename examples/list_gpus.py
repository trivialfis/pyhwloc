"""
Simple script for listing GPU devices
=====================================
"""

from pyhwloc.hwobject import GetTypeDepth, ObjType
from pyhwloc.topology import Topology, TypeFilter

with (
    Topology(load=False)
    # GPU is categorized as IO device.
    .set_io_types_filter(TypeFilter.HWLOC_TYPE_FILTER_KEEP_ALL).load() as topo
):
    # Look for OS devices (which include GPUs)
    os_devices = list(topo.iter_objects_by_type(ObjType.HWLOC_OBJ_OS_DEVICE))

    for obj in os_devices:
        # Check if it's a GPU device
        if obj.is_osdev_gpu:
            assert obj.depth == GetTypeDepth.HWLOC_TYPE_DEPTH_OS_DEVICE
            print(obj)
