# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import os
import platform

import pytest

from pyhwloc.hwloc.bitmap import (
    bitmap_alloc,
    bitmap_free,
    bitmap_only,
)
from pyhwloc.hwloc.core import (
    MemBindFlags,
    MemBindPolicy,
    _close_proc_handle,
    _open_proc_handle,
    get_area_membind,
    get_membind,
    get_proc_membind,
    set_area_membind,
    set_membind,
    set_proc_membind,
)
from pyhwloc.hwloc.libc import free as cfree
from pyhwloc.hwloc.libc import malloc as cmalloc

from .test_core import Topology
from .utils import has_nice_cap

DFT_POLICY = (
    MemBindPolicy.FIRSTTOUCH
    if platform.system() == "Linux"
    # AIX, HP-UX, OSF, Solaris, Windows
    else MemBindPolicy.BIND
)


@pytest.mark.skipif(
    condition=not has_nice_cap(), reason="Running in a sandboxed environment."
)
def test_membind() -> None:
    """Test the set_membind function with different policies and flags."""
    topo = Topology()

    # Create a nodeset with the first NUMA node
    nodeset = bitmap_alloc()
    bitmap_only(nodeset, 0)

    # Test basic set_membind with DEFAULT policy
    set_membind(topo.hdl, nodeset, MemBindPolicy.DEFAULT, 0)
    policy = get_membind(topo.hdl, nodeset, 0)
    assert policy == DFT_POLICY

    # Test with BIND policy
    set_membind(topo.hdl, nodeset, MemBindPolicy.BIND, 0)
    policy = get_membind(topo.hdl, nodeset, 0)
    assert policy == MemBindPolicy.BIND

    # Test with strict,
    set_membind(
        topo.hdl,
        nodeset,
        MemBindPolicy.BIND,
        MemBindFlags.STRICT,
    )
    policy = get_membind(topo.hdl, nodeset, 0)
    assert policy == MemBindPolicy.BIND

    set_membind(
        topo.hdl,
        nodeset,
        MemBindPolicy.DEFAULT,
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
        MemBindPolicy.BIND,
        MemBindFlags.STRICT | MemBindFlags.BYNODESET,
    )
    policy = get_proc_membind(topo.hdl, phdl, nodeset, 0)
    assert policy == MemBindPolicy.BIND
    set_proc_membind(
        topo.hdl,
        phdl,
        nodeset,
        MemBindPolicy.DEFAULT,
        0,
    )

    bitmap_free(nodeset)
    _close_proc_handle(phdl)


@pytest.mark.skipif(
    condition=not has_nice_cap() or "Windows" == platform.system(),
    reason="Running in a sandboxed environment or on Windows.",
)
def test_area_membind() -> None:
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
        MemBindPolicy.DEFAULT,
        MemBindFlags.PROCESS,
    )
    policy = get_area_membind(
        topo.hdl,
        addr,
        size,
        result_nodeset,
        MemBindFlags.PROCESS,
    )
    assert policy == MemBindPolicy.FIRSTTOUCH

    # Test with BIND policy
    set_area_membind(
        topo.hdl,
        addr,
        size,
        nodeset,
        MemBindPolicy.BIND,
        MemBindFlags.PROCESS,
    )
    policy = get_area_membind(
        topo.hdl,
        addr,
        size,
        result_nodeset,
        MemBindFlags.PROCESS,
    )
    assert policy == MemBindPolicy.BIND

    # Test with strict flag
    set_area_membind(
        topo.hdl,
        addr,
        size,
        nodeset,
        MemBindPolicy.BIND,
        MemBindFlags.STRICT,
    )
    policy = get_area_membind(topo.hdl, addr, size, result_nodeset, MemBindFlags.STRICT)
    assert policy == MemBindPolicy.BIND

    # Test INTERLEAVE policy
    set_area_membind(
        topo.hdl,
        addr,
        size,
        nodeset,
        MemBindPolicy.INTERLEAVE,
        0,
    )
    policy = get_area_membind(
        topo.hdl,
        addr,
        size,
        result_nodeset,
        MemBindFlags.PROCESS,
    )
    assert policy == MemBindPolicy.INTERLEAVE

    # Clean up
    bitmap_free(nodeset)
    bitmap_free(result_nodeset)

    cfree(addr)
