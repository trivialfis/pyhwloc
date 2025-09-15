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

import copy
import os
import platform
import threading

import pytest

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


def test_cpubind() -> None:
    with Topology.from_this_system() as topo:
        # cpu_bind
        orig = topo.get_cpubind()
        target = copy.copy(orig)
        idx = target.first()
        topo.set_cpubind(set([idx]))
        new = topo.get_cpubind()
        assert new[0] is True
        assert new.weight() == 1

        topo.set_cpubind(orig)
        new = topo.get_cpubind()
        assert new == orig
        # proc cpubind
        pid = os.getpid()
        orig_proc = topo.get_proc_cpubind(pid)
        target_proc = copy.copy(orig_proc)
        idx = target_proc.first()
        topo.set_proc_cpubind(pid, set([idx]))
        new_proc = topo.get_proc_cpubind(pid)
        assert new_proc[0] is True
        assert new_proc.weight() == 1

        topo.set_proc_cpubind(pid, orig_proc)
        new_proc = topo.get_proc_cpubind(pid)
        assert new_proc == orig_proc

        # Err
        invalid_pid = 999999

        with pytest.raises(ValueError):
            topo.get_proc_cpubind(invalid_pid)

        with pytest.raises(ValueError):
            topo.set_proc_cpubind(invalid_pid, set([0]))


def test_thread_cpubind() -> None:
    with Topology.from_this_system() as topo:
        thread_id = threading.get_ident()
        orig = topo.get_thread_cpubind(thread_id)
        target = copy.copy(orig)
        idx = target.first()

        obj = topo.get_obj_by_type(ObjType.HWLOC_OBJ_PU, idx)
        assert obj is not None
        topo.set_thread_cpubind(thread_id, obj)

        new = topo.get_thread_cpubind(thread_id)
        assert new[0] is True
        assert new.weight() == 1

        topo.set_thread_cpubind(thread_id, orig)
        new = topo.get_thread_cpubind(thread_id)
        assert new == orig
