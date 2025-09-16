# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import pytest

pytest.importorskip("pyhwloc.windows", exc_type=ImportError)

from pyhwloc.hwloc.bitmap import bitmap_alloc, bitmap_free
from pyhwloc.hwloc.sched import cpuset_to_sched_affinity
from pyhwloc.hwloc.windows import (
    get_nr_processor_groups,
    get_processor_group_cpuset,
)

from .test_core import Topology


def test_windows_helpers() -> None:
    topo = Topology()
    nr = get_nr_processor_groups(topo.hdl)
    assert nr >= 1

    cpuset = bitmap_alloc()
    get_processor_group_cpuset(topo.hdl, 0, cpuset)
    aff = cpuset_to_sched_affinity(cpuset)
    assert len(aff) >= 1
    bitmap_free(cpuset)
