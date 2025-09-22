# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import pytest

cudart = pytest.importorskip("cuda.bindings.runtime", exc_type=ImportError)
_ = pytest.importorskip("pyhwloc.hwloc.cudart", exc_type=OSError)  # type: ignore

from .utils import _skip_if_none, has_gpu

if not has_gpu():
    pytest.skip("GPU discovery tests.", allow_module_level=True)

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
from pyhwloc.hwloc.cudart import (
    _check_cudart,
    get_device_cpuset,
    get_device_osdev_by_index,
    get_device_pcidev,
)

from .test_core import Topology


def test_get_device_osdev() -> None:
    topo = Topology([TypeFilter.KEEP_IMPORTANT])

    status, cnt = cudart.cudaGetDeviceCount()
    _check_cudart(status)

    for ordinal in range(cnt):
        dev_obj = get_device_osdev_by_index(topo.hdl, ordinal)
        assert _skip_if_none(dev_obj)
        assert dev_obj.contents.type == ObjType.OS_DEVICE


def test_cudart_get_device_cpuset() -> None:
    topo = Topology([TypeFilter.KEEP_IMPORTANT])

    status, cnt = cudart.cudaGetDeviceCount()
    _check_cudart(status)

    for ordinal in range(cnt):
        cpuset = bitmap_alloc()

        get_device_cpuset(topo.hdl, ordinal, cpuset)
        assert not bitmap_iszero(cpuset)

        weight = bitmap_weight(cpuset)
        assert weight > 0

        bitmap_free(cpuset)


def test_get_device_pcidev() -> None:
    topo = Topology([TypeFilter.KEEP_IMPORTANT])

    status, cnt = cudart.cudaGetDeviceCount()
    _check_cudart(status)

    for ordinal in range(cnt):
        pci_obj = get_device_pcidev(topo.hdl, ordinal)
        assert _skip_if_none(pci_obj)
        assert pci_obj is not None
        assert pci_obj.contents.type == ObjType.PCI_DEVICE
