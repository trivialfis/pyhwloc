# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import pytest

cuda = pytest.importorskip("cuda.bindings.driver", exc_type=ImportError)
_ = pytest.importorskip("pyhwloc.hwloc.cudadr", exc_type=OSError)  # type: ignore

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
from pyhwloc.hwloc.cudadr import (
    _check_cu,
    get_device_cpuset,
    get_device_osdev,
    get_device_osdev_by_index,
    get_device_pci_ids,
    get_device_pcidev,
)

from .test_core import Topology


def test_get_device_osdev() -> None:
    cuda.cuInit(0)
    res, cnt = cuda.cuDeviceGetCount()
    _check_cu(res)

    topo = Topology([TypeFilter.KEEP_IMPORTANT])

    for i in range(cnt):
        res, dev = cuda.cuDeviceGet(i)
        _check_cu(res)
        dev_obj = get_device_osdev(topo.hdl, dev)
        assert _skip_if_none(dev_obj)
        assert dev_obj.contents.type == ObjType.OS_DEVICE

        dev_obj = get_device_osdev_by_index(topo.hdl, i)
        assert _skip_if_none(dev_obj)
        assert dev_obj.contents.type == ObjType.OS_DEVICE


def test_cuda_get_device_pci_ids() -> None:
    cuda.cuInit(0)
    res, cnt = cuda.cuDeviceGetCount()
    _check_cu(res)
    assert cnt > 0

    topo = Topology([TypeFilter.KEEP_IMPORTANT])

    for i in range(cnt):
        res, dev = cuda.cuDeviceGet(i)
        _check_cu(res)

        # Get PCI IDs for the CUDA device
        domain, bus, device_id = get_device_pci_ids(topo.hdl, dev)

        # Verify return types
        assert isinstance(domain, int) and domain >= 0
        assert isinstance(bus, int) and bus >= 0
        assert isinstance(device_id, int) and device_id >= 0

        # Cross check consistency.
        res, cudomain = cuda.cuDeviceGetAttribute(
            cuda.CUdevice_attribute.CU_DEVICE_ATTRIBUTE_PCI_DOMAIN_ID, dev
        )
        _check_cu(res)
        assert domain == cudomain


def test_cuda_get_device_cpuset() -> None:
    cuda.cuInit(0)
    res, cnt = cuda.cuDeviceGetCount()
    _check_cu(res)
    assert cnt > 0

    topo = Topology([TypeFilter.KEEP_IMPORTANT])

    for i in range(cnt):
        res, dev = cuda.cuDeviceGet(i)
        _check_cu(res)

        # Allocate a cpuset to receive the device's CPU affinity
        cpuset = bitmap_alloc()

        # Get the CPU set for the CUDA device
        get_device_cpuset(topo.hdl, dev, cpuset)
        assert not bitmap_iszero(cpuset)

        weight = bitmap_weight(cpuset)
        assert weight > 0

        bitmap_free(cpuset)


def test_cuda_get_device_pcidev() -> None:
    cuda.cuInit(0)
    res, cnt = cuda.cuDeviceGetCount()
    _check_cu(res)
    assert cnt > 0

    topo = Topology([TypeFilter.KEEP_IMPORTANT])

    for i in range(cnt):
        res, dev = cuda.cuDeviceGet(i)
        _check_cu(res)

        # Get the PCI device object for the CUDA device
        pci_obj = get_device_pcidev(topo.hdl, dev)
        assert _skip_if_none(pci_obj)

        assert pci_obj.contents.type == ObjType.PCI_DEVICE
        # Get the PCI attributes
        pci_attr = pci_obj.contents.attr.contents.pcidev

        # Cross-validate with cuda_get_device_pci_ids
        hwloc_domain, hwloc_bus, hwloc_dev = get_device_pci_ids(topo.hdl, dev)

        assert pci_attr.domain == hwloc_domain
        assert pci_attr.bus == hwloc_bus
        assert pci_attr.dev == hwloc_dev
