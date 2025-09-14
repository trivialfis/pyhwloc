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
import platform
from ctypes.util import find_library

if platform.system() == "Windows":
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
