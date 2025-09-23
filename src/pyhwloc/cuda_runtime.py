# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Interoperability with the CUDA Runtime API
==========================================
"""

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from .bitmap import Bitmap
from .hwloc import cudart as _cudart
from .hwobject import OsDevice, PciDevice
from .topology import Topology
from .utils import PciId, _reuse_doc, _TopoRefMixin

if TYPE_CHECKING:
    from .utils import _TopoRef

__all__ = [
    "Device",
    "get_device",
]


class Device(_TopoRefMixin):
    """Class to represent a CUDA runtime device. This class can be created using the
    :py:func:`get_device`.

    .. code-block::

        from pyhwloc.topology import Topology, TypeFilter
        from pyhwloc.cuda_runtime import get_device

        with Topology.from_this_system().set_io_types_filter(
            TypeFilter.KEEP_ALL
        ) as topo:
            ordinal = 0  # The first CUDA runtime device.
            dev = get_device(topo, ordinal)
            print(dev.get_affinity())  # CPU affinity
            print(dev.pci_id)  # PCI information
            # Get the hwloc object
            osdev = dev.get_osdev()

    """

    def __init__(self) -> None:
        raise RuntimeError("Use `get_device` instead.")
        self._idx: int = -1
        self._topo_ref: _TopoRef

    @classmethod
    def from_idx(cls, topo: _TopoRef, idx: int) -> Device:
        """Create Device from CUDA ordinal."""
        dev = cls.__new__(cls)
        dev._idx = idx
        dev._topo_ref = topo
        return dev

    @property
    def index(self) -> int:
        """Device ordinal."""
        return self._idx

    # Use property to be consistent with hwobject.pci_id
    @property
    @_reuse_doc(_cudart.get_device_pci_ids)
    def pci_id(self) -> PciId:
        domain, bus, dev = _cudart.get_device_pci_ids(
            self._topo.native_handle, self._idx
        )
        return PciId(domain, bus, dev)

    @_reuse_doc(_cudart.get_device_cpuset)
    def get_affinity(self) -> Bitmap:
        bitmap = Bitmap()
        _cudart.get_device_cpuset(
            self._topo.native_handle, self._idx, bitmap.native_handle
        )
        return bitmap

    @_reuse_doc(_cudart.get_device_pcidev)
    def get_pcidev(self) -> PciDevice | None:
        dev_obj = _cudart.get_device_pcidev(self._topo.native_handle, self._idx)
        if dev_obj:
            return PciDevice(dev_obj, self._topo_ref)
        return None

    @_reuse_doc(_cudart.get_device_osdev_by_index)
    def get_osdev(self) -> OsDevice | None:
        dev_obj = _cudart.get_device_osdev_by_index(self._topo.native_handle, self._idx)
        if dev_obj:
            return OsDevice(dev_obj, self._topo_ref)
        return None


def get_device(topology: Topology, device: int) -> Device:
    """Get the CUDA device from its ordinal.

    Parameters
    ----------
    topology :
        Hwloc topology, loaded with OS devices.
    device :
        Device ordinal.

    """
    return Device.from_idx(weakref.ref(topology), device)
