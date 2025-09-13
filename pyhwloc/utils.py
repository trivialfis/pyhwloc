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
