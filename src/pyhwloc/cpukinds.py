# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
CPU Kinds
=========

CPU Kinds is a structure inside the topology. The Python interface implements it as an
independent class.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .hwloc import core as _core
from .utils import _get_info, _reuse_doc, _TopoRefMixin

if TYPE_CHECKING:
    from .bitmap import Bitmap
    from .utils import _TopoRef


class CpuKinds(_TopoRefMixin):
    """Represents the CPU kinds in hwloc. Use the
    :py:meth:`~pyhwloc.topology.Topology.get_cpukinds` to obtain an instance of this
    class.

    """

    def __init__(self, topology: _TopoRef) -> None:
        self._topo_ref = topology

    @_reuse_doc(_core.cpukinds_register)
    def register(
        self, cpuset: Bitmap, forced_efficiency: int, infos: dict[str, str] = {}
    ) -> None:
        cinfos = _core.Infos()
        cinfos.allocated = 0
        cinfos.count = len(infos)
        names = []
        values = []
        cinfos.array = None

        # Create array of hwloc_info_s items
        items = []
        for k, v in infos.items():
            item = _core.Info()
            names.append(k.encode("utf-8"))
            values.append(v.encode("utf-8"))
            items.append(item)

        # Create array of pointers to items
        array = (_core.Info * len(infos))()
        for i, item in enumerate(items):
            item.name = names[i]
            item.value = values[i]
            array[i] = items[i]

        # Cast to the right type and assign
        cinfos.array = array

        # Pass None if no infos to let the low-level function handle it
        infos_arg = cinfos if len(infos) > 0 else None
        _core.cpukinds_register(
            self._topo.native_handle, cpuset.native_handle, forced_efficiency, infos_arg
        )

    @_reuse_doc(_core.cpukinds_get_nr)
    def n_kinds(self) -> int:
        return _core.cpukinds_get_nr(self._topo.native_handle)

    @_reuse_doc(_core.cpukinds_get_by_cpuset)
    def get_kind_by_cpuset(self, cpuset: Bitmap) -> int:
        return _core.cpukinds_get_by_cpuset(
            self._topo.native_handle, cpuset.native_handle
        )

    @_reuse_doc(_core.cpukinds_get_info)
    def get_info(self, kind_index: int) -> tuple[Bitmap, int, dict[str, str]]:
        from .bitmap import Bitmap

        c_cpuset, efficiency, infos_ptr = _core.cpukinds_get_info(
            self._topo.native_handle, kind_index
        )

        # The cpuset is allocated by the get_info in Python.
        cpuset = Bitmap.from_native_handle(c_cpuset)

        # Convert infos to dictionary
        infos_d = {}
        if infos_ptr:
            infos = infos_ptr.contents
            infos_d = _get_info(infos)

        return cpuset, efficiency, infos_d

    def __deepcopy__(self, memo: dict) -> CpuKinds:
        raise RuntimeError("The CpuKinds class cannot be deep-copied.")
