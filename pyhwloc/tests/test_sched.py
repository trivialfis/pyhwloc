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
import os
import platform

import pytest

from pyhwloc.bitmap import bitmap_free
from pyhwloc.sched import (
    cpuset_from_sched_affinity,
    cpuset_to_sched_affinity,
)


@pytest.mark.skipif(
    condition=platform.system() != "Linux", reason="Linux-specific test"
)
def test_cpuset_sched_affinity() -> None:
    assert hasattr(os, "sched_getaffinity")
    aff0 = os.sched_getaffinity(0)
    cpuset = cpuset_from_sched_affinity(aff0)
    aff1 = cpuset_to_sched_affinity(cpuset)
    bitmap_free(cpuset)
    assert aff0 == aff1
