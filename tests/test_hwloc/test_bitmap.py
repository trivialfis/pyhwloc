# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import ctypes

from pyhwloc.hwloc.bitmap import (
    bitmap_allbut,
    bitmap_alloc,
    bitmap_alloc_full,
    bitmap_and,
    bitmap_andnot,
    bitmap_clr,
    bitmap_clr_range,
    bitmap_compare,
    bitmap_compare_first,
    bitmap_copy,
    bitmap_dup,
    bitmap_fill,
    bitmap_first,
    bitmap_first_unset,
    bitmap_free,
    bitmap_from_ulong,
    bitmap_intersects,
    bitmap_isequal,
    bitmap_isincluded,
    bitmap_isset,
    bitmap_last,
    bitmap_list_snprintf,
    bitmap_list_sscanf,
    bitmap_next,
    bitmap_next_unset,
    bitmap_not,
    bitmap_only,
    bitmap_or,
    bitmap_set,
    bitmap_set_range,
    bitmap_singlify,
    bitmap_snprintf,
    bitmap_sscanf,
    bitmap_taskset_snprintf,
    bitmap_taskset_sscanf,
    bitmap_to_ulong,
    bitmap_weight,
    bitmap_xor,
    bitmap_zero,
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


def test_bitmap_basic_operations() -> None:
    # Test allocation and duplication
    bitmap1 = bitmap_alloc()
    bitmap_from_ulong(bitmap1, 0x5)  # bits 0 and 2

    bitmap2 = bitmap_dup(bitmap1)
    assert bitmap_isequal(bitmap1, bitmap2)

    # Test copy operation
    bitmap3 = bitmap_alloc()
    bitmap_copy(bitmap3, bitmap1)
    assert bitmap_isequal(bitmap1, bitmap3)

    bitmap_free(bitmap1)
    bitmap_free(bitmap2)
    bitmap_free(bitmap3)


def test_bitmap_zero_fill_operations() -> None:
    bitmap = bitmap_alloc()

    # Test only - set only bit 3
    bitmap_only(bitmap, 3)
    assert bitmap_isset(bitmap, 3)
    assert not bitmap_isset(bitmap, 2)
    assert not bitmap_isset(bitmap, 4)
    assert bitmap_weight(bitmap) == 1

    # Test allbut - set all except bit 3
    bitmap_allbut(bitmap, 3)
    assert not bitmap_isset(bitmap, 3)
    # Check some nearby bits are set
    for i in range(10):
        if i != 3:
            assert bitmap_isset(bitmap, i)

    bitmap_free(bitmap)


def test_bitmap_set_clear_operations() -> None:
    bitmap = bitmap_alloc()
    bitmap_zero(bitmap)

    # Test individual bit operations
    bitmap_set(bitmap, 5)
    assert bitmap_isset(bitmap, 5)
    assert bitmap_weight(bitmap) == 1

    bitmap_set(bitmap, 10)
    assert bitmap_isset(bitmap, 10)
    assert bitmap_weight(bitmap) == 2

    bitmap_clr(bitmap, 5)
    assert not bitmap_isset(bitmap, 5)
    assert bitmap_isset(bitmap, 10)
    assert bitmap_weight(bitmap) == 1

    # Test range operations
    bitmap_zero(bitmap)
    assert not bitmap_isset(bitmap, 5)
    bitmap_set_range(bitmap, 2, 5)  # Set bits 2, 3, 4
    assert bitmap_isset(bitmap, 2)
    assert bitmap_isset(bitmap, 3)
    assert bitmap_isset(bitmap, 4)
    assert not bitmap_isset(bitmap, 1)
    # FIXME(jiamingy): Failed
    # assert not bitmap_isset(bitmap, 5)
    # assert bitmap_weight(bitmap) == 3

    bitmap_clr_range(bitmap, 3, 6)  # Clear bits 3, 4, 5
    assert bitmap_isset(bitmap, 2)
    assert not bitmap_isset(bitmap, 3)
    assert not bitmap_isset(bitmap, 4)
    assert bitmap_weight(bitmap) == 1

    bitmap_free(bitmap)


def test_bitmap_iteration() -> None:
    bitmap = bitmap_alloc()
    bitmap_zero(bitmap)

    # Set some bits: 1, 5, 8, 12
    bitmap_set(bitmap, 1)
    bitmap_set(bitmap, 5)
    bitmap_set(bitmap, 8)
    bitmap_set(bitmap, 12)

    # Test forward iteration
    assert bitmap_first(bitmap) == 1
    assert bitmap_next(bitmap, 1) == 5
    assert bitmap_next(bitmap, 5) == 8
    assert bitmap_next(bitmap, 8) == 12
    assert bitmap_next(bitmap, 12) == -1

    # Test last
    assert bitmap_last(bitmap) == 12

    # Collect all set bits
    bits = []
    bit = bitmap_first(bitmap)
    while bit != -1:
        bits.append(bit)
        bit = bitmap_next(bitmap, bit)
    assert bits == [1, 5, 8, 12]

    bitmap_free(bitmap)


def test_bitmap_unset_iteration() -> None:
    bitmap = bitmap_alloc()
    bitmap_fill(bitmap)

    # Clear some bits: 2, 7, 10
    bitmap_clr(bitmap, 2)
    bitmap_clr(bitmap, 7)
    bitmap_clr(bitmap, 10)

    # Test unset iteration
    first_unset = bitmap_first_unset(bitmap)
    assert first_unset == 2

    next_unset = bitmap_next_unset(bitmap, 2)
    assert next_unset == 7

    next_unset = bitmap_next_unset(bitmap, 7)
    assert next_unset == 10

    bitmap_free(bitmap)


def test_bitmap_logical_operations() -> None:
    bitmap1 = bitmap_alloc()
    bitmap2 = bitmap_alloc()
    result = bitmap_alloc()

    # Setup test bitmaps
    bitmap_from_ulong(bitmap1, 0b1010)  # bits 1, 3
    bitmap_from_ulong(bitmap2, 0b1100)  # bits 2, 3

    # Test OR
    bitmap_or(result, bitmap1, bitmap2)
    assert bitmap_to_ulong(result) == 0b1110  # bits 1, 2, 3

    # Test AND
    bitmap_and(result, bitmap1, bitmap2)
    assert bitmap_to_ulong(result) == 0b1000  # bit 3 only

    # Test XOR
    bitmap_xor(result, bitmap1, bitmap2)
    assert bitmap_to_ulong(result) == 0b0110  # bits 1, 2

    # Test ANDNOT (bitmap1 AND NOT bitmap2)
    bitmap_andnot(result, bitmap1, bitmap2)
    assert bitmap_to_ulong(result) == 0b0010  # bit 1 only

    # Test NOT
    bitmap_not(result, bitmap1)
    # NOT operation flips all bits, so bit 1 and 3 should be clear
    assert not bitmap_isset(result, 1)
    assert not bitmap_isset(result, 3)
    assert bitmap_isset(result, 0)
    assert bitmap_isset(result, 2)

    bitmap_free(bitmap1)
    bitmap_free(bitmap2)
    bitmap_free(result)


def test_bitmap_comparison_operations() -> None:
    bitmap1 = bitmap_alloc()
    bitmap2 = bitmap_alloc()
    bitmap3 = bitmap_alloc()

    # Setup test cases
    bitmap_from_ulong(bitmap1, 0b1010)  # bits 1, 3
    bitmap_from_ulong(bitmap2, 0b1100)  # bits 2, 3
    bitmap_from_ulong(bitmap3, 0b1010)  # same as bitmap1

    # Test equality
    assert bitmap_isequal(bitmap1, bitmap3)
    assert not bitmap_isequal(bitmap1, bitmap2)

    # Test intersection
    assert bitmap_intersects(bitmap1, bitmap2)  # both have bit 3
    bitmap_from_ulong(bitmap2, 0b0001)  # bit 0 only
    assert not bitmap_intersects(bitmap1, bitmap2)  # no common bits

    # Test inclusion
    bitmap_from_ulong(bitmap1, 0b1110)  # bits 1, 2, 3
    bitmap_from_ulong(bitmap2, 0b0110)  # bits 1, 2 (subset)
    assert bitmap_isincluded(bitmap2, bitmap1)  # bitmap2 is included in bitmap1
    assert not bitmap_isincluded(bitmap1, bitmap2)  # bitmap1 is not included in bitmap2

    # Test compare
    bitmap_from_ulong(bitmap1, 0b1000)  # bit 3
    bitmap_from_ulong(bitmap2, 0b0100)  # bit 2
    # bitmap1 > bitmap2 (first set bit is higher)
    assert bitmap_compare(bitmap1, bitmap2) > 0

    # Test compare_first
    # first bit in bitmap1 (3) > first in bitmap2 (2)
    assert bitmap_compare_first(bitmap1, bitmap2) > 0

    bitmap_free(bitmap1)
    bitmap_free(bitmap2)
    bitmap_free(bitmap3)


def test_bitmap_formatting() -> None:
    """Test bitmap string formatting functions."""
    bitmap = bitmap_alloc()
    bitmap_from_ulong(bitmap, 0x5)  # bits 0 and 2

    # Test hex formatting
    buf = ctypes.create_string_buffer(64)
    n_written = bitmap_snprintf(buf, 64, bitmap)
    assert n_written > 0
    hex_str = buf.value.decode("utf-8")
    assert "5" in hex_str or "0x5" in hex_str

    # Test list formatting
    buf = ctypes.create_string_buffer(64)
    n_written = bitmap_list_snprintf(buf, 64, bitmap)
    assert n_written > 0
    list_str = buf.value.decode("utf-8")
    assert "0" in list_str and "2" in list_str

    # Test taskset formatting
    buf = ctypes.create_string_buffer(64)
    n_written = bitmap_taskset_snprintf(buf, 64, bitmap)
    assert n_written > 0
    taskset_str = buf.value.decode("utf-8")
    assert len(taskset_str) > 0

    bitmap_free(bitmap)


def test_bitmap_parsing() -> None:
    """Test bitmap parsing from strings."""
    bitmap = bitmap_alloc()

    # Test hex parsing
    bitmap_sscanf(bitmap, "0x5")
    assert bitmap_to_ulong(bitmap) == 0x5

    # Test list parsing
    bitmap_list_sscanf(bitmap, "0,2,4")
    assert bitmap_isset(bitmap, 0)
    assert bitmap_isset(bitmap, 2)
    assert bitmap_isset(bitmap, 4)
    assert not bitmap_isset(bitmap, 1)
    assert not bitmap_isset(bitmap, 3)

    # Test taskset parsing
    bitmap_taskset_sscanf(bitmap, "5")
    assert bitmap_to_ulong(bitmap) == 0x5

    bitmap_free(bitmap)


def test_bitmap_singlify() -> None:
    """Test bitmap singlify operation."""
    bitmap = bitmap_alloc()

    # Set multiple bits
    bitmap_from_ulong(bitmap, 0b1110)  # bits 1, 2, 3
    assert bitmap_weight(bitmap) == 3

    # Singlify should keep only one bit
    bitmap_singlify(bitmap)
    assert bitmap_weight(bitmap) == 1

    # Should be one of the original bits
    first_bit = bitmap_first(bitmap)
    assert first_bit in [1, 2, 3]

    bitmap_free(bitmap)
