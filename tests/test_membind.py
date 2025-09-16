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
from __future__ import annotations

import os
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable

import pytest

from pyhwloc import Topology
from pyhwloc.bitmap import Bitmap
from pyhwloc.topology import MemBindFlags, MemBindPolicy

from .test_hwloc.test_membind import DFT_POLICY, has_nice_cap


def reset(orig_cpuset: Bitmap, topo: Topology) -> None:
    topo.set_membind(orig_cpuset, MemBindPolicy.HWLOC_MEMBIND_DEFAULT, 0)
    orig_cpuset, policy = topo.get_membind()
    assert policy in (DFT_POLICY, MemBindPolicy.HWLOC_MEMBIND_DEFAULT)


def with_tpool(worker: Callable, *args: Any) -> None:
    cnt = os.cpu_count()
    assert cnt is not None
    n_workers = min(cnt, 8)
    futures = []
    with ThreadPoolExecutor(max_workers=n_workers) as execu:
        n_cpus = os.cpu_count()
        assert n_cpus
        for i in range(n_cpus):
            fut = execu.submit(worker, MemBindPolicy.HWLOC_MEMBIND_BIND)

            futures.append(fut)

    assert all(fut.result() for fut in futures)


def worker_1(exp: MemBindFlags) -> bool:
    with Topology.from_this_system() as topo:
        cpuset, policy = topo.get_membind()
        assert cpuset.weight() >= 1
        return policy == exp


@pytest.mark.skipif(
    condition=not has_nice_cap(), reason="Running in a sandboxed environment."
)
def test_membind() -> None:
    with Topology.from_this_system() as topo:
        orig_cpuset, policy = topo.get_membind()

        assert policy in (DFT_POLICY, MemBindPolicy.HWLOC_MEMBIND_DEFAULT)
        assert orig_cpuset.weight() == os.cpu_count()

        target_set = Bitmap()
        target_set.set(0)
        # neither HWLOC_MEMBIND_PROCESS or HWLOC_MEMBIND_THREAD is used, the current
        # process is assumed to be single-threaded
        topo.set_membind(target_set, MemBindPolicy.HWLOC_MEMBIND_BIND, 0)

        cpuset_1, policy_1 = topo.get_membind()
        assert cpuset_1.weight() >= 1  # All CPUs in a socket.
        assert policy_1 == MemBindPolicy.HWLOC_MEMBIND_BIND, MemBindPolicy(
            policy_1
        ).name

        # Test the child threads correctly inherits the bind policy
        def worker_0(exp: MemBindPolicy) -> bool:
            cpuset, policy = topo.get_membind()
            assert cpuset.weight() >= 1
            return policy == exp

        with_tpool(worker_0, MemBindPolicy.HWLOC_MEMBIND_BIND)
        with_tpool(worker_1, MemBindPolicy.HWLOC_MEMBIND_BIND)
        # -- Reset
        reset(orig_cpuset, topo)

        # Test launching thread before setting membind
        def worker_2(fut: Future, exp: MemBindPolicy) -> None:
            res = worker_0(exp)
            fut.set_result(res)

        fut: Future[bool] = Future()
        t = threading.Thread(
            name="worker",
            target=worker_2,
            args=(fut, MemBindPolicy.HWLOC_MEMBIND_DEFAULT),
        )
        topo.set_membind(
            target_set,
            MemBindPolicy.HWLOC_MEMBIND_BIND,
            [MemBindFlags.HWLOC_MEMBIND_STRICT, MemBindFlags.HWLOC_MEMBIND_THREAD],
        )
        t.start()
        t.join()
        assert not fut.result()
        # -- Reset
        reset(orig_cpuset, topo)

        # Test launching thread before setting membind with process
        if topo.get_support().membind.set_proc_membind:
            # Linux doesn't support process-based membind, this is not really testing
            # anything since Windows doesn't support any types of membind policy other
            # than bind.
            fut = Future()
            t = threading.Thread(
                name="worker",
                target=worker_2,
                args=(fut, MemBindPolicy.HWLOC_MEMBIND_DEFAULT),
            )
            topo.set_membind(
                target_set,
                MemBindPolicy.HWLOC_MEMBIND_BIND,
                MemBindFlags.HWLOC_MEMBIND_PROCESS,
            )
            t.start()
            t.join()
            assert not fut.result()
        # -- Reset
        reset(orig_cpuset, topo)

        # Test migrate
        if topo.get_support().membind.migrate_membind:
            fut = Future()
            t = threading.Thread(
                name="worker",
                target=worker_2,
                args=(fut, MemBindPolicy.HWLOC_MEMBIND_BIND),
            )
            topo.set_membind(
                target_set,
                MemBindPolicy.HWLOC_MEMBIND_BIND,
                [MemBindFlags.HWLOC_MEMBIND_STRICT, MemBindFlags.HWLOC_MEMBIND_MIGRATE],
            )
            _, policy = topo.get_membind()
            assert policy == MemBindPolicy.HWLOC_MEMBIND_BIND
            t.start()
            t.join()
            assert fut.result()
        # -- Reset
        reset(orig_cpuset, topo)


@pytest.mark.skipif(
    condition=not has_nice_cap(), reason="Running in a sandboxed environment."
)
def test_area_membind() -> None:
    kb = 64
    with Topology.from_this_system() as topo:
        if not topo.get_support().membind.set_area_membind:
            pytest.skip("Current system doesn't support set_area_membind")
        # Test with memoryview
        data = bytearray(1024 * kb)
        mv = memoryview(data)
        bitmap, policy = topo.get_area_membind(mv)
        assert bitmap.weight() >= 1
        assert policy in (DFT_POLICY, MemBindPolicy.HWLOC_MEMBIND_DEFAULT)

        target_set = Bitmap()
        target_set.set(0)

        topo.set_area_membind(
            mv,
            target_set,
            MemBindPolicy.HWLOC_MEMBIND_BIND,
            [MemBindFlags.HWLOC_MEMBIND_STRICT],
        )

        bitmap, policy = topo.get_area_membind(mv)
        assert bitmap.weight() >= 1
        assert policy == MemBindPolicy.HWLOC_MEMBIND_BIND

        with pytest.raises(ValueError):
            topo.get_area_membind(mv, 123456)


def test_proc_membind() -> None:
    with Topology.from_this_system() as topo:
        if not topo.get_support().membind.set_thisproc_membind:
            pytest.skip("Current system doesn't support set_thisproc_membind")

        pid = os.getpid()
        orig_cpuset, policy = topo.get_proc_membind(pid)

        target_set = Bitmap()
        target_set.set(0)
        target_set.to_string()
        topo.set_proc_membind(pid, target_set, MemBindPolicy.HWLOC_MEMBIND_BIND, 0)

        bitmap, policy = topo.get_proc_membind(pid, 0)
        assert policy == MemBindPolicy.HWLOC_MEMBIND_BIND
        assert bitmap.weight() > 1

        reset(orig_cpuset, topo)
