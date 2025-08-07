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
import cuda.bindings.runtime as cudart

from pyhwloc.core import hwloc_type_filter_e, hwloc_obj_type_t
from pyhwloc.cudart import _check_cudart, get_device_osdev_by_index

from .test_core import Topology


def test_get_device_osdev() -> None:
    topo = Topology([hwloc_type_filter_e.HWLOC_TYPE_FILTER_KEEP_IMPORTANT])

    status, cnt = cudart.cudaGetDeviceCount()
    _check_cudart(status)

    for i in range(cnt):
        dev_obj = get_device_osdev_by_index(topo.hdl, i)
        assert dev_obj.contents.type == hwloc_obj_type_t.HWLOC_OBJ_OS_DEVICE
