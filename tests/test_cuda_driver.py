# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pytest

from .test_hwloc.utils import has_gpu

if not has_gpu():
    pytest.skip("GPU discovery tests.", allow_module_level=True)

cuda = pytest.importorskip("cuda.bindings.driver")

from pyhwloc import cuda_driver as hwloc_cudadr
from pyhwloc.hwloc.cudadr import _check_cu
from pyhwloc.hwobject import OsDevice
from pyhwloc.topology import Topology, TypeFilter


def test_cuda_driver() -> None:
    with Topology.from_this_system().set_io_types_filter(TypeFilter.KEEP_ALL) as topo:
        cuda.cuInit(0)
        status, cu_device = cuda.cuDeviceGet(0)
        _check_cu(status)

        dev = hwloc_cudadr.get_device(topo, cu_device)

        osdev = dev.get_osdev()
        assert osdev is not None
        assert isinstance(osdev, OsDevice) and osdev.is_gpu()

        pcidev = dev.get_pcidev()
        assert pcidev is not None
        assert pcidev.is_pci_device()

        assert dev.get_affinity().weight() >= 1

        pci_id = dev.pci_id
        assert isinstance(pci_id, hwloc_cudadr.PciId)
        assert pci_id.domain >= 0
        assert pci_id.bus >= 0
        assert pci_id.dev >= 0

        with pytest.raises(RuntimeError, match="get_device"):
            type(dev)()
