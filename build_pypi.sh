#!/bin/bash
# build_pypi.sh - Script to prepare files for PyPI release with Cython compilation

set -e  # Exit on any error

echo "Preparing files for PyPI release with Cython compilation..."

# Copy core Python files to .pyx files for Cython compilation
echo "Copying core files to .pyx format..."
cp src/farady/core_functions.py src/farady/core_functions.pyx
cp src/farady/pipelines.py src/farady/pipelines.pyx

echo "Files prepared for Cython compilation:"
echo "  - src/farady/core_functions.pyx"
echo "  - src/farady/pipelines.pyx"

echo "Ready for Cython compilation. Use 'python setup.py build_ext --inplace' to compile."

echo "Build preparation complete!"