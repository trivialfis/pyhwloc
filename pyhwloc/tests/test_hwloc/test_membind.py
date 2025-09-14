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
import os
import platform

import pytest

from pyhwloc.hwloc.bitmap import (
    bitmap_alloc,
    bitmap_free,
    bitmap_only,
)
from pyhwloc.hwloc.core import (
    _close_proc_handle,
    _open_proc_handle,
    get_area_membind,
    get_membind,
    get_proc_membind,
    hwloc_membind_flags_t,
    hwloc_membind_policy_t,
    set_area_membind,
    set_membind,
    set_proc_membind,
)
from pyhwloc.hwloc.libc import free as cfree
from pyhwloc.hwloc.libc import malloc as cmalloc

from .test_core import Topology


def test_membind() -> None:
    """Test the set_membind function with different policies and flags."""
    topo = Topology()

    # Create a nodeset with the first NUMA node
    nodeset = bitmap_alloc()
    bitmap_only(nodeset, 0)

    # Test basic set_membind with DEFAULT policy
    set_membind(topo.hdl, nodeset, hwloc_membind_policy_t.HWLOC_MEMBIND_DEFAULT, 0)
    policy = get_membind(topo.hdl, nodeset, 0)
    assert policy == hwloc_membind_policy_t.HWLOC_MEMBIND_FIRSTTOUCH

    # Test with BIND policy
    set_membind(topo.hdl, nodeset, hwloc_membind_policy_t.HWLOC_MEMBIND_BIND, 0)
    policy = get_membind(topo.hdl, nodeset, 0)
    assert policy == hwloc_membind_policy_t.HWLOC_MEMBIND_BIND

    # Test with strict,
    set_membind(
        topo.hdl,
        nodeset,
        hwloc_membind_policy_t.HWLOC_MEMBIND_BIND,
        hwloc_membind_flags_t.HWLOC_MEMBIND_STRICT,
    )
    policy = get_membind(topo.hdl, nodeset, 0)
    assert policy == hwloc_membind_policy_t.HWLOC_MEMBIND_BIND

    set_membind(
        topo.hdl,
        nodeset,
        hwloc_membind_policy_t.HWLOC_MEMBIND_DEFAULT,
        0,
    )

    bitmap_free(nodeset)


@pytest.mark.xfail(
    "Linux" == platform.system(),
    reason="HwLoc not implemented.",
    raises=NotImplementedError,
)
def test_proc_membind() -> None:
    "Bind process memory."
    topo = Topology()

    # Create a nodeset with the first NUMA node
    nodeset = bitmap_alloc()
    bitmap_only(nodeset, 0)
    pid = os.getpid()
    phdl = _open_proc_handle(pid, False)

    # Set proc membind first
    set_proc_membind(
        topo.hdl,
        phdl,
        nodeset,
        hwloc_membind_policy_t.HWLOC_MEMBIND_BIND,
        hwloc_membind_flags_t.HWLOC_MEMBIND_STRICT
        | hwloc_membind_flags_t.HWLOC_MEMBIND_BYNODESET,
    )
    policy = get_proc_membind(topo.hdl, phdl, nodeset, 0)
    set_proc_membind(
        topo.hdl,
        phdl,
        nodeset,
        hwloc_membind_policy_t.HWLOC_MEMBIND_DEFAULT,
        0,
    )

    bitmap_free(nodeset)
    _close_proc_handle(phdl)


def test_area_membind() -> None:
    """Test the set_area_membind and get_area_membind functions."""

    topo = Topology()

    # Create a nodeset with the first NUMA node
    nodeset = bitmap_alloc()
    bitmap_only(nodeset, 0)

    result_nodeset = bitmap_alloc()

    # Allocate a memory area for testing
    size = 1024 * 1024  # 1MB
    # buf = (ctypes.c_char * size)()
    addr = cmalloc(size)

    # Test basic set_area_membind with DEFAULT policy
    set_area_membind(
        topo.hdl,
        addr,
        size,
        nodeset,
        hwloc_membind_policy_t.HWLOC_MEMBIND_DEFAULT,
        hwloc_membind_flags_t.HWLOC_MEMBIND_PROCESS,
    )
    policy = get_area_membind(
        topo.hdl,
        addr,
        size,
        result_nodeset,
        hwloc_membind_flags_t.HWLOC_MEMBIND_PROCESS,
    )
    assert policy == hwloc_membind_policy_t.HWLOC_MEMBIND_FIRSTTOUCH

    # Test with BIND policy
    set_area_membind(
        topo.hdl,
        addr,
        size,
        nodeset,
        hwloc_membind_policy_t.HWLOC_MEMBIND_BIND,
        hwloc_membind_flags_t.HWLOC_MEMBIND_PROCESS,
    )
    policy = get_area_membind(
        topo.hdl,
        addr,
        size,
        result_nodeset,
        hwloc_membind_flags_t.HWLOC_MEMBIND_PROCESS,
    )
    assert policy == hwloc_membind_policy_t.HWLOC_MEMBIND_BIND

    # Test with strict flag
    set_area_membind(
        topo.hdl,
        addr,
        size,
        nodeset,
        hwloc_membind_policy_t.HWLOC_MEMBIND_BIND,
        hwloc_membind_flags_t.HWLOC_MEMBIND_STRICT,
    )
    policy = get_area_membind(
        topo.hdl, addr, size, result_nodeset, hwloc_membind_flags_t.HWLOC_MEMBIND_STRICT
    )
    assert policy == hwloc_membind_policy_t.HWLOC_MEMBIND_BIND

    # Test INTERLEAVE policy
    set_area_membind(
        topo.hdl,
        addr,
        size,
        nodeset,
        hwloc_membind_policy_t.HWLOC_MEMBIND_INTERLEAVE,
        0,
    )
    policy = get_area_membind(
        topo.hdl,
        addr,
        size,
        result_nodeset,
        hwloc_membind_flags_t.HWLOC_MEMBIND_PROCESS,
    )
    assert policy == hwloc_membind_policy_t.HWLOC_MEMBIND_INTERLEAVE

    # Clean up
    bitmap_free(nodeset)
    bitmap_free(result_nodeset)

    cfree(addr)
