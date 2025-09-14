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
from collections.abc import Sequence
from typing import Callable, ParamSpec, TypeVar, Union

_P = ParamSpec("_P")
_R = TypeVar("_R")


def _reuse_doc(orig: Callable) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    def fn(fobj: Callable[_P, _R]) -> Callable[_P, _R]:
        fobj.__doc__ = orig.__doc__
        return fobj

    return fn


_Flag = TypeVar("_Flag")
_Flags = Union[int, _Flag, Sequence[_Flag]]


def _or_flags(flags: _Flags) -> int:
    if isinstance(flags, Sequence):
        r = flags[0]
        for f in flags:
            r |= f
        flags = r
    return flags


ctypes.pythonapi.PyMemoryView_FromMemory.argtypes = (
    ctypes.c_void_p,
    ctypes.c_ssize_t,  # size: size of the memory block
    ctypes.c_int,  # flags: 0x100 for read-only, 0x200 for read/write
)
ctypes.pythonapi.PyMemoryView_FromMemory.restype = ctypes.py_object  # Python memoryview


def memoryview_from_memory(
    ptr: ctypes.c_void_p, size: int, read_only: bool
) -> memoryview:
    """Create a Python memoryview from a ctypes poitner.

    Parameters
    ----------
    ptr :
        A ctypes Pointer.
    size :
        Size in bytes.
    read_only :
        Do we need write access to the memory view?

    Returns
    -------
    A Python :py:class:`memoryview` object.

    """
    PyBUF_READ = 0x100
    PyBUF_WRITE = 0x200
    flags = PyBUF_READ if read_only else PyBUF_WRITE
    mv = ctypes.pythonapi.PyMemoryView_FromMemory(ptr, size, flags)
    return mv
