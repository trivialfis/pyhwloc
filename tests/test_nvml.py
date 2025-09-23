# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import ctypes
import platform

import pytest

from .test_hwloc.utils import has_gpu

if not has_gpu():
    pytest.skip("GPU discovery tests.", allow_module_level=True)

if platform.system() == "Windows":
    pytest.skip("Linux-only tests.", allow_module_level=True)

pytest.importorskip("pynvml")

import pynvml as nm

from pyhwloc import nvml as hwloc_nvml
from pyhwloc.hwobject import OsDevice
from pyhwloc.topology import Topology, TypeFilter


def test_nvml() -> None:
    with Topology.from_this_system().set_io_types_filter(TypeFilter.KEEP_ALL) as topo:
        nm.nvmlInit()
        dev = hwloc_nvml.get_device(topo, 0)

        osdev = dev.get_osdev()
        assert osdev is not None and isinstance(osdev, OsDevice)
        assert osdev.is_gpu()

        nmhdl = nm.nvmlDeviceGetHandleByIndex(0)
        assert isinstance(nmhdl, ctypes._Pointer)
        dev = hwloc_nvml.get_device(topo, nmhdl)
        osdev = dev.get_osdev()
        assert osdev is not None and isinstance(osdev, OsDevice)
        assert osdev.is_gpu()

        assert dev.get_affinity().weight() >= 1

        nm.nvmlShutdown()

        with pytest.raises(RuntimeError, match="get_device"):
            type(dev)()


def test_with_nvml_cpu_affinity() -> None:
    try:
        nm.nvmlInit()
        aff = hwloc_nvml.get_cpu_affinity(0)
        assert aff.weight() > 0
        with Topology.from_this_system().set_io_types_filter(
            TypeFilter.KEEP_ALL
        ) as topo:
            dev = hwloc_nvml.get_device(topo, 0)
            assert dev.get_affinity() == aff
    finally:
        nm.nvmlShutdown()
