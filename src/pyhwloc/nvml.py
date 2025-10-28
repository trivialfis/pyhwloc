# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Interoperability with the NVIDIA Management Library (NVML)
==========================================================

"""

from __future__ import annotations

import ctypes
import math
import os
import weakref
from typing import TYPE_CHECKING, Sequence

from .bitmap import Bitmap
from .hwloc import nvml as _nvml
from .hwobject import OsDevice
from .topology import Topology
from .utils import _reuse_doc, _TopoRefMixin

if TYPE_CHECKING:
    from .utils import _TopoRef

__all__ = [
    "Device",
    "get_device",
    "get_cpu_affinity",
]


class Device(_TopoRefMixin):
    """Class to represent an NVML device. This class can be created using the
    :py:func:`get_device`.

    .. code-block::

        from pyhwloc.topology import Topology, TypeFilter
        from pyhwloc.nvml import get_device
        import pynvml

        with Topology.from_this_system().set_io_types_filter(
            TypeFilter.KEEP_ALL
        ) as topo:
            # Initialize NVML
            pynvml.nvmlInit()
            try:
                # Get the first NVML device
                nvml_hdl = pynvml.nvmlDeviceGetHandleByIndex(0)
                # You can pass 0 directly to `get_device` as well.
                dev = get_device(topo, nvml_hdl)
                print(dev.get_affinity())  # CPU affinity
                # Get the hwloc object
                osdev = dev.get_osdev()
            finally:
                pynvml.nvmlShutdown()

    """

    def __init__(self) -> None:
        raise RuntimeError("Use `get_device` instead.")
        self._nvml_hdl: ctypes._Pointer = None
        self._topo_ref: _TopoRef

    @classmethod
    def from_native_handle(cls, topo: _TopoRef, hdl: ctypes._Pointer) -> Device:
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
    def from_idx(cls, topo: _TopoRef, idx: int) -> Device:
        """Create Device from NVML device ordinal."""
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
        """Obtain the NVML's native device handle."""
        return self._nvml_hdl

    @_reuse_doc(_nvml.get_device_cpuset)
    def get_affinity(self) -> Bitmap:
        bitmap = Bitmap()
        _nvml.get_device_cpuset(
            self._topo.native_handle, self.native_handle, bitmap.native_handle
        )
        return bitmap

    @_reuse_doc(_nvml.get_device_osdev)
    def get_osdev(self) -> OsDevice | None:
        dev_obj = _nvml.get_device_osdev(self._topo.native_handle, self.native_handle)
        if dev_obj:
            return OsDevice(dev_obj, self._topo_ref)
        return None


def get_device(topology: Topology, device: int | ctypes._Pointer) -> Device:
    """Get the NVML device from its handle or ordinal.

    Parameters
    ----------
    topology :
        Hwloc topology, loaded with OS devices.
    device :
        Either a device ordinal or a nvmlDevice.

    """
    if isinstance(device, int):
        return Device.from_idx(weakref.ref(topology), device)
    elif isinstance(device, ctypes._Pointer):
        return Device.from_native_handle(weakref.ref(topology), device)
    else:
        raise TypeError(
            "Invalid nvml device type. Expecting a nvmlDevice or an integer index."
        )


_MASK_SIZE = 64


class _BitField64:
    def __init__(self, mask: Sequence[ctypes.c_ulonglong]) -> None:
        assert ctypes.sizeof(ctypes.c_ulonglong) * 8 == _MASK_SIZE
        self.mask: list[ctypes.c_ulonglong] = []
        for m in mask:
            self.mask.append(m)

    @staticmethod
    def to_bit(i: int) -> tuple[int, int]:
        int_pos, bit_pos = 0, 0
        if i == 0:
            return int_pos, bit_pos

        int_pos = i // _MASK_SIZE
        bit_pos = i % _MASK_SIZE
        return int_pos, bit_pos

    def check(self, i: int) -> bool:
        ip, bp = self.to_bit(i)
        value = self.mask[ip]
        test_bit = 1 << bp
        res = int(value) & test_bit
        return bool(res)


def _get_uuid(ordinal: int) -> str:
    """Construct a string representation of UUID."""
    from cuda.bindings import runtime as cudart

    from .hwloc.cudart import _check_cudart

    status, prop = cudart.cudaGetDeviceProperties(ordinal)
    _check_cudart(status)

    dash_pos = {0, 4, 6, 8, 10}
    uuid = "GPU"

    for i in range(16):
        if i in dash_pos:
            uuid += "-"
        h = hex(0xFF & prop.uuid.bytes[i])
        assert h[:2] == "0x"
        h = h[2:]

        while len(h) < 2:
            h = "0" + h
        uuid += h
    return uuid


def get_cpu_affinity(device: int | str) -> Bitmap:
    """Get optimal affinity using nvml directly. This should produce the same result as
    :py:meth:`pyhwloc.nvml.Device.get_affinity`.

    Parameters
    ----------
    device :
        Either the UUID of the device or a CUDA runtime ordinal.

    """
    import pynvml as nm

    cnt = os.cpu_count()
    assert cnt is not None

    if isinstance(device, int):
        uuid = _get_uuid(device)
    else:
        uuid = device
    hdl = nm.nvmlDeviceGetHandleByUUID(uuid)

    affinity = nm.nvmlDeviceGetCpuAffinity(
        hdl,
        math.ceil(cnt / _MASK_SIZE),
    )
    cpumask = _BitField64(affinity)

    cpuset = Bitmap()
    for i in range(cnt):
        if cpumask.check(i):
            cpuset.set(i)

    return cpuset
