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
"""Test script for Cython compilation process.

This script verifies that the Cython compilation process works correctly
and that the compiled modules function as expected.

Usage:
    poetry run python tests/test_cython_compilation.py
"""

import sys
import os
import tempfile
import subprocess
from pathlib import Path


def test_cython_compilation():
    """Test the Cython compilation process."""
    print("Testing Cython compilation process...")

    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    try:
        # Test 1: Prepare files for compilation
        print("  1. Testing file preparation...")
        result = subprocess.run(
            [sys.executable, "scripts/cython_compile.py", "prepare"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("     File preparation successful.")

        # Check that .pyx files were created
        pyx_files = [
            "src/farady/core_functions.pyx",
            "src/farady/pipelines.pyx",
        ]

        for pyx_file in pyx_files:
            if not os.path.exists(pyx_file):
                raise Exception(f"Expected .pyx file not created: {pyx_file}")
            print(f"     Found {pyx_file}")

        # Test 2: Compile with Cython
        print("  2. Testing Cython compilation...")
        result = subprocess.run(
            [sys.executable, "scripts/cython_compile.py", "compile"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("     Cython compilation successful.")

        # Test 3: Import compiled modules
        print("  3. Testing imported compiled modules...")

        # Add src to Python path
        sys.path.insert(0, "src")

        # Try importing the compiled modules
        try:
            import farady.core_functions

            print("     Successfully imported farady.core_functions")
        except ImportError as e:
            print(f"     Failed to import farady.core_functions: {e}")
            raise

        try:
            import farady.pipelines

            print("     Successfully imported farady.pipelines")
        except ImportError as e:
            print(f"     Failed to import farady.pipelines: {e}")
            raise

        # Test 4: Clean compiled files
        print("  4. Testing cleanup...")
        result = subprocess.run(
            [sys.executable, "scripts/cython_compile.py", "clean"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("     Cleanup successful.")

        # Check that .pyx files were removed
        for pyx_file in pyx_files:
            if os.path.exists(pyx_file):
                raise Exception(f"Expected .pyx file not removed: {pyx_file}")
            print(f"     Removed {pyx_file}")

        print("All Cython compilation tests passed!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Test failed with exception: {e}")
        return False


if __name__ == "__main__":
    success = test_cython_compilation()
    sys.exit(0 if success else 1)
