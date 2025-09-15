#!/usr/bin/env python3
"""CMake build script and hatchling hook for pyhwloc."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def run_cmake_build(
    source_dir: str | Path = ".",
    build_dir: str | Path = "build",
    build_type: str = "Release",
    parallel_jobs: int | None = None,
    cmake_args: list[str] | None = None,
    skip_on_error: bool = False,
) -> None:
    """Run CMake build process.

    Parameters
    ----------
    source_dir : str | Path
        Source directory containing CMakeLists.txt
    build_dir : str | Path
        Build directory for CMake
    build_type : str
        CMake build type (Release, Debug, etc.)
    parallel_jobs : int | None
        Number of parallel jobs, defaults to cpu_count()
    cmake_args : list[str] | None
        Additional CMake arguments
    skip_on_error : bool
        Whether to continue on build errors
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
        "-S", str(source_path),
        "-B", str(build_path),
        f"-DCMAKE_BUILD_TYPE={build_type}",
        *cmake_args,
    ]

    print(f"Configuring CMake: {' '.join(configure_cmd)}")
    result = subprocess.run(configure_cmd, check=False)
    if result.returncode != 0:
        error_msg = f"CMake configuration failed with code {result.returncode}"
        if skip_on_error:
            print(f"Warning: {error_msg} (continuing anyway)")
            return
        sys.exit(error_msg)

    # Build with CMake
    build_cmd = [
        "cmake",
        "--build", str(build_path),
        "--config", build_type,
        "--parallel", str(parallel_jobs),
    ]

    print(f"Building with CMake: {' '.join(build_cmd)}")
    result = subprocess.run(build_cmd, check=False)
    if result.returncode != 0:
        error_msg = f"CMake build failed with code {result.returncode}"
        if skip_on_error:
            print(f"Warning: {error_msg} (continuing anyway)")
            return
        sys.exit(error_msg)

    print("CMake build completed successfully")


class CMakeBuildHook(BuildHookInterface):
    """Build hook to run CMake during package building."""

    PLUGIN_NAME = "cmake"

    def initialize(self, version: str, build_data):
        """Run CMake build before packaging."""
        print(build_data)
        # print("Running CMake build hook...")

        # Check if native library already exists
        lib_dir = Path(self.root) / "pyhwloc" / "_lib"
        if lib_dir.exists() and list(lib_dir.glob("*.so")):
            print("Native libraries already exist, skipping CMake build")
            return

        # Run CMake build directly
        try:
            run_cmake_build(source_dir=self.root, skip_on_error=True)
            print("CMake build completed successfully")
        except Exception as e:
            print(f"Exception during CMake build: {e}")
            print("Continuing with package build anyway...")


if __name__ == "__main__":
    run_cmake_build()
