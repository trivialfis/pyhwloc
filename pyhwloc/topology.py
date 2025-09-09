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

"""
The Topology Interface
======================
"""
from __future__ import annotations

import ctypes
import logging
import os
from types import TracebackType
from typing import Type, TypeAlias

from .hwloc import core as _core
from .hwloc import lib as _lib

__all__ = ["Topology"]

# fixme:
# - don't set the handle if the initialization failes
# - use filter
# - remove manual destroy

ExportXmlFlags: TypeAlias = _core.hwloc_topology_export_xml_flags_e
ExportSyntheticFlags: TypeAlias = _core.hwloc_topology_export_synthetic_flags_e


class Topology:
    """High-level pythonic interface for hwloc topology.

    This class provides a context manager interface for working with hardware
    topology information. It automatically handles topology initialization,
    loading, and cleanup.

    .. code-block::

        # Context manager usage (recommended)
        with Topology() as topo:  # Current system
            print(f"Topology depth: {topo.depth}")

        # Synthetic topology
        with Topology.from_synthetic("node:2 core:2 pu:2") as topo:
            print(f"Synthetic depth: {topo.depth}")

        # Load from XML file
        with Topology.from_xml_file("/path/to/topology.xml") as topo:
            print(f"XML depth: {topo.depth}")

        # Direct usage (manual cleanup is recommended)
        try:
            topo = Topology()
            print(f"Topology depth: {topo.depth}")
        finally:
            topo.destroy()

    The default `Topology` constructor initializes a topology object based on the
    current system. For alternative topology sources, use the class methods:

    - :meth:`from_pid`
    - :meth:`from_synthetic`
    - :meth:`from_xml_file`
    - :meth:`from_xml_buffer`

    """

    def __init__(self) -> None:
        """Initialize a new topology for the current system."""
        hdl = _core.topology_t()

        try:
            # Initialize and load the current system topology
            _core.topology_init(hdl)
            _core.topology_load(hdl)
        except (_lib.HwLocError, NotImplementedError) as e:
            if hdl:
                _core.topology_destroy(hdl)
            raise e

        self._hdl = hdl
        self._loaded = True

    @classmethod
    def from_native_hdl(cls, hdl: _core.topology_t) -> Topology:
        topo = cls.__new__(cls)
        topo._hdl = hdl
        topo._loaded = True
        topo.check()
        return topo

    @classmethod
    def from_pid(cls, pid: int) -> Topology:
        """Create topology from a specific process ID.

        Parameters
        ----------

        pid :
            Process ID to get topology from

        Returns
        -------
        New Topology instance for the specified process.
        """
        hdl = _core.topology_t(0)
        try:
            _core.topology_init(hdl)
            _core.topology_set_pid(hdl, pid)
            _core.topology_load(hdl)
        except (_lib.HwLocError, NotImplementedError) as e:
            if hdl:
                _core.topology_destroy(hdl)
            raise e

        return cls.from_native_hdl(hdl)

    @classmethod
    def from_synthetic(cls, description: str) -> Topology:
        """Create topology from synthetic description.

        Parameters
        ----------

        description :
            Synthetic topology description (e.g., "node:2 core:2 pu:2")

        Returns
        -------
        New Topology instance from the synthetic description.
        """
        hdl = _core.topology_t(0)
        try:
            _core.topology_init(hdl)
            _core.topology_set_synthetic(hdl, description)
            _core.topology_load(hdl)
        except (_lib.HwLocError, NotImplementedError) as e:
            if hdl:
                _core.topology_destroy(hdl)
            raise e

        return cls.from_native_hdl(hdl)

    @classmethod
    def from_xml_file(cls, xml_path: str) -> Topology:
        """Create topology from XML file.

        Parameters
        ----------

        xml_path :
            Path to XML file containing topology

        Returns
        -------
        New Topology instance loaded from XML file.
        """
        hdl = _core.topology_t(0)
        try:
            _core.topology_init(hdl)
            _core.topology_set_xml(hdl, xml_path)
            _core.topology_load(hdl)
        except (_lib.HwLocError, NotImplementedError) as e:
            if hdl:
                _core.topology_destroy(hdl)
            raise e

        return cls.from_native_hdl(hdl)

    @classmethod
    def from_xml_buffer(cls, xml_buffer: str) -> Topology:
        """Create topology from XML string.

        Parameters
        ----------

        xml_buffer :
            XML string containing topology

        Returns
        -------
        New Topology instance loaded from XML string.
        """
        hdl = _core.topology_t(0)
        try:
            _core.topology_init(hdl)
            _core.topology_set_xmlbuffer(hdl, xml_buffer)
            _core.topology_load(hdl)
        except (_lib.HwLocError, NotImplementedError) as e:
            if hdl:
                _core.topology_destroy(hdl)
            raise e

        return cls.from_native_hdl(hdl)

    def check(self) -> None:
        _core.topology_check(self._hdl)

    @property
    def native_handle(self) -> _core.topology_t:
        """Get the native hwloc topology handle."""
        if not hasattr(self, "_hdl"):
            raise RuntimeError("Topology has been destroyed")
        return self._hdl

    def export_xml_buffer(self, flags: ExportXmlFlags | int) -> str:
        "See :py:func:`~pyhwloc.hwloc.core.topology_export_xmlbuffer`."
        return _core.topology_export_xmlbuffer(self._hdl, flags)

    def export_xml_file(
        self, path: os.PathLike | str, flags: ExportXmlFlags | int
    ) -> None:
        "See :py:func:`~pyhwloc.hwloc.core.topology_export_xml`."
        path = os.fspath(os.path.expanduser(path))
        _core.topology_export_xml(self._hdl, path, flags)

    def export_synthetic(self, flags: ExportSyntheticFlags | int) -> str:
        "See :py:func:`~pyhwloc.hwloc.core.topology_export_synthetic`."
        n_bytes = 1024
        buf = ctypes.create_string_buffer(n_bytes)
        n_written = _core.topology_export_synthetic(self._hdl, buf, n_bytes, flags)
        while n_written == n_bytes - 1:
            n_bytes = n_bytes * 2
            buf = ctypes.create_string_buffer(n_bytes)
            n_written = _core.topology_export_synthetic(self._hdl, buf, n_bytes, flags)
            if n_bytes >= 8192:
                raise RuntimeError("Failed to export synthetic.")
        assert buf.value is not None
        return buf.value.decode("utf-8")

    @property
    def is_loaded(self) -> bool:
        """Check if topology is loaded and ready for use."""
        return hasattr(self, "_hdl") and self._loaded

    @property
    def is_this_system(self) -> bool:
        """Check if topology represents the current system."""
        if not self.is_loaded:
            return False
        return _core.topology_is_thissystem(self._hdl)

    @property
    def depth(self) -> int:
        """Get the depth of the topology tree."""
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        return _core.topology_get_depth(self._hdl)

    def destroy(self) -> None:
        """Explicitly destroy the topology and free resources."""
        if hasattr(self, "_hdl"):
            _core.topology_destroy(self._hdl)
            self._loaded = False
            del self._hdl

    def __enter__(self) -> Topology:
        """Context manager entry."""
        if not self.is_loaded:
            raise RuntimeError("Topology is not loaded")
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit - cleanup topology."""
        self.destroy()

    def __del__(self) -> None:
        """Automatic cleanup if not used as context manager."""
        if hasattr(self, "_hdl"):
            try:
                self.destroy()
            except Exception as e:
                logging.warn(str(e))

    def __copy__(self) -> Topology:
        new = _core.topology_dup(self._hdl)
        return Topology.from_native_hdl(new)

    def __deepcopy__(self, memo: dict) -> Topology:
        return self.__copy__()
