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
