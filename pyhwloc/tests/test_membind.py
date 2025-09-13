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

from pyhwloc import Topology
from pyhwloc.bitmap import Bitmap
from pyhwloc.topology import MemBindFlags, MemBindPolicy


def reset(orig_cpuset: Bitmap, topo: Topology) -> None:
    topo.set_memory_bind(orig_cpuset, MemBindPolicy.HWLOC_MEMBIND_DEFAULT, 0)
    orig_cpuset, policy = topo.get_memory_bind()
    assert policy in (
        MemBindPolicy.HWLOC_MEMBIND_FIRSTTOUCH,
        MemBindPolicy.HWLOC_MEMBIND_DEFAULT,
    )


def with_tpool(worker: Callable, *args: Any) -> None:
    futures = []
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as execu:
        for i in range(os.cpu_count()):
            fut = execu.submit(worker, MemBindPolicy.HWLOC_MEMBIND_BIND)

            futures.append(fut)

    assert all(fut.result() for fut in futures)


def test_membind() -> None:
    with Topology.from_this_system() as topo:
        orig_cpuset, policy = topo.get_memory_bind()
        assert policy in (
            MemBindPolicy.HWLOC_MEMBIND_FIRSTTOUCH,
            MemBindPolicy.HWLOC_MEMBIND_DEFAULT,
        )
        assert orig_cpuset.weight == os.cpu_count()

        target_set = Bitmap()
        target_set.set(0)
        # neither HWLOC_MEMBIND_PROCESS or HWLOC_MEMBIND_THREAD is used, the current
        # process is assumed to be single-threaded
        topo.set_memory_bind(target_set, MemBindPolicy.HWLOC_MEMBIND_BIND, 0)

        cpuset_1, policy_1 = topo.get_memory_bind()
        assert cpuset_1.weight >= 1  # All CPUs in a socket.
        assert policy_1 == MemBindPolicy.HWLOC_MEMBIND_BIND, MemBindPolicy(
            policy_1
        ).name

        # Test the child threads correctly inherits the bind policy
        def worker_0(exp: MemBindFlags) -> bool:
            cpuset, policy = topo.get_memory_bind()
            assert cpuset.weight >= 1
            return policy == exp

        def worker_1(exp: MemBindFlags) -> bool:
            with Topology.from_this_system() as topo:
                cpuset, policy = topo.get_memory_bind()
                assert cpuset.weight >= 1
                return policy == exp

        with_tpool(worker_0, MemBindPolicy.HWLOC_MEMBIND_BIND)
        with_tpool(worker_1, MemBindPolicy.HWLOC_MEMBIND_BIND)
        # -- Reset
        reset(orig_cpuset, topo)

        # Test launching thread before setting membind
        fut = Future()

        def worker_2() -> None:
            res = worker_0(MemBindPolicy.HWLOC_MEMBIND_DEFAULT)
            fut.set_result(res)

        t = threading.Thread(name="worker", target=worker_2)
        topo.set_memory_bind(target_set, MemBindPolicy.HWLOC_MEMBIND_BIND, 0)
        t.start()
        t.join()
        assert not fut.result()
        # -- Reset
        reset(orig_cpuset, topo)

        # Test launching thread before setting membind with process
        if topo.get_support().membind.set_proc_membind:
            # Linux doesn't support process-based membind
            t = threading.Thread(name="worker", target=worker_2)
            topo.set_memory_bind(
                target_set,
                MemBindPolicy.HWLOC_MEMBIND_BIND,
                MemBindFlags.HWLOC_MEMBIND_PROCESS,
            )
            t.start()
            t.join()
            assert not fut.result()
        # -- Reset
        reset(orig_cpuset, topo)
