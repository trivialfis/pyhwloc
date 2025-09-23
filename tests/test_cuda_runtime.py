# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pytest

from .test_hwloc.utils import has_gpu

if not has_gpu():
    pytest.skip("GPU discovery tests.", allow_module_level=True)

from pyhwloc import cuda_runtime as hwloc_cudart
from pyhwloc.hwobject import OsDevice
from pyhwloc.topology import Topology, TypeFilter
from pyhwloc.utils import PciId


def test_cudart() -> None:
    with Topology.from_this_system().set_io_types_filter(TypeFilter.KEEP_ALL) as topo:
        dev = hwloc_cudart.get_device(topo, 0)

        osdev = dev.get_osdev()
        assert osdev is not None
        assert isinstance(osdev, OsDevice) and osdev.is_gpu()

        pcidev = dev.get_pcidev()
        if pcidev is not None:
            assert pcidev.is_pci_device()

        assert dev.get_affinity().weight() >= 1
        assert isinstance(dev.pci_id, PciId)

        with pytest.raises(RuntimeError, match="get_device"):
            type(dev)()
