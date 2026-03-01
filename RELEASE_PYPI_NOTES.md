# PyPI Release Workflow

This branch (release-pypi) contains special files for PyPI releases that are not present on the main branch.

## Workflow:
1. To update this branch with changes from main:
   ```bash
   git checkout release-pypi
   git merge main
   ```
   
2. DO NOT force push from main to this branch as it will remove the special files.

3. Special files on this branch:
   - `.github/workflows/pypi-release-tests.yml` - PyPI-specific tests
   - `setup.py` - Cython compilation setup
   - `build_pypi.sh` - Build script for file transformation
   - Modified `pyproject.toml` with Cython dependencies