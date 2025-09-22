# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Interoperability with the CUDA Driver API
==========================================
"""

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from .bitmap import Bitmap
from .hwloc import cudadr as _cudadr
from .hwobject import Object
from .topology import Topology
from .utils import PciId, _reuse_doc, _TopoRef

__all__ = [
    "Device",
    "get_device",
]

if TYPE_CHECKING:
    from cuda.bindings.driver import CUDevice


class Device(_TopoRef):
    """Class to represent a CUDA driver device. This class can be created using the
    :py:func:`get_device`.

    .. code-block::

        from pyhwloc.topology import Topology, TypeFilter
        from pyhwloc.cuda_driver import get_device
        import cuda.bindings.driver as cuda

        with Topology.from_this_system().set_io_types_filter(
            TypeFilter.KEEP_ALL
        ) as topo:
            # Get the first CUDA device
            status, cu_device = cuda.cuDeviceGet(0)
            dev = get_device(topo, cu_device)
            print(dev.get_affinity())  # CPU affinity
            print(dev.pci_ids())  # PCI information
            # Get the hwloc objects
            pcidev = dev.get_pcidev()
            osdev = dev.get_osdev()

    """

    def __init__(self) -> None:
        raise RuntimeError("Use `get_device` instead.")
        self._cu_device: CUDevice
        self._topo_ref: weakref.ReferenceType["Topology"]

    @classmethod
    def from_cu_device(
        cls, topo: weakref.ReferenceType["Topology"], device: CUDevice
    ) -> Device:
        """Create Device from CUDA driver device.

        Parameters
        ----------
        topo :
            Weak reference to topology
        device :
            CUdevice handle from CUDA driver API

        """
        dev = cls.__new__(cls)
        dev._cu_device = device
        dev._topo_ref = topo
        return dev

    @classmethod
    def from_idx(cls, topo: weakref.ReferenceType["Topology"], idx: int) -> Device:
        import cuda.bindings.driver as cuda

        status, cu_device = cuda.cuDeviceGet(idx)
        _cudadr._check_cu(status)
        return cls.from_cu_device(topo, cu_device)

    @property
    def native_handle(self) -> "CUDevice":
        return self._cu_device

    # Use property to be consistent with hwobject.pci_id
    @property
    @_reuse_doc(_cudadr.get_device_pci_ids)
    def pci_id(self) -> PciId:
        import cuda.bindings.driver as cuda

        domain, bus, dev = _cudadr.get_device_pci_ids(
            self._topo.native_handle, cuda.CUdevice(self.native_handle)
        )
        return PciId(domain, bus, dev)

    @_reuse_doc(_cudadr.get_device_cpuset)
    def get_affinity(self) -> Bitmap:
        import cuda.bindings.driver as cuda

        bitmap = Bitmap()
        _cudadr.get_device_cpuset(
            self._topo.native_handle,
            cuda.CUdevice(self.native_handle),
            bitmap.native_handle,
        )
        return bitmap

    @_reuse_doc(_cudadr.get_device_pcidev)
    def get_pcidev(self) -> Object | None:
        import cuda.bindings.driver as cuda

        dev_obj = _cudadr.get_device_pcidev(
            self._topo.native_handle, cuda.CUdevice(self.native_handle)
        )
        if dev_obj:
            return Object(dev_obj, self._topo_ref)
        return None

    @_reuse_doc(_cudadr.get_device_osdev)
    def get_osdev(self) -> Object | None:
        import cuda.bindings.driver as cuda

        dev_obj = _cudadr.get_device_osdev(
            self._topo.native_handle, cuda.CUdevice(self.native_handle)
        )
        if dev_obj:
            return Object(dev_obj, self._topo_ref)
        return None


def get_device(topology: Topology, device: int | CUDevice) -> Device:
    """Get the CUDA driver device from its CUdevice handle or ordinal.

    Parameters
    ----------
    topology :
        Hardware topology, loaded with OS devices
    device :
        CUdevice handle from CUDA driver API or device ordinal.

    """
    if isinstance(device, int):
        return Device.from_idx(weakref.ref(topology), device)
    else:
        return Device.from_cu_device(weakref.ref(topology), device)
