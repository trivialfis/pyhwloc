# Copyright (c) 2025, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import pytest

cudart = pytest.importorskip("cuda.bindings.runtime", exc_type=ImportError)

from pyhwloc.hwloc.bitmap import (
    bitmap_alloc,
    bitmap_free,
    bitmap_iszero,
    bitmap_weight,
)
from pyhwloc.hwloc.core import (
    TypeFilter,
    ObjType,
)
from pyhwloc.hwloc.cudart import (
    _check_cudart,
    get_device_cpuset,
    get_device_osdev_by_index,
    get_device_pcidev,
)

from .test_core import Topology
from .utils import _skip_if_none


def test_get_device_osdev() -> None:
    topo = Topology([TypeFilter.HWLOC_TYPE_FILTER_KEEP_IMPORTANT])

    status, cnt = cudart.cudaGetDeviceCount()
    _check_cudart(status)

    for ordinal in range(cnt):
        dev_obj = get_device_osdev_by_index(topo.hdl, ordinal)
        assert _skip_if_none(dev_obj)
        assert dev_obj.contents.type == ObjType.HWLOC_OBJ_OS_DEVICE


def test_cudart_get_device_cpuset() -> None:
    topo = Topology([TypeFilter.HWLOC_TYPE_FILTER_KEEP_IMPORTANT])

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
    topo = Topology([TypeFilter.HWLOC_TYPE_FILTER_KEEP_IMPORTANT])

    status, cnt = cudart.cudaGetDeviceCount()
    _check_cudart(status)

    for ordinal in range(cnt):
        pci_obj = get_device_pcidev(topo.hdl, ordinal)
        assert _skip_if_none(pci_obj)
        assert pci_obj is not None
        assert pci_obj.contents.type == ObjType.HWLOC_OBJ_PCI_DEVICE
