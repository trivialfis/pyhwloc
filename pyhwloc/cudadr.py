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
import cuda.bindings.driver as cuda

from .core import _pyhwloc_lib, obj_t, topology_t, ObjType


def _check_cu(status: cuda.CUresult) -> None:
    if status != cuda.CUresult.CUDA_SUCCESS:
        res, msg = cuda.cuGetErrorString(status)
        if res != cuda.CUresult.CUDA_SUCCESS:
            msg = f"Failed to call `cuGetErrorString` for a CUresult: {status}"
        raise RuntimeError(msg)

###########################################
# Interoperability with the CUDA Driver API
###########################################


_pyhwloc_lib.pyhwloc_cuda_get_device_osdev.restype = obj_t


def get_device_osdev(topology: topology_t, device: cuda.CUdevice) -> ObjType:
    dev_obj = _pyhwloc_lib.pyhwloc_cuda_get_device_osdev(topology, int(device))
    return dev_obj


_pyhwloc_lib.pyhwloc_cuda_get_device_osdev_by_index.restype = obj_t


def get_device_osdev_by_index(topology: topology_t, idx: int) -> ObjType:
    dev_obj = _pyhwloc_lib.pyhwloc_cuda_get_device_osdev_by_index(topology, idx)
    return dev_obj
