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

import os
import subprocess
from pathlib import Path

import pytest

from pyhwloc.hwloc.lib import normpath
from pyhwloc.tests.test_hwloc.utils import has_gpu, has_nice_cap

tests_dir = Path(normpath(__file__)).parent
demo_dir = tests_dir.parent.parent / "examples"


@pytest.mark.skipif(
    condition=not has_nice_cap(), reason="Running in a sandboxed environment."
)
def test_intro_low_level() -> None:
    script = os.path.join(demo_dir, "intro_low_level.py")
    results = subprocess.check_call(["python", script], stdout=subprocess.PIPE)
    assert results == 0


def test_intro() -> None:
    script = os.path.join(demo_dir, "intro.py")
    results = subprocess.check_call(["python", script], stdout=subprocess.PIPE)
    assert results == 0


@pytest.mark.skipif(condition=not has_gpu(), reason="GPU discovery tests.")
def test_list_gpus() -> None:
    script = os.path.join(demo_dir, "list_gpus.py")
    results = subprocess.check_call(["python", script], stdout=subprocess.PIPE)
    assert results == 0


@pytest.mark.skipif(
    condition=not has_nice_cap(), reason="Running in a sandboxed environment."
)
def test_membind() -> None:
    script = os.path.join(demo_dir, "membind.py")
    results = subprocess.check_call(["python", script], stdout=subprocess.PIPE)
    assert results == 0


@pytest.mark.skipif(condition=not has_gpu(), reason="GPU discovery tests.")
def test_gds_hops() -> None:
    script = os.path.join(demo_dir, "gds_hops.py")
    results = subprocess.check_call(["python", script], stdout=subprocess.PIPE)
    assert results == 0
