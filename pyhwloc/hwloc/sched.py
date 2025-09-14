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
Interoperability with Python sched affinity
===========================================
"""

from __future__ import annotations

from .bitmap import (
    bitmap_alloc,
    bitmap_first,
    bitmap_next,
    bitmap_set,
)
from .core import (
    hwloc_const_cpuset_t,
    hwloc_cpuset_t,
)

############################################
# Interoperability with glibc sched affinity
############################################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00175.php

# We don't use the linux cpuset directly. Instead, routines here have the Python
# `os.sched_*` in mind.


def cpuset_to_sched_affinity(cpuset: hwloc_const_cpuset_t) -> set[int]:
    """Convert the bitmap to the Python sched affinity set."""
    idx = bitmap_first(cpuset)
    affinity = set()
    while idx != -1:
        affinity.add(idx)
        idx = bitmap_next(cpuset, idx)
    return affinity


def cpuset_from_sched_affinity(affinity: set[int]) -> hwloc_cpuset_t:
    """Convert the Python sched affinity set to a bitmap. The caller needs to free the
    returned cpuset.

    """
    hw_cpuset = bitmap_alloc()
    for v in affinity:
        bitmap_set(hw_cpuset, v)

    return hw_cpuset
