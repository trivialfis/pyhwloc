# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""CMake build script and hatchling hook for pyhwloc."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def run_cmake_build(
    source_dir: str | Path = ".",
    build_dir: str | Path = "build",
    build_type: str = "Release",
    parallel_jobs: int | None = None,
    cmake_args: list[str] | None = None,
) -> None:
    """Run CMake build process.

    Parameters
    ----------
    source_dir :
        Source directory containing CMakeLists.txt
    build_dir :
        Build directory for CMake
    build_type :
        CMake build type (Release, Debug, etc.)
    parallel_jobs :
        Number of parallel jobs, defaults to cpu_count()
    cmake_args :
        Additional CMake arguments

    """
    source_path = Path(source_dir).resolve()
    build_path = Path(build_dir).resolve()

    if cmake_args is None:
        cmake_args = []

    if parallel_jobs is None:
        parallel_jobs = os.cpu_count() or 1

    # Create build directory
    build_path.mkdir(exist_ok=True)

    # Configure CMake
    configure_cmd = [
        "cmake",
        "-S",
        str(source_path),
        "-B",
        str(build_path),
        f"-DCMAKE_BUILD_TYPE={build_type}",
        *cmake_args,
    ]

    print(f"CMake config: {' '.join(configure_cmd)}")
    result = subprocess.run(configure_cmd, check=False)
    if result.returncode != 0:
        error_msg = f"CMake configuration failed with code {result.returncode}"
        raise RuntimeError(error_msg)

    # Build with CMake
    build_cmd = [
        "cmake",
        "--build",
        str(build_path),
        "--config",
        build_type,
        "--parallel",
        str(parallel_jobs),
    ]
    print(f"CMake build: {' '.join(build_cmd)}")

    result = subprocess.run(build_cmd, check=False)
    if result.returncode != 0:
        error_msg = f"CMake build failed with code {result.returncode}"
        raise RuntimeError(error_msg)

    install_cmd = [
        "cmake",
        "--install",
        str(build_path),
        "--config",
        build_type,
        "--parallel",
        str(parallel_jobs),
    ]
    print(f"CMake install: {' '.join(install_cmd)}")
    result = subprocess.run(install_cmd, check=True)
    if result.returncode != 0:
        error_msg = f"CMake install failed with code {result.returncode}"
        raise RuntimeError(error_msg)


class CMakeBuildHook(BuildHookInterface):
    """Build hook to run CMake during package building."""

    PLUGIN_NAME = "cmake"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Run CMake build before packaging."""
        # Check if native library already exists
        lib_dir = Path(self.root) / "src" / "pyhwloc" / "_lib"
        if lib_dir.exists() and (
            list(lib_dir.glob("*pyhwloc.so")) or list(lib_dir.glob("*pyhwloc.dll"))
        ):
            print("Native libraries already exist, skipping CMake build")
            return

        # Run CMake build directly
        run_cmake_build(source_dir=self.root)
