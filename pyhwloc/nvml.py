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

import pynvml

from .core import ObjType, _checkc, _pyhwloc_lib, hwloc_cpuset_t, obj_t, topology_t

#####################################################
# Interoperability with the NVIDIA Management Library
#####################################################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00179.php


_pyhwloc_lib.pyhwloc_nvml_get_device_cpuset.argtypes = [
    topology_t,
    pynvml.c_nvmlDevice_t,
    hwloc_cpuset_t,
]
_pyhwloc_lib.pyhwloc_nvml_get_device_cpuset.restype = ctypes.c_int


def get_device_cpuset(
    topology: topology_t, device: pynvml.c_nvmlDevice_t, cpuset: hwloc_cpuset_t
) -> None:
    _checkc(_pyhwloc_lib.pyhwloc_nvml_get_device_cpuset(topology, device, cpuset))


_pyhwloc_lib.pyhwloc_nvml_get_device_osdev_by_index.argtypes = [
    topology_t,
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_nvml_get_device_osdev_by_index.restype = obj_t


def get_device_osdev_by_index(topology: topology_t, idx: int) -> ObjType:
    return _pyhwloc_lib.pyhwloc_nvml_get_device_osdev_by_index(topology, idx)


_pyhwloc_lib.pyhwloc_nvml_get_device_osdev.argtypes = [
    topology_t,
    pynvml.c_nvmlDevice_t,
]
_pyhwloc_lib.pyhwloc_nvml_get_device_osdev.restype = obj_t


def get_device_osdev(topology: topology_t, device: pynvml.c_nvmlDevice_t) -> ObjType:
    dev_obj = _pyhwloc_lib.pyhwloc_nvml_get_device_osdev(topology, device)
    return dev_obj
