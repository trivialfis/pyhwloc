# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import os

import pytest

from pyhwloc.distances import Distances
from pyhwloc.hwloc.lib import normpath
from pyhwloc.hwobject import GetTypeDepth
from pyhwloc.topology import Topology

sample_numa_path = os.path.join(os.path.dirname(normpath(__file__)), "sample_numa.xml")


def test_distance_numa() -> None:
    with Topology.from_xml_file(xml_path=sample_numa_path) as topo:
        distances = topo.get_distances()
        assert len(distances) == 1
        assert isinstance(distances[0], Distances)
        dist = distances[0]
        assert dist.name == "NUMALatency"
        assert dist.nbobjs == 2
        assert len(dist.shape) == 2
        assert dist.shape == (dist.nbobjs, dist.nbobjs)

        assert len(dist.objects) == 2
        for obj in dist.objects:
            assert obj.depth == GetTypeDepth.NUMANODE
        v = dist.get_distance(dist.objects[0], dist.objects[1])
        assert v[0] == v[1] == 21
        v = dist.get_distance(dist.objects[0], dist.objects[0])
        assert v[0] == v[1] == 10

        idx = dist.find_object_index(dist.objects[1])
        assert idx == 1

        # Test using the values directly
        d0 = dist[dist.objects[0], dist.objects[1]]
        d1 = dist[dist.objects[1], dist.objects[0]]
        d2 = dist[dist.objects[0], dist.objects[0]]
        d3 = dist[dist.objects[1], dist.objects[1]]
        assert d0 == d1 == 21
        assert d2 == d3 == 10
        d0 = dist[0, dist.objects[1]]
        d1 = dist[dist.objects[1], 0]
        d2 = dist[0, dist.objects[0]]
        d3 = dist[dist.objects[1], 1]
        assert d0 == d1 == 21
        assert d2 == d3 == 10
        with pytest.raises(IndexError):
            _ = dist[dist.objects[1], 2]

        # Test with invalid objects.
        root = topo.get_root_obj()
        assert dist.find_object_index(root) == -1
        with pytest.raises(ValueError, match="obj1 or obj2"):
            dist.get_distance(root, root)


def test_distance_error_handling() -> None:
    topo = Topology()

    distances = topo.get_distances()
    topo.destroy()

    for dist in distances:
        with pytest.raises(RuntimeError, match="Topology"):
            _ = dist.native_handle

        with pytest.raises(RuntimeError, match="Topology"):
            _ = dist.nbobjs

    topo = Topology.from_xml_file(xml_path=sample_numa_path).load()
    distances = topo.get_distances()
    topo.destroy()  # cleanup all distances

    for dist in distances:
        with pytest.raises(RuntimeError, match="Topology"):
            _ = dist.native_handle

        with pytest.raises(RuntimeError, match="Topology"):
            _ = dist.nbobjs

    topo = Topology.from_xml_file(xml_path=sample_numa_path).load()
    distances = topo.get_distances()
    # Internal cleanup couldn't happen as the old `distances` is still valid.
    distances = topo.get_distances()
    assert len(topo._cleanup) == 2
    assert topo._cleanup[0]() is None
    # Internal cleanup happens, number of values is kept at 2.
    distances = topo.get_distances()
    assert len(topo._cleanup) == 2
    assert topo._cleanup[0]() is None
