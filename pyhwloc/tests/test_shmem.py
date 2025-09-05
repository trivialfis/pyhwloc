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
    shmem_topology_get_length,
    shmem_topology_write,
)

from .test_core import Topology

####################################################
# Sharing topologies between processes
####################################################


def _find_mmap_addr(length: int) -> int:
    """Find a suitable memory address for mmap, similar to C test find_mmap_addr."""
    print(f"Testing mmaps to find room for length {length}")

    try:
        # Create a test anonymous mmap to find a working address
        test_map = mmap.mmap(-1, length, flags=mmap.MAP_ANONYMOUS | mmap.MAP_SHARED)
        # Get the address that the system assigned
        test_addr = ctypes.cast(
            ctypes.addressof(ctypes.c_char.from_buffer(test_map)), ctypes.c_void_p
        ).value
        test_map.close()

        print(f" Test mmap succeeded, got address 0x{test_addr:x}")
        return test_addr
    except OSError as e:
        print(f" Test mmap failed (errno {e.errno})")
        return 0


def test_shmem_topology_get_length() -> None:
    topo = Topology()

    length = shmem_topology_get_length(topo.hdl)

    assert length is not None

    # Length should be reasonable.
    assert length >= 1024
    assert length < 100 * 1024 * 1024


def test_shmem_topology_write() -> None:
    """Test writing topology to shared memory."""
    topo = Topology()

    # First get the required length
    length = shmem_topology_get_length(topo.hdl)

    # Find a suitable memory address like the C test does
    forced_addr = _find_mmap_addr(length)
    # Create a temporary file for shared memory
    with tempfile.NamedTemporaryFile() as tmp_file:
        # Add page alignment to file offset like the C test does
        page_size = os.sysconf(os.sysconf_names["SC_PAGE_SIZE"])
        fileoffset = (1 + page_size - 1) & ~(page_size - 1)  # Align to page boundary

        # Resize file to include the offset plus required length
        tmp_file.truncate(fileoffset + length)
        tmp_file.flush()

        print(
            f"Writing topology to shmem at address 0x{forced_addr:x} in file {tmp_file.name} offset {fileoffset}"
        )

        # Write topology to shared memory using the forced address
        # This tells hwloc to write data as if it will be mapped at forced_addr
        try:
            shmem_topology_write(
                topo.hdl,
                tmp_file.fileno(),
                fileoffset,  # use page-aligned file offset like C test
                ctypes.c_void_p(forced_addr),  # use the forced address directly
                length,
            )

            print(f"Wrote length {length}")

            # Now map the file at the same address to verify the data
            with mmap.mmap(tmp_file.fileno(), length, offset=fileoffset) as mm:
                # Verify some data was written (file should not be all zeros)
                mm.seek(0)
                data = mm.read(min(1024, length))
                assert any(b != 0 for b in data), "Written data should not be all zeros"
                print("Verification successful - data was written to shared memory")

        except HwLocError as e:
            if e.errno == 16:  # EBUSY - Device or resource busy
                pytest.skip("Shared memory topology mapping is busy on this system")
            else:
                raise
