# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import ctypes

from pyhwloc.utils import memoryview_from_memory


def test_memview_from_mem() -> None:
    buf = ctypes.create_string_buffer(1024)
    for i in range(len(buf)):
        k = i % 10
        buf[i] = chr(k).encode("utf-8")
    ptr = ctypes.cast(ctypes.addressof(buf), ctypes.c_void_p)
    mv = memoryview_from_memory(ptr, len(buf), False)
    for i in range(len(buf)):
        k = i % 10
        assert mv[i] == k
