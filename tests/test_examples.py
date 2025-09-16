# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from pyhwloc.hwloc.lib import normpath

from .test_hwloc.utils import has_gpu, has_nice_cap

tests_dir = Path(normpath(__file__)).parent
demo_dir = tests_dir.parent / "examples"


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
