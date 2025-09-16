# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause

"""Utilities for testing."""

from __future__ import annotations

import platform
import subprocess
from functools import cache as fcache
from typing import TypeGuard

import pytest

from pyhwloc.hwloc.bitmap import (
    bitmap_alloc,
    bitmap_free,
)
from pyhwloc.hwloc.core import (
    ObjPtr,
    get_membind,
    topology_destroy,
    topology_init,
    topology_load,
    topology_t,
)


def _skip_if_none(dev_obj: ObjPtr | None) -> TypeGuard[ObjPtr]:
    if dev_obj is None:
        assert platform.system() == "Windows"
        pytest.skip(reason="Windows is not supported")
    return True


@fcache
def has_nice_cap() -> bool:
    hdl = topology_t(0)
    nodeset = bitmap_alloc()
    try:
        topology_init(hdl)
        topology_load(hdl)
        get_membind(hdl, nodeset, 0)
        return True
    except PermissionError:
        return False
    finally:
        bitmap_free(nodeset)
        if hdl:
            topology_destroy(hdl)


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
