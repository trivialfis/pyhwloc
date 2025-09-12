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
import os

import pytest

from pyhwloc.distance import Distances
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
            assert obj.depth == GetTypeDepth.HWLOC_TYPE_DEPTH_NUMANODE
        v = dist.get_distance(dist.objects[0], dist.objects[1])
        assert v[0] == v[1] == 21
        v = dist.get_distance(dist.objects[0], dist.objects[0])
        assert v[0] == v[1] == 10

        idx = dist.find_object_index(dist.objects[1])
        assert idx == 1

        # Test with invalid objects.
        root = topo.get_root_obj()
        assert dist.find_object_index(root) == -1
        with pytest.raises(ValueError, match="obj1 or obj2"):
            dist.get_distance(root, root)


def test_distance_error_handling() -> None:
    """Test Distance error handling."""
    # Test with destroyed topology
    topo = Topology()
    topo.load()

    distances = topo.get_distances()
    topo.destroy()

    for dist in distances:
        with pytest.raises(RuntimeError, match="Topology"):
            _ = dist.native_handle

        with pytest.raises(RuntimeError):
            _ = dist.nbobjs
