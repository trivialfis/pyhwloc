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
import ctypes
import os
import platform
import threading

import pytest

from pyhwloc.core import (
    _close_thread_handle,
    _open_thread_handle,
    bitmap_alloc,
    bitmap_free,
    bitmap_isequal,
    bitmap_iszero,
    bitmap_set,
    get_cpubind,
    get_last_cpu_location,
    get_proc_last_cpu_location,
    get_thread_cpubind,
    hwloc_cpubind_flags_t,
    hwloc_pid_t,
    hwloc_thread_t,
    set_cpubind,
    set_thread_cpubind,
)
from pyhwloc.sched import cpuset_to_sched_affinity

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
    run_cpubind(hwloc_cpubind_flags_t.HWLOC_CPUBIND_STRICT)


def test_thread_cpubind() -> None:
    topo = Topology()

    # Get current thread ID
    current_thread = threading.get_ident()
    thread_id = threading.get_native_id()

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
