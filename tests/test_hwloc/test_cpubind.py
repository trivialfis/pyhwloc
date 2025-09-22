# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import os
import platform
import threading

import pytest

from pyhwloc.hwloc.bitmap import (
    bitmap_alloc,
    bitmap_free,
    bitmap_isequal,
    bitmap_iszero,
    bitmap_set,
)
from pyhwloc.hwloc.core import (
    CpuBindFlags,
    _close_thread_handle,
    _open_thread_handle,
    get_cpubind,
    get_last_cpu_location,
    get_proc_last_cpu_location,
    get_thread_cpubind,
    hwloc_pid_t,
    set_cpubind,
    set_thread_cpubind,
)
from pyhwloc.hwloc.sched import cpuset_to_sched_affinity

from .test_core import Topology

##################################
# CPU binding functions
##################################


def run_cpubind(flags: int) -> None:
    topo = Topology()

    orig_cpuset = bitmap_alloc()
    get_cpubind(topo.hdl, orig_cpuset, flags)

    # Create a simple cpuset with just CPU 0
    cpuset = bitmap_alloc()
    pu_id = 1
    bitmap_set(cpuset, pu_id)

    set_cpubind(topo.hdl, cpuset, flags)

    test_cpuset = bitmap_alloc()
    get_cpubind(topo.hdl, test_cpuset, flags)
    assert not bitmap_iszero(test_cpuset)

    aff = cpuset_to_sched_affinity(test_cpuset)
    if hasattr(os, "sched_getaffinity"):
        assert aff == set([1]) == os.sched_getaffinity(0)

    aff = cpuset_to_sched_affinity(orig_cpuset)
    set_cpubind(topo.hdl, orig_cpuset, flags)

    get_cpubind(topo.hdl, test_cpuset, flags)
    assert bitmap_isequal(test_cpuset, orig_cpuset)

    bitmap_free(cpuset)
    bitmap_free(orig_cpuset)
    bitmap_free(test_cpuset)


def test_cpubind() -> None:
    run_cpubind(0)  # The most portable way
    # Not so portable?
    run_cpubind(CpuBindFlags.STRICT)


def test_thread_cpubind() -> None:
    topo = Topology()

    # Get current thread ID
    thread_id = threading.get_ident()
    # For Windows, `threading.get_ident` and `threading.get_native_id` are the same. On
    # Linux, only `get_ident` returns the valid thread handle, while `get_native_id`
    # returns an integer.
    # print(thread_id, threading.get_native_id())

    thread_hdl = _open_thread_handle(thread_id, read_only=False)

    # Preserve the original mask.
    orig_cpuset = bitmap_alloc()
    get_thread_cpubind(topo.hdl, thread_hdl, orig_cpuset, 0)
    orig_aff = cpuset_to_sched_affinity(orig_cpuset)

    # Create a simple cpuset with just CPU 0
    cpuset = bitmap_alloc()
    bitmap_set(cpuset, 0)

    # Test that set_thread_cpubind doesn't raise an exception with valid inputs
    set_thread_cpubind(topo.hdl, thread_hdl, cpuset, 0)
    get_thread_cpubind(topo.hdl, thread_hdl, cpuset, 0)

    aff = cpuset_to_sched_affinity(cpuset)
    assert aff == set([0])

    set_thread_cpubind(topo.hdl, thread_hdl, orig_cpuset, 0)
    get_thread_cpubind(topo.hdl, thread_hdl, cpuset, 0)
    aff = cpuset_to_sched_affinity(cpuset)
    assert aff == orig_aff

    bitmap_free(cpuset)
    bitmap_free(orig_cpuset)

    _close_thread_handle(thread_hdl)


@pytest.mark.xfail(
    "Windows" == platform.system(),
    reason="HwLoc not implemented.",
    raises=NotImplementedError,
)
def test_get_last_cpu_location() -> None:
    topo = Topology()

    cpuset = bitmap_alloc()
    get_last_cpu_location(topo.hdl, cpuset, 0)
    assert not bitmap_iszero(cpuset)

    bitmap_free(cpuset)

    current_pid = os.getpid()
    pid = hwloc_pid_t(current_pid)

    cpuset = bitmap_alloc()
    get_proc_last_cpu_location(topo.hdl, pid, cpuset, 0)
    assert not bitmap_iszero(cpuset)
