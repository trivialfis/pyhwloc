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

import platform

import pytest

from pyhwloc.core import (
    bitmap_alloc,
    bitmap_free,
    bitmap_isequal,
    bitmap_iszero,
    bitmap_only,
)

linux = pytest.importorskip("pyhwloc.linux")

from pyhwloc.linux import get_tid_cpubind, get_tid_last_cpu_location, set_tid_cpubind

from .test_core import Topology


@pytest.mark.skipif(
    condition=platform.system() != "Linux", reason="Linux-specific test"
)
def test_tid_cpubind() -> None:
    topo = Topology()
    tid = 0

    # Allocate cpusets for testing
    original_cpuset = bitmap_alloc()
    test_cpuset = bitmap_alloc()
    retrieved_cpuset = bitmap_alloc()

    get_tid_cpubind(topo.hdl, tid, original_cpuset)

    # Create a test CPU set (bind to CPU 0 only)
    bitmap_only(test_cpuset, 0)
    # Roundtrip
    set_tid_cpubind(topo.hdl, tid, test_cpuset)
    get_tid_cpubind(topo.hdl, tid, retrieved_cpuset)

    assert bitmap_isequal(test_cpuset, retrieved_cpuset)

    # Restore original CPU binding
    set_tid_cpubind(topo.hdl, tid, original_cpuset)

    bitmap_free(original_cpuset)
    bitmap_free(test_cpuset)
    bitmap_free(retrieved_cpuset)


@pytest.mark.skipif(
    condition=platform.system() != "Linux", reason="Linux-specific test"
)
def test_get_tid_last_cpu_location() -> None:
    topo = Topology()
    cpuset = bitmap_alloc()
    get_tid_last_cpu_location(topo.hdl, 0, cpuset)
    assert not bitmap_iszero(cpuset)
    bitmap_free(cpuset)
