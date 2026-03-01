#!/bin/bash
# build_pypi.sh - Script to prepare files for PyPI release with Cython compilation

set -e  # Exit on any error

echo "Preparing files for PyPI release with Cython compilation..."

# Our setup.py is configured to compile the .py files directly
# No need to copy files to .pyx format since we're compiling the original .py files
echo "Setup.py configured to compile .py files directly with Cython"

echo "Ready for Cython compilation. Use 'python setup.py build_ext --inplace' to compile."

echo "Build preparation complete!"