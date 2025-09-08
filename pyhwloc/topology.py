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
from __future__ import annotations

from types import TracebackType
from typing import Type

from .hwloc import core as _core
from .hwloc import lib as _lib

__all__ = ["Topology"]

# fixme:
# - don't set the handle if the initialization failes
# - use filter
# - remove manual destroy


class Topology:
    """High-level pythonic interface for hwloc topology.

    This class provides a context manager interface for working with hardware
    topology information. It automatically handles topology initialization,
    loading, and cleanup.

    Examples:
        # Context manager usage (recommended)
        with Topology() as topo:  # Current system
            print(f"Topology depth: {topo.depth}")

        # Synthetic topology
        with Topology.from_synthetic("node:2 core:2 pu:2") as topo:
            print(f"Synthetic depth: {topo.depth}")

        # Load from XML file
        with Topology.from_xml_file("/path/to/topology.xml") as topo:
            print(f"XML depth: {topo.depth}")

        # Direct usage (manual cleanup required)
        topo = Topology()
        try:
            print(f"Topology depth: {topo.depth}")
        finally:
            topo.destroy()
    """

    def __init__(self) -> None:
        """Initialize a new topology for the current system.

        For other topology sources, use the class methods:
        - Topology.from_pid(pid)
        - Topology.from_synthetic(description)
        - Topology.from_xml_file(path)
        - Topology.from_xml_buffer(xml_string)
        """
        self._hdl = _core.topology_t()
        self._loaded = False
        self._destroyed = False

        try:
            # Initialize and load the current system topology
            _core.topology_init(self._hdl)
            _core.topology_load(self._hdl)
            self._loaded = True

        except Exception:
            # If initialization fails, clean up
            if not self._destroyed:
                try:
                    _core.topology_destroy(self._hdl)
                except Exception:
                    pass
                self._destroyed = True
            raise

    @classmethod
    def from_native_hdl(cls, hdl: _core.topology_t) -> Topology:
        topo = cls.__new__(cls)
        topo._hdl = hdl
        topo._loaded = True
        topo._destroyed = False
        topo.check()
        return topo

    @classmethod
    def from_pid(cls, pid: int) -> Topology:
        """Create topology from a specific process ID.

        Args:
            pid: Process ID to get topology from

        Returns:
            New Topology instance for the specified process
        """
        instance = cls.__new__(cls)
        instance._hdl = _core.topology_t()
        instance._loaded = False
        instance._destroyed = False

        try:
            _core.topology_init(instance._hdl)
            _core.topology_set_pid(instance._hdl, pid)
            _core.topology_load(instance._hdl)
            instance._loaded = True

        except Exception:
            if not instance._destroyed:
                try:
                    _core.topology_destroy(instance._hdl)
                except Exception:
                    pass
                instance._destroyed = True
            raise

        return instance

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

        Args:
            xml_path: Path to XML file containing topology

        Returns:
            New Topology instance loaded from XML file
        """
        instance = cls.__new__(cls)
        instance._hdl = _core.topology_t()
        instance._loaded = False
        instance._destroyed = False

        try:
            _core.topology_init(instance._hdl)
            _core.topology_set_xml(instance._hdl, xml_path)
            _core.topology_load(instance._hdl)
            instance._loaded = True

        except Exception:
            if not instance._destroyed:
                try:
                    _core.topology_destroy(instance._hdl)
                except Exception:
                    pass
                instance._destroyed = True
            raise

        return instance

    @classmethod
    def from_xml_buffer(cls, xml_buffer: str) -> Topology:
        """Create topology from XML string.

        Args:
            xml_buffer: XML string containing topology

        Returns:
            New Topology instance loaded from XML string
        """
        instance = cls.__new__(cls)
        instance._hdl = _core.topology_t()
        instance._loaded = False
        instance._destroyed = False

        try:
            _core.topology_init(instance._hdl)
            _core.topology_set_xmlbuffer(instance._hdl, xml_buffer)
            _core.topology_load(instance._hdl)
            instance._loaded = True

        except Exception:
            if not instance._destroyed:
                try:
                    _core.topology_destroy(instance._hdl)
                except Exception:
                    pass
                instance._destroyed = True
            raise

        return instance

    def check(self) -> None:
        _core.topology_check(self._hdl)

    @property
    def native_handle(self) -> _core.topology_t:
        """Get the native hwloc topology handle."""
        if self._destroyed:
            raise RuntimeError("Topology has been destroyed")
        return self._hdl

    @property
    def is_loaded(self) -> bool:
        """Check if topology is loaded and ready for use."""
        return self._loaded and not self._destroyed

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
        if not self._destroyed:
            _core.topology_destroy(self._hdl)
            self._destroyed = True
            self._loaded = False

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
        if hasattr(self, "_destroyed") and not self._destroyed:
            try:
                self.destroy()
            except Exception:
                pass
