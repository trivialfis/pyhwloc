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

"""Tests for the Distance class and distance functionality."""

import pytest

from pyhwloc.distance import Distance, Kind
from pyhwloc.topology import Topology
from pyhwloc.hwobject import ObjType


def test_distance_basic_functionality() -> None:
    """Test basic Distance class functionality."""
    with Topology() as topo:
        # Get all distances from system topology
        distances = topo.get_distances()

        # Even if no distances exist, the method should work
        assert isinstance(distances, list)

        # If we have distances, test their properties
        for dist in distances:
            assert isinstance(dist, Distance)
            assert isinstance(dist.nbobjs, int)
            assert dist.nbobjs >= 0
            assert isinstance(dist.kind, Kind)
            assert isinstance(dist.shape, tuple)
            assert len(dist.shape) == 2
            assert dist.shape == (dist.nbobjs, dist.nbobjs)


def test_distance_with_custom_distances() -> None:
    """Test Distance class with custom added distances."""
    with Topology() as topo:
        # Find NUMA nodes to create distances for
        numa_nodes = list(topo.iter_numa_nodes())

        if len(numa_nodes) >= 2:
            # Create a simple 2x2 distance matrix
            values = [0, 10, 10, 0]  # Distance from each node to itself is 0

            # Add custom distances
            topo.add_distances(
                numa_nodes[:2],
                values,
                Kind.HWLOC_DISTANCES_KIND_VALUE_LATENCY,
                "test_latency"
            )

            # Get the added distances
            distances = topo.get_distances()

            # Should have at least one distance matrix now
            assert len(distances) > 0

            # Find our test distance matrix
            test_dist = None
            for dist in distances:
                if dist.name == "test_latency":
                    test_dist = dist
                    break

            if test_dist:
                # Test distance matrix properties
                assert test_dist.nbobjs == 2
                assert test_dist.kind == Kind.HWLOC_DISTANCES_KIND_VALUE_LATENCY
                assert test_dist.name == "test_latency"
                assert test_dist.shape == (2, 2)

                # Test matrix access
                assert test_dist[0, 0] == 0.0  # Distance to self
                assert test_dist[0, 1] == 10.0  # Distance to other
                assert test_dist[1, 0] == 10.0  # Distance from other
                assert test_dist[1, 1] == 0.0   # Other to self

                # Test flat index access
                assert test_dist[0] == 0.0   # (0,0)
                assert test_dist[1] == 10.0  # (0,1)
                assert test_dist[2] == 10.0  # (1,0)
                assert test_dist[3] == 0.0   # (1,1)


def test_distance_objects_property() -> None:
    """Test Distance objects property."""
    with Topology() as topo:
        # Add custom distances to test with
        numa_nodes = list(topo.iter_numa_nodes())

        if len(numa_nodes) >= 2:
            values = [0, 5, 5, 0]
            topo.add_distances(
                numa_nodes[:2],
                values,
                Kind.HWLOC_DISTANCES_KIND_VALUE_BANDWIDTH,
                "test_bandwidth"
            )

            distances = topo.get_distances()

            for dist in distances:
                if dist.name == "test_bandwidth":
                    # Test objects property
                    objects = dist.objects
                    assert len(objects) == 2

                    # Test object access in matrix
                    obj1, obj2 = objects[0], objects[1]
                    assert dist[obj1, obj2] == 5.0
                    assert dist[obj2, obj1] == 5.0
                    assert dist[obj1, obj1] == 0.0
                    assert dist[obj2, obj2] == 0.0

                    # Test iteration
                    assert len(dist) == 2
                    iterated_objects = list(dist)
                    assert len(iterated_objects) == 2
                    break


def test_distance_context_manager() -> None:
    """Test Distance as context manager."""
    with Topology() as topo:
        distances = topo.get_distances()

        # Test context manager functionality
        for dist in distances:
            with dist:
                # Should be able to access properties inside context
                assert dist.nbobjs >= 0
                assert isinstance(dist.kind, Kind)
            # After context, distance should still be valid (unless topology destroyed)
            break


def test_distance_string_representation() -> None:
    """Test Distance string representations."""
    with Topology() as topo:
        numa_nodes = list(topo.iter_numa_nodes())

        if len(numa_nodes) >= 2:
            values = [0, 1, 1, 0]
            topo.add_distances(
                numa_nodes[:2],
                values,
                Kind.HWLOC_DISTANCES_KIND_VALUE_HOPS,
                "test_hops"
            )

            distances = topo.get_distances()

            for dist in distances:
                if dist.name == "test_hops":
                    # Test string representations
                    str_repr = str(dist)
                    assert "test_hops" in str_repr
                    assert "2 objects" in str_repr

                    repr_str = repr(dist)
                    assert "Distance(" in repr_str
                    assert "nbobjs=2" in repr_str
                    break


def test_distance_error_handling() -> None:
    """Test Distance error handling."""
    # Test with destroyed topology
    topo = Topology()
    topo.load()

    distances = topo.get_distances()

    # Destroy topology
    topo.destroy()

    # Distance objects should detect destroyed topology
    for dist in distances:
        with pytest.raises(RuntimeError, match="Topology"):
            _ = dist.native_handle

        with pytest.raises(RuntimeError):
            _ = dist.nbobjs
        break


def test_distance_equality() -> None:
    """Test Distance equality and hashing."""
    with Topology() as topo:
        distances1 = topo.get_distances()
        distances2 = topo.get_distances()

        # Same distance matrices should be equal
        for i, (dist1, dist2) in enumerate(zip(distances1, distances2)):
            assert dist1 == dist2
            assert hash(dist1) == hash(dist2)
            break
