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
import platform
from typing import Callable, ParamSpec, Type, TypeVar

from .libc import strerror as cstrerror


def normpath(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


_file_path = normpath(__file__)

if platform.system() == "Linux":
    prefix = os.path.expanduser("~/ws/pyhwloc_dev/hwloc/build/hwloc/.libs")
    _LIB = ctypes.CDLL(os.path.join(prefix, "libhwloc.so"), use_errno=True)
    _lib_path = normpath(
        os.path.join(
            os.path.dirname(_file_path), os.path.pardir, "_lib", "libpyhwloc.so"
        )
    )
else:
    prefix = os.path.expanduser("C:/Users/jiamingy/ws/pyhwloc_dev/bin/")
    _LIB = ctypes.CDLL(os.path.join(prefix, "hwloc.dll"), use_errno=True)
    _lib_path = normpath(
        os.path.join(os.path.dirname(_file_path), os.path.pardir, "_lib", "pyhwloc.dll")
    )


_pyhwloc_lib = ctypes.cdll.LoadLibrary(_lib_path)


class HwLocError(RuntimeError):
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
    if status != 0:
        err = ctypes.get_errno()
        msg = cstrerror(err)
        if err == errno.ENOSYS:
            raise NotImplementedError(msg)
        raise HwLocError(status, err, msg)


_P = ParamSpec("_P")
_R = TypeVar("_R")


def _cfndoc(fn: Callable[_P, _R]) -> Callable[_P, _R]:
    doc = f"See :cpp:func:`hwloc_{fn.__name__}`"
    fn.__doc__ = doc
    return fn


def _cenumdoc(enum: Type) -> Type:
    doc = f"""See :cpp:enum:`{enum.__name__}`."""
    enum.__doc__ = doc
    return enum
