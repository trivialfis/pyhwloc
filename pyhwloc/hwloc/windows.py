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
"""
Windows-specific helpers
========================
"""

import ctypes
import os
import platform

from .core import _LIB, _checkc, hwloc_cpuset_t, topology_t
from .lib import _c_prefix_fndoc

_is_doc_build = bool(os.environ.get("PYHWLOC_SPHINX", False))

if platform.system() != "Windows" and not _is_doc_build:
    raise ImportError("This module is only defined for Windows.")


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00174.php


if not _is_doc_build:
    _LIB.hwloc_windows_get_nr_processor_groups.argtypes = [topology_t, ctypes.c_ulong]
    _LIB.hwloc_windows_get_nr_processor_groups.restype = ctypes.c_int


@_c_prefix_fndoc("windows")
def get_nr_processor_groups(topology: topology_t) -> int:
    # flags must be 0
    nr = _LIB.hwloc_windows_get_nr_processor_groups(topology, 0)
    if nr == -1:
        _checkc(nr)
    return nr


if not _is_doc_build:
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
