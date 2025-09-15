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
"""
The Bitmap Interface
====================
"""

from __future__ import annotations

import ctypes
from collections.abc import Iterable
from typing import Iterator, Sequence

from .hwloc import bitmap as _bitmap
from .hwloc import sched as _sched
from .utils import _reuse_doc

__all__ = ["Bitmap", "compare_first"]


class Bitmap:
    """This represents a set of integers (positive or null). A bitmap may be of infinite
    size (all bits are set after some point). A bitmap may even be full if all bits are
    set.

    """

    def __init__(self) -> None:
        self._hdl = _bitmap.bitmap_alloc()
        self._own = True
        _bitmap.bitmap_zero(self._hdl)

    @property
    def native_handle(self) -> _bitmap.bitmap_t:
        return self._hdl

    def __del__(self) -> None:
        """Free the underlying bitmap."""
        if hasattr(self, "_hdl") and self._hdl and self._own:
            _bitmap.bitmap_free(self._hdl)

    @classmethod
    def full(cls) -> Bitmap:
        """Create an infinite bitmap with all bits set."""
        return Bitmap.from_native_handle(_bitmap.bitmap_alloc_full())

    @classmethod
    def from_ulong(cls, mask: int) -> Bitmap:
        bitmap = Bitmap()
        _bitmap.bitmap_from_ulong(bitmap._hdl, mask)
        return bitmap

    @classmethod
    def from_ulongs(cls, mask: Sequence[int]) -> Bitmap:
        bitmap = Bitmap()
        ptr = (ctypes.c_ulong * len(mask))(*mask)
        _bitmap.bitmap_from_ulongs(bitmap._hdl, len(mask), ptr)
        return bitmap

    @classmethod
    def from_ith_ulong(cls, i: int, mask: int) -> Bitmap:
        bitmap = Bitmap()
        _bitmap.bitmap_from_ith_ulong(bitmap._hdl, i, mask)
        return bitmap

    @classmethod
    def from_pyseq(cls, index: Iterable[int]) -> Bitmap:
        bitmap = Bitmap()
        for idx in index:
            bitmap.set(idx)
        return bitmap

    @classmethod
    def from_string(cls, string: str) -> Bitmap:
        """Parse a bitmap from string representation."""
        bitmap = Bitmap()
        _bitmap.bitmap_sscanf(bitmap._hdl, string)
        return bitmap

    @classmethod
    def from_list_string(cls, list_string: str) -> Bitmap:
        """Parse a bitmap from list string representation (e.g., '0,2,4-6')."""
        bitmap = Bitmap()
        _bitmap.bitmap_list_sscanf(bitmap._hdl, list_string)
        return bitmap

    @classmethod
    def from_taskset_string(cls, string: str) -> Bitmap:
        """Parse a bitmap from taskset string representation."""
        bitmap = Bitmap()
        _bitmap.bitmap_taskset_sscanf(bitmap._hdl, string)
        return bitmap

    @classmethod
    def from_sched_set(cls, index: set[int]) -> Bitmap:
        """From a Python set of index, typically used by the ``os.sched_*`` functions to
        represent CPU index.

        """
        return cls.from_native_handle(_sched.cpuset_from_sched_affinity(index), True)

    @classmethod
    def from_native_handle(cls, hdl: _bitmap.bitmap_t, own: bool = True) -> Bitmap:
        bitmap = cls.__new__(cls)
        assert not hasattr(bitmap, "_hdl")
        bitmap._hdl = hdl
        bitmap._own = own
        return bitmap

    def to_sched_set(self) -> set[int]:
        """Convert to a Python set of index, typically used by the ``os.sched_*``
        functions to represent CPU index.

        """
        return _sched.cpuset_to_sched_affinity(self.native_handle)

    def __copy__(self) -> Bitmap:
        return Bitmap.from_native_handle(_bitmap.bitmap_dup(self._hdl))

    def __deepcopy__(self, memo: dict) -> Bitmap:
        return self.__copy__()

    def set(self, bit: int) -> None:
        """Set a bit in the bitmap."""
        _bitmap.bitmap_set(self._hdl, bit)

    def clr(self, bit: int) -> None:
        """Clear a bit in the bitmap."""
        _bitmap.bitmap_clr(self._hdl, bit)

    def set_range(self, begin: int, end: int) -> None:
        """Set a range of bits [begin, end)."""
        _bitmap.bitmap_set_range(self._hdl, begin, end)

    def clear_range(self, begin: int, end: int) -> None:
        """Clear a range of bits [begin, end)."""
        _bitmap.bitmap_clr_range(self._hdl, begin, end)

    def zero(self) -> None:
        """Clear all bits in the bitmap."""
        _bitmap.bitmap_zero(self._hdl)

    def fill(self) -> None:
        """Set all bits in the bitmap."""
        _bitmap.bitmap_fill(self._hdl)

    def only(self, bit: int) -> None:
        """Clear all bits except the specified one."""
        _bitmap.bitmap_only(self._hdl, bit)

    def allbut(self, bit: int) -> None:
        """Set all bits except the specified one."""
        _bitmap.bitmap_allbut(self._hdl, bit)

    def singlify(self) -> None:
        """Keep only the lowest set bit."""
        _bitmap.bitmap_singlify(self._hdl)

    def andnot(self, other: Bitmap) -> Bitmap:
        """Compute the bitwise AND NOT of this bitmap and another."""
        result = Bitmap()
        _bitmap.bitmap_andnot(result._hdl, self._hdl, other._hdl)
        return result

    def to_string(self) -> str:
        """Convert the bitmap to the hwloc bitmap string representation (Hex
        representation of the integers).

        """
        return _bitmap.bitmap_asprintf(self._hdl)

    def to_list_string(self) -> str:
        """Convert the bitmap to a list string representation (e.g., '0,2,4-6')."""
        return _bitmap.bitmap_list_asprintf(self._hdl)

    def to_taskset_string(self) -> str:
        """Convert bitmap to taskset string representation (Concatenated hex strings)."""
        return _bitmap.bitmap_taskset_asprintf(self._hdl)

    def __iter__(self) -> Iterator[int]:
        """Iterate over set bits in the bitmap."""
        bit = _bitmap.bitmap_first(self._hdl)
        while bit != -1:
            yield bit
            bit = _bitmap.bitmap_next(self._hdl, bit)

    def iter_unset(self) -> Iterator[int]:
        """Iterate over unset bits in the bitmap."""
        bit = _bitmap.bitmap_first_unset(self._hdl)
        while bit != -1:
            yield bit
            bit = _bitmap.bitmap_next_unset(self._hdl, bit)

    def weight(self) -> int:
        """Number of set bits in the bitmap."""
        return _bitmap.bitmap_weight(self._hdl)

    def first(self) -> int:
        """First set bit, or -1 if bitmap is empty."""
        return _bitmap.bitmap_first(self._hdl)

    def last(self) -> int:
        """Last set bit, or -1 if bitmap is empty."""
        return _bitmap.bitmap_last(self._hdl)

    @property
    def is_zero(self) -> bool:
        """True if bitmap has no set bits."""
        return _bitmap.bitmap_iszero(self._hdl)

    @property
    def is_full(self) -> bool:
        """True if bitmap has all bits set."""
        return _bitmap.bitmap_isfull(self._hdl)

    def intersects(self, other: Bitmap) -> bool:
        """True if this bitmap intersects with another."""
        return _bitmap.bitmap_intersects(self._hdl, other._hdl)

    def is_included(self, other: Bitmap) -> bool:
        """True if this bitmap is included in another."""
        return _bitmap.bitmap_isincluded(self._hdl, other._hdl)

    def __contains__(self, bit: int) -> bool:
        return _bitmap.bitmap_isset(self._hdl, bit)

    def __getitem__(self, bit: int) -> bool:
        return bit in self

    def __setitem__(self, bit: int, value: bool) -> None:
        if value:
            self.set(bit)
        else:
            self.clr(bit)

    def any(self) -> bool:
        """True if bitmap has any set bits."""
        return not self.is_zero

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bitmap):
            raise TypeError("Expecting Bitmap for comparison.")
        return _bitmap.bitmap_isequal(self._hdl, other._hdl)

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Bitmap):
            raise TypeError("Expecting Bitmap for comparison.")
        return _bitmap.bitmap_compare(self._hdl, other._hdl) == -1

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Bitmap):
            raise TypeError("Expecting Bitmap for comparison.")
        return _bitmap.bitmap_compare(self._hdl, other._hdl) == 1

    def __le__(self, other: object) -> bool:
        return not (self > other)

    def __ge__(self, other: object) -> bool:
        return not (self < other)

    def __or__(self, other: Bitmap) -> Bitmap:
        result = Bitmap()
        _bitmap.bitmap_or(result._hdl, self._hdl, other._hdl)
        return result

    def __and__(self, other: Bitmap) -> Bitmap:
        result = Bitmap()
        _bitmap.bitmap_and(result._hdl, self._hdl, other._hdl)
        return result

    def __xor__(self, other: Bitmap) -> Bitmap:
        result = Bitmap()
        _bitmap.bitmap_xor(result._hdl, self._hdl, other._hdl)
        return result

    def __invert__(self) -> Bitmap:
        result = Bitmap()
        _bitmap.bitmap_not(result._hdl, self._hdl)
        return result

    def __str__(self) -> str:
        return self.to_list_string()

    def __repr__(self) -> str:
        return f"Bitmap({self.to_list_string()!r})"


@_reuse_doc(_bitmap.bitmap_compare_first)
def compare_first(lhs: Bitmap, rhs: Bitmap) -> int:
    return _bitmap.bitmap_compare_first(lhs.native_handle, rhs.native_handle)
