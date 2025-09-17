# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Interoperability with the NVIDIA Management Library (NVML)
==========================================================
"""
from __future__ import annotations

import ctypes
import weakref

from .bitmap import Bitmap
from .hwloc import nvml as _nvml
from .hwobject import Object
from .topology import Topology
from .utils import _reuse_doc

__all__ = [
    "Device",
    "get_device",
]


class Device:
    """Class to represent an NVML device. This class can be created using the
    :py:func:`get_device`.

    .. code-block::

        from pyhwloc.topology import Topology, TypeFilter
        from pyhwloc.nvml import get_device
        import pynvml

        with Topology.from_this_system().set_io_types_filter(
            TypeFilter.HWLOC_TYPE_FILTER_KEEP_ALL
        ) as topo:
            # Initialize NVML
            pynvml.nvmlInit()
            try:
                # Get the first NVML device
                nvml_hdl = pynvml.nvmlDeviceGetHandleByIndex(0)
                dev = get_device(topo, nvml_hdl)
                print(dev.cpuset)  # CPU affinity
                # Get the hwloc object
                osdev = dev.get_osdev()
            finally:
                pynvml.nvmlShutdown()

    """

    def __init__(self) -> None:
        raise RuntimeError("Use `get_device` instead.")
        self._nvml_hdl: ctypes._Pointer = None
        self._topo_ref: weakref.ReferenceType["Topology"]

    @property
    def _topo(self) -> Topology:
        if not self._topo_ref or not self._topo_ref().is_loaded:  # type: ignore
            raise RuntimeError("Topology is invalid")
        v = self._topo_ref()
        assert v is not None
        return v

    @classmethod
    def from_native_handle(
        cls, topo: weakref.ReferenceType["Topology"], hdl: ctypes._Pointer
    ) -> Device:
        """Create Device from NVML handle and index.

        Parameters
        ----------
        topo :
            Weak reference to the topology
        hdl :
            NVML device handle from pynvml

        """
        dev = cls.__new__(cls)
        dev._nvml_hdl = hdl
        dev._topo_ref = topo
        return dev

    @classmethod
    def from_idx(cls, topo: weakref.ReferenceType["Topology"], idx: int) -> Device:
        import pynvml as nm

        hdl = nm.nvmlDeviceGetHandleByIndex(idx)
        return cls.from_native_handle(topo, hdl)

    @property
    def index(self) -> int:
        """Device ordinal."""
        import pynvml as nm

        idx = nm.nvmlDeviceGetIndex(self.native_handle)
        return idx

    @property
    def native_handle(self) -> ctypes._Pointer:
        return self._nvml_hdl

    # Defined as a property to align with Object. Normally we should use a method when
    # it's implemented as a function in hwloc.
    @property
    @_reuse_doc(_nvml.get_device_cpuset)
    def cpuset(self) -> Bitmap:
        bitmap = Bitmap()
        _nvml.get_device_cpuset(
            self._topo.native_handle, self.native_handle, bitmap.native_handle
        )
        return bitmap

    @_reuse_doc(_nvml.get_device_osdev)
    def get_osdev(self) -> Object | None:
        dev_obj = _nvml.get_device_osdev(self._topo.native_handle, self.native_handle)
        if dev_obj:
            return Object(dev_obj, self._topo_ref)
        return None


def get_device(topology: Topology, device: int | ctypes._Pointer) -> Device:
    """Get the NVML device from its handle or ordinal.

    Parameters
    ----------
    topology :
        Hwloc topology, loaded with OS devices.
    device :
        Either the device ordinal or the nvmlDevice

    """
    if isinstance(device, int):
        return Device.from_idx(weakref.ref(topology), device)
    elif isinstance(device, ctypes._Pointer):
        return Device.from_native_handle(weakref.ref(topology), device)
    else:
        raise TypeError(
            "Invalid nvml device type. Expecting a nvmlDevice or an integer index."
        )
