# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import pytest

from pyhwloc.hwloc.bitmap import (
    bitmap_alloc,
    bitmap_free,
    bitmap_iszero,
    bitmap_weight,
)
from pyhwloc.hwloc.core import (
    ObjType,
    TypeFilter,
)

nm = pytest.importorskip("pynvml", exc_type=ImportError)
_ = pytest.importorskip("pyhwloc.hwloc.nvml", exc_type=OSError)  # type: ignore

from pyhwloc.hwloc.nvml import get_device_cpuset, get_device_osdev

from .test_core import Topology
from .utils import _skip_if_none


class Nvml:
    def __enter__(self) -> None:
        nm.nvmlInit()

    def __exit__(self, t: None, value: None, traceback: None) -> None:
        nm.nvmlShutdown()


def test_get_device_osdev() -> None:
    topo = Topology([TypeFilter.KEEP_IMPORTANT])

    with Nvml():
        nvhdl = nm.nvmlDeviceGetHandleByIndex(0)
        idx = nm.nvmlDeviceGetIndex(nvhdl)
        assert idx == 0

        dev_obj = get_device_osdev(topo.hdl, nvhdl)
        assert _skip_if_none(dev_obj)
        assert dev_obj.contents.type == ObjType.OS_DEVICE


def test_nvml_get_device_cpuset() -> None:
    topo = Topology([TypeFilter.KEEP_IMPORTANT])

    with Nvml():
        # Get handle for the first device
        nvhdl = nm.nvmlDeviceGetHandleByIndex(0)

        cpuset = bitmap_alloc()

        get_device_cpuset(topo.hdl, nvhdl, cpuset)
        assert not bitmap_iszero(cpuset)
        weight = bitmap_weight(cpuset)
        assert weight > 0

        bitmap_free(cpuset)
