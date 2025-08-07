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
import ctypes

import pytest

from pyhwloc.core import (
    HwLocError,
    _free,
    # _obj_t_get_cpuset,
    bitmap_asprintf,
    bitmap_dup,
    bitmap_free,
    bitmap_singlify,
    get_nbobjs_by_depth,
    get_obj_by_depth,
    get_type_or_below_depth,
    hwloc_obj_type_t,
    hwloc_type_filter_e,
    set_cpubind,
    topology_destroy,
    topology_get_depth,
    topology_get_infos,
    topology_init,
    topology_load,
    topology_set_io_types_filter,
    topology_t,
)


class Topology:
    def __init__(self, filters: list[hwloc_type_filter_e] = []) -> None:
        self.hdl = topology_t()
        topology_init(self.hdl)
        if filters:
            for f in filters:
                topology_set_io_types_filter(self.hdl, f)
        topology_load(self.hdl)

    def __del__(self) -> None:
        topology_destroy(self.hdl)


def test_topology_init() -> None:
    hdl = topology_t()
    topology_init(hdl)
    topology_load(hdl)
    topology_destroy(hdl)


def test_topology_get_depth() -> None:
    topo = Topology()
    depth = topology_get_depth(topo.hdl)
    assert depth >= 0
    for d in range(depth):
        n_objs = get_nbobjs_by_depth(topo.hdl, d)
        assert n_objs >= 0


def test_topology_get_infos() -> None:
    topo = topology_t()
    topology_init(topo)

    topology_set_io_types_filter(
        topo, hwloc_type_filter_e.HWLOC_TYPE_FILTER_KEEP_IMPORTANT
    )
    topology_load(topo)

    infos = topology_get_infos(topo)

    cnt = infos.contents.count
    assert cnt > 0
    names = [infos.contents.array[i].name for i in range(cnt)]
    assert b"OSName" in names

    topology_destroy(topo)


def test_error() -> None:
    with pytest.raises(HwLocError, match="error:"):
        topo = Topology()
        topology_set_io_types_filter(
            topo.hdl, hwloc_type_filter_e.HWLOC_TYPE_FILTER_KEEP_IMPORTANT
        )


def test_example() -> None:
    topo = Topology()

    depth = get_type_or_below_depth(topo.hdl, hwloc_obj_type_t.HWLOC_OBJ_CORE)

    obj = get_obj_by_depth(topo.hdl, depth, get_nbobjs_by_depth(topo.hdl, depth) - 1)
    if obj:
        # Get a copy of its cpuset that we may modify.
        cpuset = bitmap_dup(obj.contents.cpuset)

        # Get only one logical processor (in case the core is SMT/hyper-threaded).
        bitmap_singlify(cpuset)

        # And try to bind ourself there
        set_cpubind(topo.hdl, cpuset, 0)
        bitmap_str = ctypes.c_char_p()
        # int error = errno;
        bitmap_asprintf(ctypes.byref(bitmap_str), obj.contents.cpuset)
        print(bitmap_str.value)
        # printf("Couldn't bind to cpuset %s: %s\n", str, strerror(error));
        _free(bitmap_str)

        # Free our cpuset copy
        bitmap_free(cpuset)
