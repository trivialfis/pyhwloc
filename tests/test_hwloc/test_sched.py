# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import os
import platform

import pytest

from pyhwloc.hwloc.bitmap import bitmap_free
from pyhwloc.hwloc.sched import (
    cpuset_from_sched_affinity,
    cpuset_to_sched_affinity,
)


@pytest.mark.skipif(
    condition=platform.system() != "Linux", reason="Linux-specific test"
)
def test_cpuset_sched_affinity() -> None:
    assert hasattr(os, "sched_getaffinity")
    aff0 = os.sched_getaffinity(0)
    cpuset = cpuset_from_sched_affinity(aff0)
    aff1 = cpuset_to_sched_affinity(cpuset)
    bitmap_free(cpuset)
    assert aff0 == aff1
