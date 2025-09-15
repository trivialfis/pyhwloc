#!/usr/bin/env python3
"""CMake build script and hatchling hook for pyhwloc."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
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
        "-S",
        str(source_path),
        "-B",
        str(build_path),
        f"-DCMAKE_BUILD_TYPE={build_type}",
        *cmake_args,
    ]

    print(f"Configuring CMake: {' '.join(configure_cmd)}")
    result = subprocess.run(configure_cmd, check=False)
    if result.returncode != 0:
        error_msg = f"CMake configuration failed with code {result.returncode}"
        sys.exit(error_msg)

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

    result = subprocess.run(build_cmd, check=False)
    if result.returncode != 0:
        error_msg = f"CMake build failed with code {result.returncode}"
        sys.exit(error_msg)


class CMakeBuildHook(BuildHookInterface):
    """Build hook to run CMake during package building."""

    PLUGIN_NAME = "cmake"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Run CMake build before packaging."""
        # Check if native library already exists
        lib_dir = Path(self.root) / "pyhwloc" / "_lib"
        if lib_dir.exists() and (
            list(lib_dir.glob("*pyhwloc.so")) or list(lib_dir.glob("*pyhwloc.dll"))
        ):
            print("Native libraries already exist, skipping CMake build")
            self._copy_dependencies_to_wheel()
            return

        # Run CMake build directly
        run_cmake_build(source_dir=self.root)

        # Copy dependency libraries to the wheel
        self._copy_dependencies_to_wheel()

    def _copy_dependencies_to_wheel(self) -> None:
        """Copy dependency libraries from CMake output to wheel."""
        deps_file = Path(self.root) / "build" / "hwloc_deps.txt"

        lib_dir = Path(self.root) / "pyhwloc" / "_lib"
        lib_dir.mkdir(exist_ok=True)

        # Read dependency paths and copy them
        with open(deps_file, 'r') as f:
            for line in f:
                dep_path = Path(line.strip())
                if dep_path.exists() and dep_path.is_file():
                    dest_path = lib_dir / dep_path.name
                    if not dest_path.exists():
                        print(f"Copying dependency: {dep_path} -> {dest_path}")
                        shutil.copy2(dep_path, dest_path)
                    else:
                        print(f"Dependency already exists: {dest_path}")
                else:
                    raise FileNotFoundError(f"Dependency not found: {dep_path}")


if __name__ == "__main__":
    run_cmake_build()
