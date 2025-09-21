# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Linux-specific helpers
======================
"""

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00171.php

from __future__ import annotations

import ctypes
import platform

from .bitmap import bitmap_t
from .core import (
    _LIB,
    _checkc,
    hwloc_const_cpuset_t,
    hwloc_cpuset_t,
    topology_t,
)
from .lib import _IS_DOC_BUILD, _c_prefix_fndoc

if platform.system() != "Linux" and not _IS_DOC_BUILD:
    raise ImportError("This module is only defined for Linux.")


if not _IS_DOC_BUILD:
    _LIB.hwloc_linux_set_tid_cpubind.argtypes = [
        topology_t,
        ctypes.c_int,  # pid_t (typically int on Linux)
        hwloc_const_cpuset_t,
    ]
    _LIB.hwloc_linux_set_tid_cpubind.restype = ctypes.c_int


@_c_prefix_fndoc("linux")
def set_tid_cpubind(
    topology: topology_t, tid: int, cpuset: hwloc_const_cpuset_t
) -> None:
    _checkc(_LIB.hwloc_linux_set_tid_cpubind(topology, tid, cpuset))


if not _IS_DOC_BUILD:
    _LIB.hwloc_linux_get_tid_cpubind.argtypes = [
        topology_t,
        ctypes.c_int,  # pid_t (typically int on Linux)
        hwloc_cpuset_t,
    ]
    _LIB.hwloc_linux_get_tid_cpubind.restype = ctypes.c_int


@_c_prefix_fndoc("linux")
def get_tid_cpubind(topology: topology_t, tid: int, cpuset: hwloc_cpuset_t) -> None:
    _checkc(_LIB.hwloc_linux_get_tid_cpubind(topology, tid, cpuset))


if not _IS_DOC_BUILD:
    _LIB.hwloc_linux_get_tid_last_cpu_location.argtypes = [
        topology_t,
        ctypes.c_int,  # pid_t (typically int on Linux)
        bitmap_t,
    ]
    _LIB.hwloc_linux_get_tid_last_cpu_location.restype = ctypes.c_int


@_c_prefix_fndoc("linux")
def get_tid_last_cpu_location(topology: topology_t, tid: int, cpuset: bitmap_t) -> None:
    _checkc(_LIB.hwloc_linux_get_tid_last_cpu_location(topology, tid, cpuset))


if not _IS_DOC_BUILD:
    _LIB.hwloc_linux_read_path_as_cpumask.argtypes = [
        ctypes.c_char_p,  # const char *path
        bitmap_t,
    ]
    _LIB.hwloc_linux_read_path_as_cpumask.restype = ctypes.c_int


@_c_prefix_fndoc("linux")
def read_path_as_cpumask(path: str, cpuset: bitmap_t) -> None:
    path_bytes = path.encode("utf-8")
    _checkc(_LIB.hwloc_linux_read_path_as_cpumask(path_bytes, cpuset))
