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
import copy

import pytest

from pyhwloc.hwloc.lib import HwLocError
from pyhwloc.topology import ExportXmlFlags, Topology


def test_context_manager_current_system():
    """Test context manager usage with current system topology."""
    with Topology() as topo:
        # Verify topology is loaded and accessible
        assert topo.is_loaded
        assert isinstance(topo.depth, int)
        assert topo.depth > 0
        assert topo.is_this_system

    # After context manager exits, topology should be destroyed
    assert not topo.is_loaded
    with pytest.raises(RuntimeError):
        _ = topo.depth


def test_direct_usage_current_system():
    """Test direct usage with manual cleanup for current system topology."""
    topo = Topology()
    try:
        # Verify topology is loaded and accessible
        assert topo.is_loaded
        assert isinstance(topo.depth, int)
        assert topo.depth > 0
        assert topo.is_this_system

    finally:
        topo.destroy()

    # After destroy(), topology should not be accessible
    assert not topo.is_loaded
    with pytest.raises(RuntimeError):
        _ = topo.depth


def test_context_manager_synthetic() -> None:
    desc = "node:2 core:2 pu:2"

    with Topology.from_synthetic(desc) as topo:
        # Verify synthetic topology is loaded
        assert topo.is_loaded
        assert isinstance(topo.depth, int)
        assert topo.depth > 0
        # Synthetic topology should not be "this system"
        assert not topo.is_this_system

    # After context manager exits, topology should be destroyed
    assert not topo.is_loaded

    desc = "node:2 core:2 foo:2"
    with pytest.raises(HwLocError, match="Invalid argument"):
        with Topology.from_synthetic(desc) as topo:
            pass


def test_direct_usage_synthetic():
    """Test direct usage with manual cleanup for synthetic topology."""
    synthetic_desc = "node:2 core:2 pu:2"

    topo = Topology.from_synthetic(synthetic_desc)
    try:
        # Verify synthetic topology is loaded
        assert topo.is_loaded
        assert isinstance(topo.depth, int)
        assert topo.depth > 0
        # Synthetic topology should not be "this system"
        assert not topo.is_this_system

    finally:
        topo.destroy()

    # After destroy(), topology should not be accessible
    assert not topo.is_loaded


def test_double_destroy_safety():
    """Test that calling destroy() multiple times is safe."""
    topo = Topology()

    # First destroy should work
    topo.destroy()
    assert not topo.is_loaded

    # Second destroy should be safe (no exception)
    topo.destroy()
    assert not topo.is_loaded


def test_access_after_destroy_fails():
    """Test that accessing properties after destroy raises RuntimeError."""
    topo = Topology()
    topo.destroy()

    # All property access should fail after destroy
    with pytest.raises(RuntimeError):
        _ = topo.native_handle
    with pytest.raises(RuntimeError):
        _ = topo.depth

    # But these should still work
    assert not topo.is_loaded


def test_context_manager_exception_cleanup():
    """Test that topology is properly cleaned up even if exception occurs in context."""
    topo_ref = None

    try:
        with Topology() as topo:
            topo_ref = topo
            assert topo.is_loaded
            # Simulate an exception in the context
            raise ValueError("Test exception")
    except ValueError:
        pass  # Expected exception

    # Topology should still be cleaned up after exception
    assert not topo_ref.is_loaded


def test_copy_exprt() -> None:
    desc = "node:2 core:2 pu:2"
    try:
        topo = Topology.from_synthetic(desc)
        cp = copy.copy(topo)
        dcp = copy.deepcopy(topo)
        assert (
            cp.export_synthetic(0)
            == topo.export_synthetic(0)
            == dcp.export_synthetic(0)
        )
        assert (
            cp.export_xmlbuffer(0)
            == topo.export_xmlbuffer(0)
            == dcp.export_xmlbuffer(0)
        )
        assert (
            len(cp.export_xmlbuffer(ExportXmlFlags.HWLOC_TOPOLOGY_EXPORT_XML_FLAG_V2))
            > 2
        )
    finally:
        topo.destroy()
        cp.destroy()
        dcp.destroy()
