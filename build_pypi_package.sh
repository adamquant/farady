#!/bin/bash
# build_pypi_package.sh - Complete script to build and package for PyPI release

set -e  # Exit on any error

echo "Building PyPI package with Cython compilation..."

# Clean any previous builds
echo "Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Prepare for Cython compilation
echo "Preparing for Cython compilation..."
./build_pypi.sh

# Compile with Cython
echo "Compiling with Cython..."
python setup.py build_ext --inplace

# Build the package
echo "Building the package..."
python -m build

# Show what we've built
echo "Package built successfully:"
ls -la dist/

echo "PyPI package build complete!"