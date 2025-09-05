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

import ctypes
import mmap
import os
import tempfile

import pytest

from pyhwloc.core import (
    HwLocError,
    shmem_topology_adopt,
    shmem_topology_get_length,
    shmem_topology_write,
    topology_load,
    topology_t,
)

from .test_core import Topology

####################################################
# Sharing topologies between processes
####################################################


def test_shmem_topology_get_length() -> None:
    topo = Topology()

    length = ctypes.c_size_t()
    shmem_topology_get_length(topo.hdl, ctypes.byref(length))

    assert length.value is not None

    # Length should be reasonable.
    assert length.value >= 1024
    assert length.value < 100 * 1024 * 1024
