# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
The bitmap API
==============
"""

from __future__ import annotations

import ctypes
from typing import Callable

from .lib import _LIB, HwLocError, _cfndoc, _checkc, _hwloc_error
from .libc import free as cfree
from .libc import strerror as cstrerror

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00161.php#gae679434c1a5f41d3560a8a7e2c1b0dee

bitmap_t = ctypes.c_void_p
const_bitmap_t = ctypes.c_void_p


_LIB.hwloc_bitmap_alloc.argtypes = []
_LIB.hwloc_bitmap_alloc.restype = ctypes.c_void_p


@_cfndoc
def bitmap_alloc() -> bitmap_t:
    ptr = ctypes.cast(_LIB.hwloc_bitmap_alloc(), bitmap_t)
    if not ptr:
        raise _hwloc_error("hwloc_bitmap_alloc")
    return ptr


_LIB.hwloc_bitmap_alloc_full.argtypes = []
_LIB.hwloc_bitmap_alloc_full.restype = ctypes.c_void_p


@_cfndoc
def bitmap_alloc_full() -> bitmap_t:
    ptr = ctypes.cast(_LIB.hwloc_bitmap_alloc_full(), bitmap_t)
    if not ptr:
        raise _hwloc_error("hwloc_bitmap_alloc_full")
    return ptr


_LIB.hwloc_bitmap_free.argtypes = [bitmap_t]


@_cfndoc
def bitmap_free(bitmap: bitmap_t) -> None:
    _LIB.hwloc_bitmap_free(bitmap)


_LIB.hwloc_bitmap_dup.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_dup.restype = bitmap_t


@_cfndoc
def bitmap_dup(bitmap: const_bitmap_t) -> bitmap_t:
    return ctypes.cast(_LIB.hwloc_bitmap_dup(bitmap), bitmap_t)


_LIB.hwloc_bitmap_copy.argtypes = [bitmap_t, const_bitmap_t]
_LIB.hwloc_bitmap_copy.restype = ctypes.c_int


@_cfndoc
def bitmap_copy(dst: bitmap_t, src: const_bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_copy(dst, src))


# Bitmap/String Conversion
_LIB.hwloc_bitmap_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    const_bitmap_t,
]
_LIB.hwloc_bitmap_snprintf.restype = ctypes.c_int


@_cfndoc
def bitmap_snprintf(
    buf: ctypes.c_char_p | ctypes.Array, buflen: int, bitmap: const_bitmap_t
) -> int:
    n_written = _LIB.hwloc_bitmap_snprintf(buf, buflen, bitmap)
    if n_written == -1:
        _checkc(n_written)
    return n_written


_LIB.hwloc_bitmap_asprintf.argtypes = [
    ctypes.POINTER(ctypes.c_char_p),
    const_bitmap_t,
]
_LIB.hwloc_bitmap_asprintf.restype = ctypes.c_int


def _asprintf_impl(bitmap: const_bitmap_t, fn: Callable) -> str:
    strp = ctypes.c_char_p(0)
    try:
        n_written = fn(ctypes.byref(strp), bitmap)
        if n_written == -1:
            err = ctypes.get_errno()
            msg = cstrerror(err)
            raise HwLocError(-1, err, msg)

        if n_written > 0:
            assert strp.value is not None
            string = strp.value.decode("utf-8")
            assert len(string) == n_written
        else:
            string = ""
        return string
    finally:
        if strp:
            cfree(strp)


@_cfndoc
def bitmap_asprintf(bitmap: const_bitmap_t) -> str:
    return _asprintf_impl(bitmap, _LIB.hwloc_bitmap_asprintf)


_LIB.hwloc_bitmap_sscanf.argtypes = [bitmap_t, ctypes.c_char_p]
_LIB.hwloc_bitmap_sscanf.restype = ctypes.c_int


@_cfndoc
def bitmap_sscanf(bitmap: bitmap_t, string: str) -> None:
    string_bytes = string.encode("utf-8")
    _checkc(_LIB.hwloc_bitmap_sscanf(bitmap, string_bytes))


_LIB.hwloc_bitmap_list_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    const_bitmap_t,
]
_LIB.hwloc_bitmap_list_snprintf.restype = ctypes.c_int


@_cfndoc
def bitmap_list_snprintf(
    buf: ctypes.c_char_p | ctypes.Array, buflen: int, bitmap: const_bitmap_t
) -> int:
    return _LIB.hwloc_bitmap_list_snprintf(buf, buflen, bitmap)


_LIB.hwloc_bitmap_list_asprintf.argtypes = [
    ctypes.POINTER(ctypes.c_char_p),
    const_bitmap_t,
]
_LIB.hwloc_bitmap_list_asprintf.restype = ctypes.c_int


@_cfndoc
def bitmap_list_asprintf(bitmap: const_bitmap_t) -> str:
    return _asprintf_impl(bitmap, _LIB.hwloc_bitmap_list_asprintf)


_LIB.hwloc_bitmap_list_sscanf.argtypes = [bitmap_t, ctypes.c_char_p]
_LIB.hwloc_bitmap_list_sscanf.restype = ctypes.c_int


@_cfndoc
def bitmap_list_sscanf(bitmap: bitmap_t, string: str) -> None:
    string_bytes = string.encode("utf-8")
    _checkc(_LIB.hwloc_bitmap_list_sscanf(bitmap, string_bytes))


_LIB.hwloc_bitmap_taskset_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    const_bitmap_t,
]
_LIB.hwloc_bitmap_taskset_snprintf.restype = ctypes.c_int


@_cfndoc
def bitmap_taskset_snprintf(
    buf: ctypes.c_char_p | ctypes.Array, buflen: int, bitmap: const_bitmap_t
) -> int:
    return _LIB.hwloc_bitmap_taskset_snprintf(buf, buflen, bitmap)


_LIB.hwloc_bitmap_taskset_asprintf.argtypes = [
    ctypes.POINTER(ctypes.c_char_p),
    const_bitmap_t,
]
_LIB.hwloc_bitmap_taskset_asprintf.restype = ctypes.c_int


@_cfndoc
def bitmap_taskset_asprintf(bitmap: const_bitmap_t) -> str:
    return _asprintf_impl(bitmap, _LIB.hwloc_bitmap_taskset_asprintf)


_LIB.hwloc_bitmap_taskset_sscanf.argtypes = [bitmap_t, ctypes.c_char_p]
_LIB.hwloc_bitmap_taskset_sscanf.restype = ctypes.c_int


@_cfndoc
def bitmap_taskset_sscanf(bitmap: bitmap_t, string: str) -> None:
    string_bytes = string.encode("utf-8")
    _checkc(_LIB.hwloc_bitmap_taskset_sscanf(bitmap, string_bytes))


_LIB.hwloc_bitmap_singlify.argtypes = [bitmap_t]

# Building bitmaps
_LIB.hwloc_bitmap_zero.argtypes = [bitmap_t]


@_cfndoc
def bitmap_zero(bitmap: bitmap_t) -> None:
    _LIB.hwloc_bitmap_zero(bitmap)


_LIB.hwloc_bitmap_fill.argtypes = [bitmap_t]


@_cfndoc
def bitmap_fill(bitmap: bitmap_t) -> None:
    _LIB.hwloc_bitmap_fill(bitmap)


_LIB.hwloc_bitmap_only.argtypes = [bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_only.restype = ctypes.c_int


@_cfndoc
def bitmap_only(bitmap: bitmap_t, id: int) -> None:
    _checkc(_LIB.hwloc_bitmap_only(bitmap, id))


_LIB.hwloc_bitmap_allbut.argtypes = [bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_allbut.restype = ctypes.c_int


@_cfndoc
def bitmap_allbut(bitmap: bitmap_t, id: int) -> None:
    _checkc(_LIB.hwloc_bitmap_allbut(bitmap, id))


_LIB.hwloc_bitmap_from_ulong.argtypes = [bitmap_t, ctypes.c_ulong]
_LIB.hwloc_bitmap_from_ulong.restype = ctypes.c_int


@_cfndoc
def bitmap_from_ulong(bitmap: bitmap_t, mask: int) -> None:
    _checkc(_LIB.hwloc_bitmap_from_ulong(bitmap, ctypes.c_ulong(mask)))


_LIB.hwloc_bitmap_from_ith_ulong.argtypes = [
    bitmap_t,
    ctypes.c_uint,
    ctypes.c_ulong,
]
_LIB.hwloc_bitmap_from_ith_ulong.restype = ctypes.c_int


@_cfndoc
def bitmap_from_ith_ulong(bitmap: bitmap_t, i: int, mask: int) -> None:
    _checkc(_LIB.hwloc_bitmap_from_ith_ulong(bitmap, i, ctypes.c_ulong(mask)))


_LIB.hwloc_bitmap_from_ulongs.argtypes = [
    bitmap_t,
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_ulong),
]
_LIB.hwloc_bitmap_from_ulongs.restype = ctypes.c_int


# ctypes.POINTER(ctypes.c_ulong)
@_cfndoc
def bitmap_from_ulongs(
    bitmap: bitmap_t, nr: int, masks: ctypes._Pointer | ctypes.Array
) -> None:
    _checkc(_LIB.hwloc_bitmap_from_ulongs(bitmap, nr, masks))


# Modifying bitmaps
_LIB.hwloc_bitmap_set.argtypes = [bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_set.restype = ctypes.c_int


@_cfndoc
def bitmap_set(bitmap: bitmap_t, id: int) -> None:
    _checkc(_LIB.hwloc_bitmap_set(bitmap, id))


_LIB.hwloc_bitmap_set_range.argtypes = [bitmap_t, ctypes.c_uint, ctypes.c_int]
_LIB.hwloc_bitmap_set_range.restype = ctypes.c_int


@_cfndoc
def bitmap_set_range(bitmap: bitmap_t, begin: int, end: int) -> None:
    _checkc(_LIB.hwloc_bitmap_set_range(bitmap, begin, end))


_LIB.hwloc_bitmap_set_ith_ulong.argtypes = [
    bitmap_t,
    ctypes.c_uint,
    ctypes.c_ulong,
]
_LIB.hwloc_bitmap_set_ith_ulong.restype = ctypes.c_int


@_cfndoc
def bitmap_set_ith_ulong(bitmap: bitmap_t, i: int, mask: int) -> None:
    _checkc(_LIB.hwloc_bitmap_set_ith_ulong(bitmap, i, mask))


_LIB.hwloc_bitmap_clr.argtypes = [bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_clr.restype = ctypes.c_int


@_cfndoc
def bitmap_clr(bitmap: bitmap_t, id: int) -> None:
    _checkc(_LIB.hwloc_bitmap_clr(bitmap, id))


_LIB.hwloc_bitmap_clr_range.argtypes = [bitmap_t, ctypes.c_uint, ctypes.c_int]
_LIB.hwloc_bitmap_clr_range.restype = ctypes.c_int


@_cfndoc
def bitmap_clr_range(bitmap: bitmap_t, begin: int, end: int) -> None:
    _checkc(_LIB.hwloc_bitmap_clr_range(bitmap, begin, end))


_LIB.hwloc_bitmap_singlify.argtypes = [bitmap_t]
_LIB.hwloc_bitmap_singlify.restype = ctypes.c_int


@_cfndoc
def bitmap_singlify(bitmap: bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_singlify(bitmap))


# Consulting bitmaps
_LIB.hwloc_bitmap_to_ulong.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_to_ulong.restype = ctypes.c_ulong


@_cfndoc
def bitmap_to_ulong(bitmap: const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_to_ulong(bitmap)


_LIB.hwloc_bitmap_to_ith_ulong.argtypes = [const_bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_to_ith_ulong.restype = ctypes.c_ulong


@_cfndoc
def bitmap_to_ith_ulong(bitmap: const_bitmap_t, i: int) -> int:
    return _LIB.hwloc_bitmap_to_ith_ulong(bitmap, i)


_LIB.hwloc_bitmap_to_ulongs.argtypes = [
    const_bitmap_t,
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_ulong),
]
_LIB.hwloc_bitmap_to_ulongs.restype = ctypes.c_int


# ctypes.POINTER(ctypes.c_ulong)
@_cfndoc
def bitmap_to_ulongs(bitmap: const_bitmap_t, nr: int, masks: ctypes._Pointer) -> None:
    _checkc(_LIB.hwloc_bitmap_to_ulongs(bitmap, nr, masks))


_LIB.hwloc_bitmap_nr_ulongs.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_nr_ulongs.restype = ctypes.c_int


@_cfndoc
def bitmap_nr_ulongs(bitmap: const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_nr_ulongs(bitmap)


_LIB.hwloc_bitmap_isset.argtypes = [const_bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_isset.restype = ctypes.c_int


@_cfndoc
def bitmap_isset(bitmap: const_bitmap_t, i: int) -> bool:
    return bool(_LIB.hwloc_bitmap_isset(bitmap, i))


_LIB.hwloc_bitmap_iszero.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_iszero.restype = ctypes.c_int


@_cfndoc
def bitmap_iszero(bitmap: const_bitmap_t) -> bool:
    return bool(_LIB.hwloc_bitmap_iszero(bitmap))


_LIB.hwloc_bitmap_isfull.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_isfull.restype = ctypes.c_int


@_cfndoc
def bitmap_isfull(bitmap: const_bitmap_t) -> bool:
    return bool(_LIB.hwloc_bitmap_isfull(bitmap))


_LIB.hwloc_bitmap_first.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_first.restype = ctypes.c_int


@_cfndoc
def bitmap_first(bitmap: const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_first(bitmap)


_LIB.hwloc_bitmap_next.argtypes = [const_bitmap_t, ctypes.c_int]
_LIB.hwloc_bitmap_next.restype = ctypes.c_int


@_cfndoc
def bitmap_next(bitmap: const_bitmap_t, prev: int) -> int:
    return _LIB.hwloc_bitmap_next(bitmap, prev)


_LIB.hwloc_bitmap_last.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_last.restype = ctypes.c_int


@_cfndoc
def bitmap_last(bitmap: const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_last(bitmap)


_LIB.hwloc_bitmap_weight.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_weight.restype = ctypes.c_int


@_cfndoc
def bitmap_weight(bitmap: const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_weight(bitmap)


_LIB.hwloc_bitmap_first_unset.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_first_unset.restype = ctypes.c_int


@_cfndoc
def bitmap_first_unset(bitmap: const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_first_unset(bitmap)


_LIB.hwloc_bitmap_next_unset.argtypes = [const_bitmap_t, ctypes.c_int]
_LIB.hwloc_bitmap_next_unset.restype = ctypes.c_int


@_cfndoc
def bitmap_next_unset(bitmap: const_bitmap_t, prev: int) -> int:
    return _LIB.hwloc_bitmap_next_unset(bitmap, prev)


_LIB.hwloc_bitmap_last_unset.argtypes = [const_bitmap_t]
_LIB.hwloc_bitmap_last_unset.restype = ctypes.c_int


@_cfndoc
def bitmap_last_unset(bitmap: const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_last_unset(bitmap)


# Combining bitmaps
_LIB.hwloc_bitmap_or.argtypes = [
    bitmap_t,
    const_bitmap_t,
    const_bitmap_t,
]
_LIB.hwloc_bitmap_or.restype = ctypes.c_int


@_cfndoc
def bitmap_or(res: bitmap_t, bitmap1: const_bitmap_t, bitmap2: const_bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_or(res, bitmap1, bitmap2))


_LIB.hwloc_bitmap_and.argtypes = [
    bitmap_t,
    const_bitmap_t,
    const_bitmap_t,
]
_LIB.hwloc_bitmap_and.restype = ctypes.c_int


@_cfndoc
def bitmap_and(res: bitmap_t, bitmap1: const_bitmap_t, bitmap2: const_bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_and(res, bitmap1, bitmap2))


_LIB.hwloc_bitmap_andnot.argtypes = [
    bitmap_t,
    const_bitmap_t,
    const_bitmap_t,
]
_LIB.hwloc_bitmap_andnot.restype = ctypes.c_int


@_cfndoc
def bitmap_andnot(
    res: bitmap_t, bitmap1: const_bitmap_t, bitmap2: const_bitmap_t
) -> None:
    _checkc(_LIB.hwloc_bitmap_andnot(res, bitmap1, bitmap2))


_LIB.hwloc_bitmap_xor.argtypes = [
    bitmap_t,
    const_bitmap_t,
    const_bitmap_t,
]
_LIB.hwloc_bitmap_xor.restype = ctypes.c_int


@_cfndoc
def bitmap_xor(res: bitmap_t, bitmap1: const_bitmap_t, bitmap2: const_bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_xor(res, bitmap1, bitmap2))


_LIB.hwloc_bitmap_not.argtypes = [bitmap_t, const_bitmap_t]
_LIB.hwloc_bitmap_not.restype = ctypes.c_int


def bitmap_not(res: bitmap_t, bitmap: const_bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_not(res, bitmap))


# Comparing bitmaps
_LIB.hwloc_bitmap_intersects.argtypes = [const_bitmap_t, const_bitmap_t]
_LIB.hwloc_bitmap_intersects.restype = ctypes.c_int


@_cfndoc
def bitmap_intersects(bitmap1: const_bitmap_t, bitmap2: const_bitmap_t) -> bool:
    return bool(_LIB.hwloc_bitmap_intersects(bitmap1, bitmap2))


_LIB.hwloc_bitmap_isincluded.argtypes = [const_bitmap_t, const_bitmap_t]
_LIB.hwloc_bitmap_isincluded.restype = ctypes.c_int


@_cfndoc
def bitmap_isincluded(sub_bitmap: const_bitmap_t, super_bitmap: const_bitmap_t) -> bool:
    return bool(_LIB.hwloc_bitmap_isincluded(sub_bitmap, super_bitmap))


_LIB.hwloc_bitmap_isequal.argtypes = [const_bitmap_t, const_bitmap_t]
_LIB.hwloc_bitmap_isequal.restype = ctypes.c_int


@_cfndoc
def bitmap_isequal(bitmap1: const_bitmap_t, bitmap2: const_bitmap_t) -> bool:
    return bool(_LIB.hwloc_bitmap_isequal(bitmap1, bitmap2))


_LIB.hwloc_bitmap_compare_first.argtypes = [const_bitmap_t, const_bitmap_t]
_LIB.hwloc_bitmap_compare_first.restype = ctypes.c_int


@_cfndoc
def bitmap_compare_first(bitmap1: const_bitmap_t, bitmap2: const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_compare_first(bitmap1, bitmap2)


_LIB.hwloc_bitmap_compare.argtypes = [const_bitmap_t, const_bitmap_t]
_LIB.hwloc_bitmap_compare.restype = ctypes.c_int


@_cfndoc
def bitmap_compare(bitmap1: const_bitmap_t, bitmap2: const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_compare(bitmap1, bitmap2)
