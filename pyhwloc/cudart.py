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

import cuda.bindings.runtime as cudart

from .core import ObjPtr, _checkc, _pyhwloc_lib, hwloc_cpuset_t, obj_t, topology_t

############################################
# Interoperability with the CUDA Runtime API
############################################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00178.php


def _check_cudart(status: cudart.cudaError_t) -> None:
    if status != cudart.cudaError_t.cudaSuccess:
        res, msg = cudart.cudaGetErrorString(status)
        if res != cudart.cudaError_t.cudaSuccess:
            msg = f"Failed to call `cudaGetErrorString` for a cudaError_t: {status}"
        raise RuntimeError(msg)


_pyhwloc_lib.pyhwloc_cudart_get_device_pci_ids.argtypes = [
    topology_t,
    ctypes.c_int,  # device index
    ctypes.POINTER(ctypes.c_int),  # domain
    ctypes.POINTER(ctypes.c_int),  # bus
    ctypes.POINTER(ctypes.c_int),  # dev
]
_pyhwloc_lib.pyhwloc_cudart_get_device_pci_ids.restype = ctypes.c_int


def get_device_pci_ids(topology: topology_t, idx: int) -> tuple[int, int, int]:
    domain = ctypes.c_int()
    bus = ctypes.c_int()
    dev = ctypes.c_int()

    _checkc(
        _pyhwloc_lib.pyhwloc_cudart_get_device_pci_ids(
            topology, idx, ctypes.byref(domain), ctypes.byref(bus), ctypes.byref(dev)
        )
    )

    return domain.value, bus.value, dev.value


_pyhwloc_lib.pyhwloc_cudart_get_device_cpuset.argtypes = [
    topology_t,
    ctypes.c_int,  # device index
    hwloc_cpuset_t,
]
_pyhwloc_lib.pyhwloc_cudart_get_device_cpuset.restype = ctypes.c_int


def get_device_cpuset(topology: topology_t, idx: int, cpuset: hwloc_cpuset_t) -> None:
    _checkc(_pyhwloc_lib.pyhwloc_cudart_get_device_cpuset(topology, idx, cpuset))


_pyhwloc_lib.pyhwloc_cudart_get_device_pcidev.argtypes = [
    topology_t,
    ctypes.c_int,  # device index
]
_pyhwloc_lib.pyhwloc_cudart_get_device_pcidev.restype = obj_t


def get_device_pcidev(topology: topology_t, idx: int) -> ObjPtr:
    return _pyhwloc_lib.pyhwloc_cudart_get_device_pcidev(topology, idx)


_pyhwloc_lib.pyhwloc_cudart_get_device_osdev_by_index.restype = obj_t


def get_device_osdev_by_index(topology: topology_t, idx: int) -> ObjPtr:
    dev_obj = _pyhwloc_lib.pyhwloc_cudart_get_device_osdev_by_index(topology, idx)
    return dev_obj
