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
from .hwobject import OsDevice, PciDevice
from .topology import Topology
from .utils import PciId, _reuse_doc, _TopoRefMixin

__all__ = [
    "Device",
    "get_device",
]


if TYPE_CHECKING:
    from cuda.bindings.driver import CUdevice

    from .utils import _TopoRef


class Device(_TopoRefMixin):
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
            # You can pass 0 directly to `get_device` as well.
            dev = get_device(topo, cu_device)
            print(dev.get_affinity())  # CPU affinity
            print(dev.pci_id)  # PCI information
            # Get the hwloc objects
            pcidev = dev.get_pcidev()
            osdev = dev.get_osdev()

    """

    def __init__(self) -> None:
        raise RuntimeError("Use `get_device` instead.")
        self._cu_device: CUdevice
        self._topo_ref: _TopoRef

    @classmethod
    def from_native_handle(cls, topo: _TopoRef, device: CUdevice) -> Device:
        """Create Device from CUDA driver device.

        Parameters
        ----------
        topo :
            Weak reference to the topology
        device :
            CUdevice handle from CUDA driver API

        """
        dev = cls.__new__(cls)
        dev._cu_device = device
        dev._topo_ref = topo
        return dev

    @classmethod
    def from_idx(cls, topo: _TopoRef, idx: int) -> Device:
        """Create Device from the CUDA driver ordinal."""
        import cuda.bindings.driver as cuda

        status, cu_device = cuda.cuDeviceGet(idx)
        _cudadr._check_cu(status)
        return cls.from_native_handle(topo, cu_device)

    @property
    def native_handle(self) -> CUdevice:
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
    def get_pcidev(self) -> PciDevice | None:
        import cuda.bindings.driver as cuda

        dev_obj = _cudadr.get_device_pcidev(
            self._topo.native_handle, cuda.CUdevice(self.native_handle)
        )
        if dev_obj:
            return PciDevice(dev_obj, self._topo_ref)
        return None

    @_reuse_doc(_cudadr.get_device_osdev)
    def get_osdev(self) -> OsDevice | None:
        import cuda.bindings.driver as cuda

        dev_obj = _cudadr.get_device_osdev(
            self._topo.native_handle, cuda.CUdevice(self.native_handle)
        )
        if dev_obj:
            return OsDevice(dev_obj, self._topo_ref)
        return None


def get_device(topology: Topology, device: int | CUdevice) -> Device:
    """Get the CUDA driver device from its CUdevice handle or ordinal.

    Parameters
    ----------
    topology :
        Hardware topology, loaded with OS devices
    device :
        CUdevice handle from CUDA driver API or a device ordinal.

    """
    if isinstance(device, int):
        return Device.from_idx(weakref.ref(topology), device)
    else:
        return Device.from_native_handle(weakref.ref(topology), device)
