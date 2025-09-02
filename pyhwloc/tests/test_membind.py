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
from pyhwloc.core import (
    bitmap_alloc,
    bitmap_free,
    bitmap_only,
    get_membind,
    hwloc_membind_flags_t,
    hwloc_membind_policy_t,
    set_membind,
)

from .test_core import Topology


def test_set_membind() -> None:
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

    bitmap_free(nodeset)
