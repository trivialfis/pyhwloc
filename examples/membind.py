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
from pyhwloc import Topology
from pyhwloc.topology import MemBindPolicy


def bind_np_array() -> None:
    try:
        import numpy as np
    except ImportError:
        return

    array = np.arange(0, 8196)

    with Topology.from_this_system() as topo:
        if not topo.get_support().membind.set_area_membind:
            return

        nodeset, policy = topo.get_area_membind(array.data, 0)
        print(MemBindPolicy(policy).name, nodeset)

        nodeset.only(0)
        topo.set_area_membind(
            array.data, 0, nodeset, MemBindPolicy.HWLOC_MEMBIND_BIND, 0
        )

        nodeset, policy = topo.get_area_membind(array.data, 0)
        print(MemBindPolicy(policy).name, nodeset)


def main() -> None:
    bind_np_array()


if __name__ == "__main__":
    main()
