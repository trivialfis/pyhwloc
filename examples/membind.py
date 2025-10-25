# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Example of using membind
========================
"""

from pyhwloc import Topology
from pyhwloc.topology import MemBindFlags, MemBindPolicy


def bind_np_array() -> None:
    """Show how to bind a numpy array."""
    try:
        import numpy as np
    except ImportError:
        print("Numpy is not available.")
        return

    array = np.arange(0, 8196)

    with Topology.from_this_system() as topo:
        if not topo.get_support().membind.set_area_membind:
            return

        nodeset, policy = topo.get_area_membind(array.data, MemBindFlags.BYNODESET)
        print(policy.name, nodeset)
        # >>> FIRSTTOUCH 0

        # Use to the first node.
        nodeset.only(0)
        topo.set_area_membind(array.data, nodeset, MemBindPolicy.BIND, 0)

        nodeset, policy = topo.get_area_membind(array.data, MemBindFlags.BYNODESET)
        print(policy.name, nodeset)
        # >>> BIND 0
        assert policy == MemBindPolicy.BIND


def main() -> None:
    bind_np_array()


if __name__ == "__main__":
    main()
