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

import pickle

import pytest

from pyhwloc.hwobject import Object, ObjType
from pyhwloc.topology import Topology


def test_get_root_object() -> None:
    with Topology.from_synthetic("node:2 core:2 pu:2") as topo:
        # Get root object (should be at depth 0, index 0)
        root = topo.get_obj_by_depth(0, 0)
        assert root == topo.get_root_obj()
        assert root is not None
        # Root should be at depth 0
        assert root.depth == 0
        # Root should have logical index 0
        assert root.logical_index == 0
        # Root should be a machine type
        assert root.type == ObjType.HWLOC_OBJ_MACHINE
        assert root.parent is None
        # Root should have children (the NUMA nodes)
        assert root.arity > 0
        assert root.first_child is not None


def test_invalid_topo() -> None:
    with Topology.from_synthetic("node:2 core:2 pu:2") as topo:
        root = topo.get_obj_by_depth(0, 0)
        assert root is not None
        assert root.type is not None

    # After context exits, accessing the object should raise an error
    with pytest.raises(RuntimeError, match="Topology is invalid"):
        _ = root.native_handle

    with pytest.raises(RuntimeError, match="Topology is invalid"):
        _ = root.type


def test_object_properties() -> None:
    with Topology.from_synthetic("node:2 core:2 pu:4") as topo:
        # Get a CPU object to test properties
        cpu = next(topo.iter_cpus(), None)
        assert cpu is not None

        # Test basic properties
        assert isinstance(cpu.type, ObjType)
        assert cpu.type == ObjType.HWLOC_OBJ_PU
        assert cpu.depth >= 0
        assert cpu.logical_index >= 0
        assert cpu.sibling_rank >= 0
        assert cpu.arity >= 0
        assert cpu.memory_arity >= 0
        assert cpu.io_arity >= 0
        assert cpu.misc_arity >= 0

        # Test optional properties
        assert cpu.subtype is None or isinstance(cpu.subtype, str)
        assert cpu.name is None or isinstance(cpu.name, str)
        assert cpu.total_memory >= 0

        # Test boolean properties
        assert isinstance(cpu.symmetric_subtree, bool)

        # Test bitmap properties
        assert cpu.cpuset is not None
        assert cpu.complete_cpuset is not None

        # Test navigation properties
        assert cpu.parent is not None  # CPU should have a parent (core)
        assert isinstance(cpu.parent, Object)


def test_object_navigation() -> None:
    with Topology.from_synthetic("node:2 core:2 pu:2") as topo:
        root = topo.get_obj_by_depth(0, 0)
        assert root is not None

        # Test children iteration
        children = list(root.iter_children())
        assert len(children) == root.arity
        assert len(children) > 0

        # Test sibling iteration
        if len(children) > 1:
            first_child = children[0]
            siblings = list(first_child.iter_siblings())
            assert len(siblings) >= 2  # At least the child itself and one sibling
            assert first_child in siblings

        # Test parent-child relationships
        for child in children:
            assert child.parent == root

        # Test next/prev sibling relationships
        if len(children) >= 2:
            first = children[0]
            second = children[1]
            assert first.next_sibling == second
            assert second.prev_sibling == first


def test_object_string_representation() -> None:
    with Topology.from_synthetic("node:2 core:2 pu:2") as topo:
        # Test root object
        root = topo.get_obj_by_depth(0, 0)
        assert root is not None

        # Test __str__ method
        str_repr = str(root)
        assert "MACHINE" in str_repr
        assert "#0" in str_repr  # Should show logical index

        # Test __repr__ method
        repr_str = repr(root)
        assert "Object(" in repr_str
        assert "type=" in repr_str
        assert "logical_index=" in repr_str
        assert "depth=" in repr_str

        # Test CPU object representation
        cpu = next(topo.iter_cpus(), None)
        if cpu is not None:
            cpu_str = str(cpu)
            assert "PU" in cpu_str
            assert f"#{cpu.logical_index}" in cpu_str


def test_object_equality_and_hashing() -> None:
    with Topology.from_synthetic("node:2 core:2 pu:2") as topo:
        # Get same object twice
        obj1 = topo.get_obj_by_depth(0, 0)
        obj2 = topo.get_obj_by_depth(0, 0)

        assert obj1 is not None
        assert obj2 is not None

        # Should be equal (same underlying pointer)
        assert obj1 == obj2
        assert hash(obj1) == hash(obj2)

        # Get different objects
        if topo.depth > 1:
            obj3 = topo.get_obj_by_depth(1, 0)
            assert obj3 is not None
            assert obj1 != obj3
            # Hash may or may not be different, but objects should be unequal

        # Test inequality with non-Object
        assert obj1 != "not an object"
        assert obj1 != 42

        with pytest.raises(ValueError, match="cannot be pickled"):
            pickle.dumps(obj1)
