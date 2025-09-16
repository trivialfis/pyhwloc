# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import platform

import pytest

from pyhwloc.hwloc.bitmap import (
    bitmap_alloc,
    bitmap_free,
    bitmap_isequal,
    bitmap_iszero,
    bitmap_only,
)

pytest.importorskip("pyhwloc.linux", exc_type=ImportError)

from pyhwloc.hwloc.linux import (
    get_tid_cpubind,
    get_tid_last_cpu_location,
    set_tid_cpubind,
)

from .test_core import Topology


@pytest.mark.skipif(
    condition=platform.system() != "Linux", reason="Linux-specific test"
)
def test_tid_cpubind() -> None:
    topo = Topology()
    tid = 0

    # Allocate cpusets for testing
    original_cpuset = bitmap_alloc()
    test_cpuset = bitmap_alloc()
    retrieved_cpuset = bitmap_alloc()

    get_tid_cpubind(topo.hdl, tid, original_cpuset)

    # Create a test CPU set (bind to CPU 0 only)
    bitmap_only(test_cpuset, 0)
    # Roundtrip
    set_tid_cpubind(topo.hdl, tid, test_cpuset)
    get_tid_cpubind(topo.hdl, tid, retrieved_cpuset)

    assert bitmap_isequal(test_cpuset, retrieved_cpuset)

    # Restore original CPU binding
    set_tid_cpubind(topo.hdl, tid, original_cpuset)

    bitmap_free(original_cpuset)
    bitmap_free(test_cpuset)
    bitmap_free(retrieved_cpuset)


@pytest.mark.skipif(
    condition=platform.system() != "Linux", reason="Linux-specific test"
)
def test_get_tid_last_cpu_location() -> None:
    topo = Topology()
    cpuset = bitmap_alloc()
    get_tid_last_cpu_location(topo.hdl, 0, cpuset)
    assert not bitmap_iszero(cpuset)
    bitmap_free(cpuset)
