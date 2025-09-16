# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
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
