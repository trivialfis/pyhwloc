# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Interoperability with the NVIDIA Management Library
===================================================
"""

from __future__ import annotations

import ctypes
import os

import pynvml

from .core import ObjPtr, _checkc, hwloc_cpuset_t, obj_t, topology_t
from .lib import _IS_DOC_BUILD, _c_prefix_fndoc, _get_libname, _lib_path

#####################################################
# Interoperability with the NVIDIA Management Library
#####################################################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00179.php

if not _IS_DOC_BUILD:
    _pyhwloc_nvml_lib = ctypes.cdll.LoadLibrary(
        os.path.join(_lib_path, _get_libname("pyhwloc_nvml"))
    )

    _pyhwloc_nvml_lib.pyhwloc_nvml_get_device_cpuset.argtypes = [
        topology_t,
        pynvml.c_nvmlDevice_t,
        hwloc_cpuset_t,
    ]
    _pyhwloc_nvml_lib.pyhwloc_nvml_get_device_cpuset.restype = ctypes.c_int


@_c_prefix_fndoc("nvml")
def get_device_cpuset(
    topology: topology_t, device: pynvml.c_nvmlDevice_t, cpuset: hwloc_cpuset_t
) -> None:
    _checkc(_pyhwloc_nvml_lib.pyhwloc_nvml_get_device_cpuset(topology, device, cpuset))


if not _IS_DOC_BUILD:
    _pyhwloc_nvml_lib.pyhwloc_nvml_get_device_osdev_by_index.argtypes = [
        topology_t,
        ctypes.c_uint,
    ]
    _pyhwloc_nvml_lib.pyhwloc_nvml_get_device_osdev_by_index.restype = obj_t


@_c_prefix_fndoc("nvml")
def get_device_osdev_by_index(topology: topology_t, idx: int) -> ObjPtr | None:
    dev_obj = _pyhwloc_nvml_lib.pyhwloc_nvml_get_device_osdev_by_index(topology, idx)
    if not dev_obj:
        return None
    return dev_obj


if not _IS_DOC_BUILD:
    _pyhwloc_nvml_lib.pyhwloc_nvml_get_device_osdev.argtypes = [
        topology_t,
        pynvml.c_nvmlDevice_t,
    ]
    _pyhwloc_nvml_lib.pyhwloc_nvml_get_device_osdev.restype = obj_t


@_c_prefix_fndoc("nvml")
def get_device_osdev(
    topology: topology_t, device: pynvml.c_nvmlDevice_t
) -> ObjPtr | None:
    dev_obj = _pyhwloc_nvml_lib.pyhwloc_nvml_get_device_osdev(topology, device)
    if not dev_obj:
        return None
    return dev_obj
