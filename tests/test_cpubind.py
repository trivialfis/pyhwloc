# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
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


@pytest.mark.skipif(
    "Windows" == platform.system(),
    reason="HwLoc not implemented.",
)
def test_get_proc_last_cpu_loc() -> None:
    def run(topo: Topology, flags: int) -> None:
        pid = os.getpid()

        loc = topo.get_proc_last_cpu_location(pid, flags)
        assert isinstance(loc, Bitmap)

        idx = loc.first()
        assert idx >= 0
        obj = topo.get_obj_by_type(ObjType.PU, idx)
        assert obj is not None
        assert obj.type == ObjType.PU

        # W/O proc
        loc = topo.get_last_cpu_location(flags)
        assert isinstance(loc, Bitmap)
        idx = loc.first()
        assert idx >= 0
        obj = topo.get_obj_by_type(ObjType.PU, idx)
        assert obj is not None
        assert obj.type == ObjType.PU

    with Topology.from_this_system() as topo:
        run(topo, 0)

        if platform.system() == "Linux":
            run(topo, CpuBindFlags.THREAD)


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

        if platform.system() == "Windows":
            Err: type[Exception] = OSError
        else:
            Err = ValueError

        with pytest.raises(Err):
            topo.get_proc_cpubind(invalid_pid)

        with pytest.raises(Err):
            topo.set_proc_cpubind(invalid_pid, set([0]))


def test_thread_cpubind() -> None:
    with Topology.from_this_system() as topo:
        thread_id = threading.get_ident()
        orig = topo.get_thread_cpubind(thread_id)
        target = copy.copy(orig)
        idx = target.first()

        obj = topo.get_obj_by_type(ObjType.PU, idx)
        assert obj is not None
        topo.set_thread_cpubind(thread_id, obj)

        new = topo.get_thread_cpubind(thread_id)
        assert new[0] is True
        assert new.weight() == 1

        topo.set_thread_cpubind(thread_id, orig)
        new = topo.get_thread_cpubind(thread_id)
        assert new == orig
