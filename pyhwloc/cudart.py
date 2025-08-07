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

from .core import ObjType, _pyhwloc_lib, obj_t, topology_t


def _check_cudart(status: cudart.cudaError_t) -> None:
    if status != cudart.cudaError_t.cudaSuccess:
        res, msg = cudart.cudaGetErrorString(status)
        if res != cudart.cudaError_t.cudaSuccess:
            msg = f"Failed to call `cudaGetErrorString` for a cudaError_t: {status}"
        raise RuntimeError(msg)


_pyhwloc_lib.pyhwloc_cudart_get_device_osdev_by_index.restype = obj_t


def get_device_osdev_by_index(topology: topology_t, idx: int) -> ObjType:
    dev_obj = _pyhwloc_lib.pyhwloc_cudart_get_device_osdev_by_index(topology, idx)
    return dev_obj
