# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import pytest

from pyhwloc import from_this_system
from pyhwloc.bitmap import Bitmap
from pyhwloc.hwobject import ObjType
from pyhwloc.memattrs import MemAttrFlag, MemAttrId
from pyhwloc.topology import TypeFilter


def test_get_memattrs() -> None:
    with from_this_system().set_all_types_filter(TypeFilter.KEEP_ALL) as topo:
        memattrs = topo.get_memattrs()
        attr = memattrs.get(MemAttrId.CAPACITY)
        attr_by_name = memattrs.get(attr.name)
        assert attr == attr_by_name
        assert attr.name == "Capacity"

        assert attr.needs_initiator is False
        assert attr.higher_first is True
        assert attr.lower_first is False

        obj = topo.get_obj_by_type(ObjType.NUMANODE, 0)
        assert obj is not None
        v = attr.get_value(obj)
        assert isinstance(v, int)

        attr = memattrs.register(
            "foo",
            [
                MemAttrFlag.NEED_INITIATOR,
                MemAttrFlag.HIGHER_FIRST,
            ],
        )
        assert memattrs.get("foo") == attr
        assert attr.needs_initiator is True
        assert attr.higher_first is True
        assert attr.lower_first is False


def test_memattrs_setter() -> None:
    with from_this_system().set_all_types_filter(TypeFilter.KEEP_ALL) as topo:
        memattrs = topo.get_memattrs()
        attr = memattrs.get(MemAttrId.BANDWIDTH)
        assert attr.name == "Bandwidth"

        assert attr.needs_initiator is True
        assert attr.higher_first is True
        assert attr.lower_first is False

        numa = topo.get_obj_by_type(ObjType.NUMANODE, 0)
        assert numa is not None
        core = topo.get_obj_by_type(ObjType.CORE, 0)
        assert core is not None

        v = 2345
        attr.set_value(numa, v, core)

        bitmap = attr.get_initiators(numa)[0][0]
        assert bitmap == core

        inits = attr.get_initiators(numa)
        assert len(inits) == 1
        assert inits[0][0] == core
        assert inits[0][1] == v

        targets = attr.get_targets(core)
        assert len(targets) == 1
        assert targets[0][0] == numa
        assert targets[0][1] == v


def test_memattrs_find_best() -> None:
    with from_this_system().set_all_types_filter(TypeFilter.KEEP_ALL) as topo:
        memattrs = topo.get_memattrs()

        attr = memattrs.register(
            "foo",
            [
                MemAttrFlag.NEED_INITIATOR,
                MemAttrFlag.LOWER_FIRST,
            ],
        )

        targets = attr.get_targets()
        assert not targets

        numa = topo.get_obj_by_type(ObjType.NUMANODE, 0)
        assert numa is not None
        core = topo.get_obj_by_type(ObjType.CORE, 0)
        v = 2345
        attr.set_value(numa, v, core)
        targets = attr.get_targets()
        assert len(targets) == 1 and targets[0][0] == numa and targets[0][1] == 0
        got = attr.get_value(numa, core)
        assert got == v
        target = attr.get_best_target(core)
        assert target[0] == numa and target[1] == v

        assert attr.get_best_initiator(numa)[0] == core
        assert attr.get_best_initiator(numa)[1] == 2345


def test_local_numa_nodes() -> None:
    with from_this_system().set_all_types_filter(TypeFilter.KEEP_ALL) as topo:
        memattrs = topo.get_memattrs()

        with pytest.raises(TypeError, match="Initiator cannot be None"):
            memattrs.get_local_numa_nodes(None)  # type: ignore

        # Test with core initiator
        core = topo.get_obj_by_type(ObjType.CORE, 0)
        if core is not None:
            local_nodes = memattrs.get_local_numa_nodes(core)
            assert isinstance(local_nodes, list)
            for node in local_nodes:
                assert node.type == ObjType.NUMANODE

        # Test with a sched set initiator
        cpu_set = {0}
        local_nodes = memattrs.get_local_numa_nodes(cpu_set)
        assert isinstance(local_nodes, list)
        for node in local_nodes:
            assert node.type == ObjType.NUMANODE

        # Test with a bitmap initiator
        bitmap = Bitmap.from_sched_set({0})
        local_nodes = memattrs.get_local_numa_nodes(bitmap)
        assert isinstance(local_nodes, list)
        for node in local_nodes:
            assert node.type == ObjType.NUMANODE
