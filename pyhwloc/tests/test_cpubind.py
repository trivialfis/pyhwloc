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
import platform

from pyhwloc import Topology
from pyhwloc.bitmap import Bitmap
from pyhwloc.hwobject import ObjType
from pyhwloc.topology import CpuBindFlags


def test_get_proc_last_cpu_loc() -> None:
    def run(topo: Topology, flags: int) -> None:
        pid = os.getpid()

        loc = topo.get_proc_last_cpu_location(pid, flags)
        assert isinstance(loc, Bitmap)

        idx = loc.first()
        assert idx >= 0
        obj = topo.get_obj_by_type(ObjType.HWLOC_OBJ_PU, idx)
        assert obj is not None
        assert obj.type == ObjType.HWLOC_OBJ_PU

        # W/O proc
        loc = topo.get_last_cpu_location(flags)
        assert isinstance(loc, Bitmap)
        idx = loc.first()
        assert idx >= 0
        obj = topo.get_obj_by_type(ObjType.HWLOC_OBJ_PU, idx)
        assert obj is not None
        assert obj.type == ObjType.HWLOC_OBJ_PU

    with Topology.from_this_system() as topo:
        run(topo, 0)

        if platform.system() == "Linux":
            run(topo, CpuBindFlags.HWLOC_CPUBIND_THREAD)
