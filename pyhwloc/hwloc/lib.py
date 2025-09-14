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
import errno
import os
import sys
from typing import Callable, ParamSpec, Type, TypeVar

from .libc import strerror as cstrerror


def normpath(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


_file_path = normpath(__file__)

_IS_WINDOWS = sys.platform == "win32"

if not _IS_WINDOWS:
    prefix = os.path.expanduser("~/ws/pyhwloc_dev/hwloc/build/hwloc/.libs")
    _LIB = ctypes.CDLL(os.path.join(prefix, "libhwloc.so"), use_errno=True)
    _libname = os.path.join("_lib", "libpyhwloc.so")
    _lib_path = normpath(
        os.path.join(
            os.path.dirname(_file_path),
            os.path.pardir,
            _libname,
        )
    )
else:
    prefix = os.path.expanduser(
        "C:/Users/jiamingy/ws/pyhwloc_dev/hwloc/contrib/windows-cmake/build/"
    )
    _LIB = ctypes.CDLL(
        os.path.join(prefix, "hwloc.dll"), use_errno=True, use_last_error=True
    )
    _libname = os.path.join("_lib", "pyhwloc.dll")
    _lib_path = normpath(
        os.path.join(
            os.path.dirname(_file_path),
            os.path.pardir,
            _libname,
        )
    )


_pyhwloc_lib = ctypes.cdll.LoadLibrary(_lib_path)


class HwLocError(RuntimeError):
    """Generic catch-all runtime error reported by pyhwloc."""

    def __init__(self, status: int, err: int, msg: bytes | str | None) -> None:
        self.status = status
        self.errno = err
        if isinstance(msg, bytes):
            self.msg: str | None = msg.decode("utf-8")
        else:
            self.msg = msg

        super().__init__(
            f"status: {self.status}, errno: {self.errno}, error: {self.msg}"
        )


def _checkc(status: int) -> None:
    """Raise errors for hwloc functions."""
    if status == 0:
        return

    err = ctypes.get_errno()
    msg = cstrerror(err)
    if err == errno.ENOSYS:
        raise NotImplementedError(msg)
    elif err == errno.EINVAL:
        raise ValueError(msg)
    elif err == errno.ENOMEM:
        raise MemoryError(msg)
    if err == 0 and _IS_WINDOWS:
        werr = ctypes.get_last_error()  # type: ignore[attr-defined]
        if werr != 0:
            raise ctypes.WinError(werr)  # type: ignore[attr-defined]
    raise HwLocError(status, err, msg)


def _hwloc_error(name: str) -> HwLocError:
    """Alternative constructor for the :py:class:`HwLocError` for functions that don't
    have status code as return value.

    """
    err = ctypes.get_errno()
    msg = f"`{name}` failed"
    c_msg = cstrerror(err)
    if c_msg is not None:
        msg += ":\n"
        msg + c_msg
    else:
        msg += "."
    return HwLocError(-1, err, msg)


_P = ParamSpec("_P")
_R = TypeVar("_R")


def _cfndoc(fn: Callable[_P, _R]) -> Callable[_P, _R]:
    doc = f"See :c:func:`hwloc_{fn.__name__}`"
    fn.__doc__ = doc
    return fn


def _c_prefix_fndoc(prefix: str) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    def _decorator(fn: Callable[_P, _R]) -> Callable[_P, _R]:
        doc = f"See :c:func:`hwloc_{prefix}_{fn.__name__}`"
        fn.__doc__ = doc
        return fn

    return _decorator


def _cenumdoc(enum: Type) -> Type:
    doc = f"""See :c:enum:`{enum.__name__}`."""
    enum.__doc__ = doc
    return enum


def _cstructdoc(parent: str | None = None) -> Callable[[Type], Type]:

    def _decorator(struct: Type) -> Type:
        assert issubclass(struct, ctypes.Structure), struct
        if parent is not None:
            doc = f"""See :c:struct:`{parent}.{struct.__name__}`"""
        else:
            doc = f"""See :c:struct:`{struct.__name__}`"""
        struct.__doc__ = doc
        return struct

    return _decorator


def _cuniondoc(parent: str | None = None) -> Callable[[Type], Type]:

    def _decorator(union: Type) -> Type:
        assert issubclass(union, ctypes.Union)
        if parent is not None:
            doc = f"""See :c:union:`{parent}.{union.__name__}`"""
        else:
            doc = f"""See :c:union:`{union.__name__}`"""
        union.__doc__ = doc
        return union

    return _decorator
