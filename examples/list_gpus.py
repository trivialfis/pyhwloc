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
Simple script for listing GPU devices
=====================================
"""

from pyhwloc import Topology
from pyhwloc.hwobject import GetTypeDepth, ObjType
from pyhwloc.topology import TypeFilter

if __name__ == "__main__":
    # GPU is categorized as IO device.
    with Topology.from_this_system(load=False).set_io_types_filter(
        TypeFilter.HWLOC_TYPE_FILTER_KEEP_ALL
    ) as topo:
        # Look for OS devices (which include GPUs)
        for obj in topo.iter_objects_by_type(ObjType.HWLOC_OBJ_OS_DEVICE):
            # Check if it's a GPU device
            if obj.is_osdev_gpu:
                assert obj.depth == GetTypeDepth.HWLOC_TYPE_DEPTH_OS_DEVICE
                print(obj, ":", obj.format_attr())
