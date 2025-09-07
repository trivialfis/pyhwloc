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
import platform

from .core import _LIB, _checkc, hwloc_cpuset_t, topology_t

if platform.system() != "Windows":
    raise ImportError("This module is only defined for Windows.")

##########################
# Windows-specific helpers
##########################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00174.php


_LIB.hwloc_windows_get_nr_processor_groups.argtypes = [topology_t, ctypes.c_ulong]
_LIB.hwloc_windows_get_nr_processor_groups.restype = ctypes.c_int


def windows_get_nr_processor_groups(topology: topology_t) -> int:
    # flags must be 0
    nr = _LIB.hwloc_windows_get_nr_processor_groups(topology, 0)
    if nr == -1:
        _checkc(nr)
    return nr


_LIB.hwloc_windows_get_processor_group_cpuset.argtypes = [
    topology_t,
    ctypes.c_uint,
    hwloc_cpuset_t,
    ctypes.c_ulong,
]
_LIB.hwloc_windows_get_processor_group_cpuset.restype = ctypes.c_int


def windows_get_processor_group_cpuset(
    topology: topology_t, pg_index: int, cpuset: hwloc_cpuset_t
) -> None:
    # flags must be 0
    # cpuset is the output.
    _checkc(
        _LIB.hwloc_windows_get_processor_group_cpuset(topology, pg_index, cpuset, 0)
    )
