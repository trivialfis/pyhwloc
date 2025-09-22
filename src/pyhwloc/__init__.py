# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
The Top Level Module
====================

The top-level pyhwloc exports some shorthands for creating the
:py:class:`~pyhwloc.topology.Topology`.

"""

from __future__ import annotations

from .hwloc import __version__
from .topology import (
    Topology,
    from_pid,
    from_synthetic,
    from_this_system,
    from_xml_buffer,
    from_xml_file,
)

__all__ = [
    "__version__",
    "Topology",
    "from_this_system",
    "from_pid",
    "from_synthetic",
    "from_xml_file",
    "from_xml_buffer",
]
