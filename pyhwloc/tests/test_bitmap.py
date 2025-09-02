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
import ctypes

from pyhwloc.core import (
    bitmap_alloc,
    bitmap_alloc_full,
    bitmap_free,
    bitmap_from_ulong,
    bitmap_snprintf,
)


def test_bitmap_alloc() -> None:
    bitmap = bitmap_alloc()
    assert bitmap is not None
    assert isinstance(bitmap, ctypes.c_void_p)
    assert bitmap.value is not None
    bitmap_free(bitmap)

    bitmap = bitmap_alloc_full()
    assert bitmap is not None
    assert isinstance(bitmap, ctypes.c_void_p)
    assert bitmap.value is not None
    bitmap_free(bitmap)


def test_bitmap_misc() -> None:
    bitmap = bitmap_alloc()
    bitmap_from_ulong(bitmap, 0x4)
    buf = ctypes.create_string_buffer(32)
    n_written = bitmap_snprintf(buf, 32, bitmap)
    assert n_written >= 10
    bitmap_free(bitmap)
    assert int(buf.value.decode("utf-8"), 16) == 4
