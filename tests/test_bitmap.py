# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import copy
import ctypes
from typing import Callable

from pyhwloc.bitmap import Bitmap


def test_bitmap_constructor_empty() -> None:
    bitmap = Bitmap()
    assert bitmap.is_zero()
    assert bitmap.weight() == 0


def test_bitmap_full_ctor() -> None:
    """Test full bitmap constructor."""
    bitmap = Bitmap.full()
    assert bitmap.is_full()
    assert not bitmap.is_zero()
    # Check that many bits are set
    count = 0
    for bit in bitmap:
        count += 1
        if count > 10:
            break


def test_bitmap_str_ctor() -> None:
    # Examples taken from the C document.
    string = "0xffffffff,0x6,0x2"
    bitmap = Bitmap.from_string(string)
    assert str(bitmap) == "1,33-34,64-95"

    string = "1,33-34,64-95"
    bitmap = Bitmap.from_list_string(string)
    assert str(bitmap) == string

    exp = "0xffffffff,0x00000006,0x00000002".replace(",0x", "")
    bitmap = Bitmap.from_taskset_string(exp)
    assert str(bitmap) == string


def test_bitmap_pyseq_ctor() -> None:
    bitmap = Bitmap.from_pyseq([1, 2, 3])
    assert str(bitmap) == "1-3"


def test_bitmap_ulong_ctor() -> None:
    mask = 1 << 2
    bitmap = Bitmap.from_ulong(mask)
    assert 2 in bitmap
    assert bitmap.weight() == 1

    masks = [mask, 1 << 3]
    bitmap = Bitmap.from_ulongs(masks)
    assert 2 in bitmap
    assert (ctypes.sizeof(ctypes.c_ulong) * 8 + 3) in bitmap
    assert bitmap.weight() == 2


def test_bitmap_copy() -> None:
    original = Bitmap.from_pyseq([1, 5, 10])

    def run(meth: Callable) -> None:
        cp = meth(original)
        # Verify they have the same content
        assert original.weight() == cp.weight()
        for bit in original:
            assert bit in cp

        cp.set(20)
        assert 20 in cp
        assert 20 not in original

    run(copy.copy)
    run(copy.deepcopy)


def test_to_string() -> None:
    empty = Bitmap()
    assert str(empty) == ""  # to_list_string
    assert empty.to_string() == "0x0"

    string = "1,33-34,64-95"
    bitmap = Bitmap.from_list_string(string)

    # Test asprintf
    exp = "0xffffffff,0x00000006,0x00000002"
    assert bitmap.to_string() == exp
    assert bitmap.to_taskset_string() == exp.replace(",0x", "")


def test_comparison() -> None:
    bitmap0 = Bitmap.from_pyseq([0, 1, 2])
    bitmap1 = Bitmap.from_pyseq([1])
    assert bitmap1 < bitmap0
    assert bitmap0 > bitmap1
    assert bitmap0 >= bitmap1
    assert bitmap0 != bitmap1
    bitmap2 = Bitmap.from_pyseq([0, 1, 2])
    assert bitmap2 == bitmap0


def test_iter() -> None:
    bitmap = Bitmap.from_pyseq([1, 2, 3])
    for i, idx in enumerate(bitmap):
        assert i + 1 == idx
    assert bitmap.first() == 1
    assert bitmap.last() == 3

    assert bitmap[2] is True
    bitmap[2] = False
    assert bitmap[2] is False


def test_misc_ops() -> None:
    bitmap0 = Bitmap.from_pyseq([1, 2, 3])
    bitmap0.singlify()
    assert 1 in bitmap0 and bitmap0.weight() == 1

    bitmap1 = Bitmap.from_pyseq([1, 2, 3])
    bitmap1.allbut(3)
    assert str(bitmap1) == "0-2,4-"

    bitmap1.only(2)
    assert str(bitmap1) == "2"

    bitmap0 = Bitmap.from_pyseq([1, 2, 3])
    assert bitmap1.is_included(bitmap0) is True
    assert bitmap1.intersects(bitmap0) is True


def test_with_sched_set() -> None:
    cpuset = set([1, 2, 4])
    bitmap = Bitmap.from_sched_set(cpuset)
    loaded = bitmap.to_sched_set()
    assert loaded == cpuset
