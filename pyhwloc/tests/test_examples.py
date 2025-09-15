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
from functools import cache as fcache
from pathlib import Path

import pytest

from pyhwloc.hwloc.lib import normpath

tests_dir = Path(normpath(__file__)).parent
demo_dir = tests_dir.parent.parent / "examples"


@fcache
def has_gpu() -> bool:
    try:
        out = subprocess.run(["nvidia-smi", "-L"], stdout=subprocess.PIPE)
        if out.returncode != 0:
            return False
    except FileNotFoundError:
        return False
    gpus = out.stdout.decode("utf-8").strip().splitlines()
    if not gpus:
        return False
    return True


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


def test_membind() -> None:
    script = os.path.join(demo_dir, "membind.py")
    results = subprocess.check_call(["python", script], stdout=subprocess.PIPE)
    assert results == 0


@pytest.mark.skipif(condition=not has_gpu(), reason="GPU discovery tests.")
def test_gds_hops() -> None:
    script = os.path.join(demo_dir, "gds_hops.py")
    results = subprocess.check_call(["python", script], stdout=subprocess.PIPE)
    assert results == 0
