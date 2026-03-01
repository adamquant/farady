#!/usr/bin/env python3
# Copyright (C) 2024  Adam Ahmed / SunnaAssets
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Cython compilation automation utility for Farady.

This script automates the process of compiling core Python files with Cython
for PyPI releases while keeping interface files readable.

Usage:
    poetry run python scripts/cython_compile.py prepare    # Prepare files for compilation
    poetry run python scripts/cython_compile.py compile    # Compile with Cython
    poetry run python scripts/cython_compile.py build      # Build package with compiled files
    poetry run python scripts/cython_compile.py clean      # Clean compiled files
    poetry run python scripts/cython_compile.py --help     # Show this help

Process:
    1. prepare: Copy core .py files to .pyx files for compilation
    2. compile: Run Cython compilation on .pyx files
    3. build:   Build package with compiled extensions
    4. clean:   Remove compiled files and artifacts
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


# Core files to compile with Cython (IP-sensitive)
CORE_FILES = [
    "src/farady/core_functions.py",
    "src/farady/pipelines.py",
]

# Files to keep readable (interfaces)
INTERFACE_FILES = [
    "src/farady/classes.py",
    "src/farady/cli.py",
    "src/farady/processing.py",
    "src/farady/__init__.py",
]


def prepare_files() -> None:
    """Prepare files for Cython compilation.

    Copies core Python files to .pyx files for compilation while preserving originals.
    """
    print("Preparing files for Cython compilation...")

    for py_file in CORE_FILES:
        pyx_file = py_file.replace(".py", ".pyx")
        print(f"  Copying {py_file} -> {pyx_file}")
        shutil.copy2(py_file, pyx_file)

    print("Files prepared for Cython compilation.")


def compile_with_cython() -> None:
    """Compile .pyx files with Cython."""
    print("Compiling with Cython...")

    try:
        # Run setup.py to compile extensions
        result = subprocess.run(
            [sys.executable, "setup.py", "build_ext", "--inplace"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Cython compilation successful.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Cython compilation failed:")
        print(e.stderr)
        raise


def build_package() -> None:
    """Build package with compiled extensions."""
    print("Building package with compiled extensions...")

    try:
        # Clean previous builds
        for path in ["build/", "dist/", "*.egg-info/"]:
            subprocess.run(["rm", "-rf", path], shell=True)

        # Build the package
        result = subprocess.run(
            [sys.executable, "-m", "build"], check=True, capture_output=True, text=True
        )
        print("Package built successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Package build failed:")
        print(e.stderr)
        raise


def clean_compiled_files() -> None:
    """Clean compiled files and artifacts."""
    print("Cleaning compiled files and artifacts...")

    # Remove .pyx files
    for py_file in CORE_FILES:
        pyx_file = py_file.replace(".py", ".pyx")
        if os.path.exists(pyx_file):
            print(f"  Removing {pyx_file}")
            os.remove(pyx_file)

    # Remove compiled extensions
    for py_file in CORE_FILES:
        # Remove .so files (Linux/macOS)
        so_file = py_file.replace(".py", ".so").replace("src/", "")
        if os.path.exists(so_file):
            print(f"  Removing {so_file}")
            os.remove(so_file)

        # Remove .pyd files (Windows)
        pyd_file = py_file.replace(".py", ".pyd").replace("src/", "")
        if os.path.exists(pyd_file):
            print(f"  Removing {pyd_file}")
            os.remove(pyd_file)

    # Remove build directories
    build_dirs = ["build/", "dist/"]
    for build_dir in build_dirs:
        if os.path.exists(build_dir):
            print(f"  Removing {build_dir}")
            shutil.rmtree(build_dir)

    # Remove egg-info directories
    for item in os.listdir("."):
        if item.endswith(".egg-info"):
            print(f"  Removing {item}")
            shutil.rmtree(item)

    print("Cleaned compiled files and artifacts.")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "prepare":
        prepare_files()
    elif command == "compile":
        compile_with_cython()
    elif command == "build":
        build_package()
    elif command == "clean":
        clean_compiled_files()
    elif command == "--help" or command == "-h":
        print(__doc__)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
