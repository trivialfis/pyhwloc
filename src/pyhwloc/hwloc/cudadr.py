# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Interoperability with the CUDA Driver API
=========================================
"""

from __future__ import annotations

import ctypes
import os

import cuda.bindings.driver as cuda

from .core import ObjPtr, _checkc, hwloc_cpuset_t, obj_t, topology_t
from .lib import _IS_DOC_BUILD, _c_prefix_fndoc, _get_libname, _lib_path

if not _IS_DOC_BUILD:
    _pyhwloc_cuda_lib = ctypes.cdll.LoadLibrary(
        os.path.join(_lib_path, _get_libname("pyhwloc_cuda"))
    )


def _check_cu(status: cuda.CUresult) -> None:
    if status != cuda.CUresult.CUDA_SUCCESS:
        res, msg = cuda.cuGetErrorString(status)
        if res != cuda.CUresult.CUDA_SUCCESS:
            msg = f"Failed to call `cuGetErrorString` for a CUresult: {status}"
        raise RuntimeError(msg)


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00177.php

if not _IS_DOC_BUILD:
    _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_pci_ids.argtypes = [
        topology_t,
        ctypes.c_int,  # CUdevice
        ctypes.POINTER(ctypes.c_int),  # domain
        ctypes.POINTER(ctypes.c_int),  # bus
        ctypes.POINTER(ctypes.c_int),  # dev
    ]
    _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_pci_ids.restype = ctypes.c_int


@_c_prefix_fndoc("cuda")
def get_device_pci_ids(
    topology: topology_t, cudevice: cuda.CUdevice
) -> tuple[int, int, int]:
    domain = ctypes.c_int()
    bus = ctypes.c_int()
    dev = ctypes.c_int()

    _checkc(
        _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_pci_ids(
            topology,
            int(cudevice),
            ctypes.byref(domain),
            ctypes.byref(bus),
            ctypes.byref(dev),
        )
    )

    return domain.value, bus.value, dev.value


if not _IS_DOC_BUILD:
    _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_cpuset.argtypes = [
        topology_t,
        ctypes.c_int,  # CUdevice
        hwloc_cpuset_t,
    ]
    _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_cpuset.restype = ctypes.c_int


@_c_prefix_fndoc("cuda")
def get_device_cpuset(
    topology: topology_t, cudevice: cuda.CUdevice, cpuset: hwloc_cpuset_t
) -> None:
    _checkc(
        _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_cpuset(
            topology, int(cudevice), cpuset
        )
    )


if not _IS_DOC_BUILD:
    _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_pcidev.argtypes = [
        topology_t,
        ctypes.c_int,  # CUdevice
    ]
    _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_pcidev.restype = obj_t


@_c_prefix_fndoc("cuda")
def get_device_pcidev(topology: topology_t, cudevice: cuda.CUdevice) -> ObjPtr | None:
    dev_obj = _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_pcidev(topology, int(cudevice))
    if not dev_obj:
        return None
    return dev_obj


if not _IS_DOC_BUILD:
    _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_osdev.restype = obj_t


@_c_prefix_fndoc("cuda")
def get_device_osdev(topology: topology_t, device: cuda.CUdevice) -> ObjPtr | None:
    dev_obj = _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_osdev(topology, int(device))
    if not dev_obj:
        return None
    return dev_obj


if not _IS_DOC_BUILD:
    _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_osdev_by_index.restype = obj_t


@_c_prefix_fndoc("cuda")
def get_device_osdev_by_index(topology: topology_t, idx: int) -> ObjPtr | None:
    dev_obj = _pyhwloc_cuda_lib.pyhwloc_cuda_get_device_osdev_by_index(topology, idx)
    if not dev_obj:
        return None
    return dev_obj
