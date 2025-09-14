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
