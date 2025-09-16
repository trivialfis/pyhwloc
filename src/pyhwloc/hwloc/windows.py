# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Windows-specific helpers
========================
"""

from __future__ import annotations

import ctypes

from .core import _LIB, _checkc, hwloc_cpuset_t, topology_t
from .lib import _IS_DOC_BUILD, _IS_WINDOWS, _c_prefix_fndoc

if not _IS_WINDOWS and not _IS_DOC_BUILD:
    raise ImportError("This module is only defined for Windows.")


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00174.php


if not _IS_DOC_BUILD:
    _LIB.hwloc_windows_get_nr_processor_groups.argtypes = [topology_t, ctypes.c_ulong]
    _LIB.hwloc_windows_get_nr_processor_groups.restype = ctypes.c_int


@_c_prefix_fndoc("windows")
def get_nr_processor_groups(topology: topology_t) -> int:
    # flags must be 0
    nr = _LIB.hwloc_windows_get_nr_processor_groups(topology, 0)
    if nr == -1:
        _checkc(nr)
    return nr


if not _IS_DOC_BUILD:
    _LIB.hwloc_windows_get_processor_group_cpuset.argtypes = [
        topology_t,
        ctypes.c_uint,
        hwloc_cpuset_t,
        ctypes.c_ulong,
    ]
    _LIB.hwloc_windows_get_processor_group_cpuset.restype = ctypes.c_int


@_c_prefix_fndoc("windows")
def get_processor_group_cpuset(
    topology: topology_t, pg_index: int, cpuset: hwloc_cpuset_t
) -> None:
    # flags must be 0
    # cpuset is the output.
    _checkc(
        _LIB.hwloc_windows_get_processor_group_cpuset(topology, pg_index, cpuset, 0)
    )
