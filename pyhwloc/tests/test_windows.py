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

pytest.importorskip("pyhwloc.windows", exc_type=ImportError)

from pyhwloc.core import bitmap_alloc, bitmap_free
from pyhwloc.sched import cpuset_to_sched_affinity
from pyhwloc.windows import (
    windows_get_nr_processor_groups,
    windows_get_processor_group_cpuset,
)

from .test_core import Topology


def test_windows_helpers() -> None:
    topo = Topology()
    nr = windows_get_nr_processor_groups(topo.hdl)
    assert nr >= 1

    cpuset = bitmap_alloc()
    windows_get_processor_group_cpuset(topo.hdl, 0, cpuset)
    aff = cpuset_to_sched_affinity(cpuset)
    assert len(aff) >= 1
    bitmap_free(cpuset)
