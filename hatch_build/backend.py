# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""CMake build script and hatchling hook for pyhwloc."""

from __future__ import annotations

import os
from typing import Any

import hatchling.build


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    print(
        f"config-settings: {config_settings}",
        f"metadata_directory: {metadata_directory}",
    )
    if config_settings is not None:
        if "fetch-hwloc" in config_settings:
            v = config_settings["fetch-hwloc"]
            assert v in ("True", "False")
            os.environ["PYHWLOC_FETCH_HWLOC"] = "1"
        if "build-dir" in config_settings:
            os.environ["PYHWLOC_BUILD_DIR"] = config_settings["build-dir"]

    try:
        wheel_name = hatchling.build.build_wheel(
            wheel_directory, config_settings, metadata_directory
        )
    finally:
        if "PYHWLOC_FETCH_HWLOC" in os.environ:
            del os.environ["PYHWLOC_FETCH_HWLOC"]
        if "PYHWLOC_BUILD_DIR" in os.environ:
            del os.environ["PYHWLOC_BUILD_DIR"]
    return wheel_name


def build_sdist(
    sdist_directory: str,
    config_settings: dict[str, Any] | None = None,
) -> str:
    sdist_name = hatchling.build.build_sdist(sdist_directory, config_settings)
    return sdist_name


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    if config_settings:
        raise NotImplementedError()
    return hatchling.build.build_editable(
        wheel_directory, config_settings, metadata_directory
    )
