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
"""Farady - Islamic Inheritance Distribution Calculator.

A Python library and CLI tool for calculating Islamic inheritance distribution
according to Faraid (Islamic inheritance law).

Usage as library:
    from farady import InheritanceCase, InheritanceCalculator

    case = InheritanceCase(ibn=2, bint=1, umm=1, zawja=True)
    calculator = InheritanceCalculator()
    result = calculator.calculate(case)
    print(result.distribution)

Usage as CLI:
    farady --ibn 2 --bint 1 --umm 1 --zawja
    farady --son 2 --daughter 1 --mother --wife
    farady --help
"""

from importlib.metadata import version as get_pkg_version, PackageNotFoundError

try:
    from farady._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"


def get_version() -> str:
    """Get the current version string.

    Returns version in format: X.Y.Z+gHASH or X.Y.Z.devN+gHASH

    Examples:
        0.1.0+g670ee68         # On or after a tag
        0.1.1.dev5+g670ee68    # 5 commits after v0.1.0 tag
    """
    try:
        return get_pkg_version("farady")
    except PackageNotFoundError:
        return __version__


from farady.distribution import (
    InheritanceCase,
    InheritanceResult,
    InheritanceCalculator,
    calculate_inheritance,
    calculate_from_dict,
    load_csv_cases,
    process_csv_results,
    PRETTY_NAMES,
    HEIR_FIELDS,
    COUNT_HEIRS,
    BOOLEAN_HEIRS,
)

from farady.logging_config import (
    get_logger,
    get_log_dir,
)

from farady.tools_for_testing import build_random_case

from farady import cli

__all__ = [
    "InheritanceCase",
    "InheritanceResult",
    "InheritanceCalculator",
    "calculate_inheritance",
    "calculate_from_dict",
    "load_csv_cases",
    "process_csv_results",
    "PRETTY_NAMES",
    "HEIR_FIELDS",
    "COUNT_HEIRS",
    "BOOLEAN_HEIRS",
    "build_random_case",
    "cli",
    "get_logger",
    "get_log_dir",
]

__version__ = "0.1.0"
