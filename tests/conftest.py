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
"""Shared fixtures and utilities for monte carlo tests.

This module provides:
- Test case loading from disk
- Result computation and caching
- Failure collection helpers
- Pytest session logging
"""

import sys
import os
import json
import subprocess
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Callable
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from farady import Case, calculate_from_dict
from farady.run_pipeline import _build_distribution


def _get_git_commit() -> str:
    """Get short git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _get_version() -> str:
    """Get version string for logging."""
    try:
        from farady import __version__

        commit = _get_git_commit()
        return f"{__version__}+g{commit}"
    except Exception:
        return "0.0.0+unknown"


_pytest_log_file = None
_test_results = {"passed": [], "failed": [], "skipped": []}


def pytest_sessionstart(session):
    """Log session start with version and timestamp."""
    global _pytest_log_file, _test_results

    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    timestamp_file = datetime.now().strftime("%Y%m%d")
    _pytest_log_file = log_dir / f"pytest_{timestamp_file}.log"

    _test_results = {"passed": [], "failed": [], "skipped": []}

    version = _get_version()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = f"""
{"=" * 80}
PYTEST SESSION - {timestamp}
VERSION: {version}
{"=" * 80}
"""

    with open(_pytest_log_file, "a") as f:
        f.write(header)


def pytest_runtest_logreport(report):
    """Log each test result."""
    global _test_results

    if _pytest_log_file is None:
        return

    if report.when == "call":
        if report.passed:
            _test_results["passed"].append(report.nodeid)
            status = "PASSED"
        elif report.failed:
            _test_results["failed"].append(report.nodeid)
            status = "FAILED"
        elif report.skipped:
            _test_results["skipped"].append(report.nodeid)
            status = "SKIPPED"
        else:
            return

        with open(_pytest_log_file, "a") as f:
            f.write(f"{status}: {report.nodeid}\n")
            if report.failed and hasattr(report, "longrepr"):
                f.write(f"  Error: {report.longrepr}\n")


def pytest_sessionfinish(session, exitstatus):
    """Log session summary."""
    if _pytest_log_file is None:
        return

    passed = len(_test_results["passed"])
    failed = len(_test_results["failed"])
    skipped = len(_test_results["skipped"])
    total = passed + failed + skipped

    summary = f"""
{"=" * 80}
SUMMARY: {passed} passed, {failed} failed, {skipped} skipped (total: {total})
{"=" * 80}
"""

    with open(_pytest_log_file, "a") as f:
        f.write(summary)


def _resolve_test_cases_path() -> Path | None:
    candidates = [
        Path(__file__).parent / "data" / "test_cases.npz",
        Path(__file__).parent / "data" / "monte" / "test_cases.npz",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    matches = list(Path(__file__).parent.rglob("test_cases.npz"))
    return matches[0] if matches else None


def load_test_cases() -> dict[str, list]:
    """Load pre-generated test cases from disk."""
    data_path = _resolve_test_cases_path()
    if data_path is None:
        pytest.skip("test_cases.npz not found")
    data = np.load(data_path, allow_pickle=True)
    return {
        "ordinary": list(data["ordinary"]),
        "no_fare": list(data["no_fare"]),
        "hawashi": list(data["hawashi"]),
    }


def case_to_result(case: Case) -> dict:
    distribution = _build_distribution(case)
    denominator = case.raas
    numerators = {
        name: int(heir.get("shares", 0))
        for name, heir in zip(case._all_heir_names, case._all_heirs)
        if heir.get("shares")
    }
    return {
        "distribution": distribution,
        "ending": case.ending,
        "asib": case.asib,
        "total": sum(distribution.values()),
        "status": case.status,
        "denominator": denominator,
        "numerators": numerators,
    }


def result_to_dict(result: dict) -> dict:
    """Convert Result dict to JSON-serializable dict."""
    return {
        "distribution": result["distribution"],
        "ending": result["ending"],
        "asib": result["asib"],
        "total": result["total"],
        "status": result["status"],
        "denominator": result["denominator"],
        "numerators": result["numerators"],
    }


def _sample_cases(cases: list, limit: int) -> list:
    if limit <= 0:
        return []
    return cases[:limit]


def compute_all_results() -> dict[str, list]:
    """Run calculations on test cases, cache results as (case, result) tuples."""
    cases = load_test_cases()
    limit = int(os.environ.get("FARADY_MONTE_LIMIT", "1"))
    results = {}
    for category in ["ordinary", "no_fare", "hawashi"]:
        sampled = _sample_cases(cases[category], limit)
        results[category] = [
            (case, case_to_result(calculate_from_dict(case))) for case in sampled
        ]
    return results


def collect_failures_with_data(
    results: dict, predicate: Callable
) -> dict[str, list[dict]]:
    """Collect failing cases with their full data (case + result).

    Returns:
        Dict of category -> list of {"index": int, "case": dict, "result": dict}
    """
    failures = {}
    for category in ["ordinary", "no_fare", "hawashi"]:
        category_failures = []
        for i, (case, result) in enumerate(results[category]):
            if predicate(result):
                category_failures.append(
                    {
                        "index": i,
                        "case": case,
                        "result": result_to_dict(result),
                    }
                )
        if category_failures:
            failures[category] = category_failures
    return failures


def save_failures_to_disk(
    failures: dict, test_name: str, timestamp: str | None = None
) -> Path | None:
    """Save failures to JSON file for analysis in Jupyter.

    Args:
        failures: Dict of category -> list of {"index", "case", "result"}
        test_name: Name of the test for filename
        timestamp: Optional timestamp string

    Returns:
        Path to saved file, or None if no failures
    """
    if not failures:
        return None

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = output_dir / f"failures_{test_name}_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(failures, f, indent=2)

    return output_file


def collect_failing_indices(
    results: dict, category: str, predicate: Callable
) -> list[int]:
    """Collect indices where predicate(result) returns True."""
    return [i for i, (_, r) in enumerate(results[category]) if predicate(r)]


def run_all_tests_and_collect_failures(results: dict) -> dict:
    """Run all monte carlo tests and collect failing indices."""
    all_failures = {}

    tests = [
        ("test_total_always_one", lambda r: abs(r.total - 1.0) >= 1e-9),
        ("test_status_is_complete", lambda r: r.status != "Complete"),
    ]

    for test_name, predicate in tests:
        test_failures = {}
        for category in ["ordinary", "no_fare", "hawashi"]:
            failures = collect_failing_indices(results, category, predicate)
            if failures:
                test_failures[category] = failures

        if test_failures:
            all_failures[test_name] = test_failures

    return all_failures


def run_all_tests_and_collect_failure_data(results: dict) -> dict:
    """Run all tests and collect full failure data (case + result).

    Returns:
        Dict of test_name -> {category -> [{"index", "case", "result"}, ...]}
    """
    all_failures = {}

    tests = [
        ("total_not_one", lambda r: abs(r.total - 1.0) >= 1e-9),
        ("status_not_complete", lambda r: r.status != "Complete"),
    ]

    for test_name, predicate in tests:
        failures = collect_failures_with_data(results, predicate)
        if failures:
            all_failures[test_name] = failures

    return all_failures


_results_cache: dict | None = None


def get_results() -> dict:
    """Get cached results, computing if necessary."""
    global _results_cache
    if _results_cache is None:
        _results_cache = compute_all_results()
    return _results_cache


def run_test_and_collect_failures(
    test_name: str, results: dict, predicate: Callable, description: str
) -> dict:
    """Run a test across all categories and collect failing indices.

    Args:
        test_name: Name of the test (for error messages)
        results: Dict of category -> list of (case, result) tuples
        predicate: Function(result) -> bool, returns True if test fails
        description: Description of what the test checks (for error message)

    Returns:
        Dict of category -> list of failing indices

    Raises:
        AssertionError: If any failures found, with formatted error message
    """
    failures_with_data = collect_failures_with_data(results, predicate)

    if failures_with_data:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_failures_to_disk(failures_with_data, test_name, timestamp)

    all_failures = {}
    for category in ["ordinary", "no_fare", "hawashi"]:
        failures = collect_failing_indices(results, category, predicate)
        if failures:
            all_failures[category] = failures

    if all_failures:
        error_parts = []
        for cat, indices in all_failures.items():
            error_parts.append(f"{cat}: indices {indices[:10]}...")
        raise AssertionError(f"{test_name}: {'; '.join(error_parts)}")

    return all_failures
