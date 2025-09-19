# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import ctypes
import platform
from ctypes.util import find_library

if platform.system() == "Windows":
    # For older Windows versions, we need msvcrt.
    _libc = ctypes.CDLL(find_library("ucrtbase"))
else:
    _libc = ctypes.CDLL(find_library("c"))


_libc.free.argtypes = [ctypes.c_void_p]


def free(ptr: ctypes._Pointer | ctypes.c_void_p | ctypes.c_char_p) -> None:
    _libc.free(ctypes.cast(ptr, ctypes.c_void_p))


_libc.malloc.argtypes = [ctypes.c_size_t]
_libc.malloc.restype = ctypes.c_void_p


def malloc(n_bytes: int) -> ctypes.c_void_p:
    return ctypes.cast(_libc.malloc(ctypes.c_size_t(n_bytes)), ctypes.c_void_p)


_libc.strerror.restype = ctypes.c_char_p
_libc.strerror.argtypes = [ctypes.c_int]


def strerror(errno: int) -> str | None:
    msg = _libc.strerror(ctypes.c_int(errno))
    if not msg:
        return None
    return msg.decode("utf-8")
