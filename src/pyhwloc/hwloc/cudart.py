# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Interoperability with the CUDA Runtime API
==========================================
"""

from __future__ import annotations

import ctypes
import os

import cuda.bindings.runtime as cudart

from .core import ObjPtr, _checkc, hwloc_cpuset_t, obj_t, topology_t
from .lib import _IS_DOC_BUILD, _c_prefix_fndoc, _get_libname, _lib_path

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00178.php

if not _IS_DOC_BUILD:
    _pyhwloc_cudart_lib = ctypes.cdll.LoadLibrary(
        os.path.join(_lib_path, _get_libname("pyhwloc_cudart"))
    )


def _check_cudart(status: cudart.cudaError_t) -> None:
    if status != cudart.cudaError_t.cudaSuccess:
        res, msg = cudart.cudaGetErrorString(status)
        if res != cudart.cudaError_t.cudaSuccess:
            msg = f"Failed to call `cudaGetErrorString` for a cudaError_t: {status}"
        raise RuntimeError(msg)


if not _IS_DOC_BUILD:
    _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_pci_ids.argtypes = [
        topology_t,
        ctypes.c_int,  # device index
        ctypes.POINTER(ctypes.c_int),  # domain
        ctypes.POINTER(ctypes.c_int),  # bus
        ctypes.POINTER(ctypes.c_int),  # dev
    ]
    _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_pci_ids.restype = ctypes.c_int


@_c_prefix_fndoc("cudart")
def get_device_pci_ids(topology: topology_t, idx: int) -> tuple[int, int, int]:
    domain = ctypes.c_int()
    bus = ctypes.c_int()
    dev = ctypes.c_int()

    _checkc(
        _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_pci_ids(
            topology, idx, ctypes.byref(domain), ctypes.byref(bus), ctypes.byref(dev)
        )
    )

    return domain.value, bus.value, dev.value


if not _IS_DOC_BUILD:
    _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_cpuset.argtypes = [
        topology_t,
        ctypes.c_int,  # device index
        hwloc_cpuset_t,
    ]
    _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_cpuset.restype = ctypes.c_int


@_c_prefix_fndoc("cudart")
def get_device_cpuset(topology: topology_t, idx: int, cpuset: hwloc_cpuset_t) -> None:
    _checkc(_pyhwloc_cudart_lib.pyhwloc_cudart_get_device_cpuset(topology, idx, cpuset))


if not _IS_DOC_BUILD:
    _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_pcidev.argtypes = [
        topology_t,
        ctypes.c_int,  # device index
    ]
    _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_pcidev.restype = obj_t


@_c_prefix_fndoc("cudart")
def get_device_pcidev(topology: topology_t, idx: int) -> ObjPtr | None:
    dev_obj = _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_pcidev(topology, idx)
    if not dev_obj:
        return None
    return dev_obj


if not _IS_DOC_BUILD:
    _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_osdev_by_index.restype = obj_t


@_c_prefix_fndoc("cudart")
def get_device_osdev_by_index(topology: topology_t, idx: int) -> ObjPtr | None:
    dev_obj = _pyhwloc_cudart_lib.pyhwloc_cudart_get_device_osdev_by_index(
        topology, idx
    )
    if not dev_obj:
        return None
    return dev_obj
