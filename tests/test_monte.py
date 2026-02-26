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
"""Simplified Monte Carlo tests for inheritance calculations.

These tests verify that all calculations produce valid results
across a large number of randomly generated test cases.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import numpy as np

# Add the src directory to the path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from farady import calculate_from_dict
from farady.pipelines import _build_distribution

# Categories for test cases
CATEGORIES = ("ordinary", "no_fare", "hawashi")


def load_test_cases():
    """Load test cases from the test_cases.npz file."""
    data_path = Path(__file__).parent / "data" / "test_cases.npz"
    if not data_path.exists():
        raise FileNotFoundError(f"Test data not found at {data_path}")

    data = np.load(data_path, allow_pickle=True)
    return {cat: list(data[cat]) for cat in CATEGORIES}


def case_to_result(case_dict):
    """Run calculation on a case and extract key results."""
    case = calculate_from_dict(case_dict)

    # Extract heir shares
    numerators = {
        name: int(heir.get("shares", 0))
        for name, heir in zip(case._all_heir_names, case._all_heirs)
        if heir.get("shares")
    }

    # Build distribution
    distribution = _build_distribution(case)

    # Extract heir shares
    numerators = {
        name: int(heir.get("shares", 0))
        for name, heir in zip(case._all_heir_names, case._all_heirs)
        if heir.get("shares")
    }

    return {
        "original_case": case_dict,
        "case": case,
        "distribution": distribution,
        "ending": case.ending,
        "asib": case.asib,
        "total": case.total,
        "status": case.status,
        "total_shares": case.total_shares,
        "raas": case.raas,
        "numerators": numerators,
    }


def collect_all_results(limit=None):
    cases = load_test_cases()

    # Apply limit if specified
    if limit is None:
        limit = int(os.environ.get("LIMIT", "100000"))

    results = {}
    for cat in CATEGORIES:
        cat_cases = cases[cat][:limit] if limit > 0 else cases[cat]
        results[cat] = [(c, case_to_result(c)) for c in cat_cases]

    return results


def save_failures(failures, test_name):
    if not any(failures.values()):
        return None

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"failures_{test_name}_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(failures, f, indent=2, default=str)

    return output_file


def collect_failures(results, predicate):
    """Collect test cases that fail the given predicate."""
    return {
        cat: [
            {"index": i, "case": c, "result": r}
            for i, (c, r) in enumerate(results[cat])
            if predicate(r)
        ]
        for cat in CATEGORIES
    }


# Load results once for all tests
_TEST_RESULTS = None


def get_test_results():
    """Get cached test results."""
    global _TEST_RESULTS
    if _TEST_RESULTS is None:
        _TEST_RESULTS = collect_all_results()
    return _TEST_RESULTS


def test_total_always_one():
    results = get_test_results()
    failures = collect_failures(
        results, lambda r: r["status"] == "Complete" and round(r["total"], 3) != 1.0
    )

    # Save failures for analysis
    save_failures(failures, "test_total_always_one")

    # Assert no failures
    failure_counts = {cat: len(failures[cat]) for cat in CATEGORIES}
    if any(count > 0 for count in failure_counts.values()):
        failure_details = ", ".join(
            f"{cat}: {count}" for cat, count in failure_counts.items() if count > 0
        )
        raise AssertionError(f"Total != 1.0 failures: {failure_details}")


def test_ibn_has_share_when_present():
    """When ibn is present, it should always have a share."""
    results = get_test_results()

    failures = collect_failures(
        results,
        lambda r: (
            r["original_case"].get("ibn", 0) > 0
            and r["distribution"].get("ibn", 0) == 0
        ),
    )

    save_failures(failures, "test_ibn_has_share_when_present")

    # Assert no failures
    failure_counts = {cat: len(failures[cat]) for cat in CATEGORIES}
    if any(count > 0 for count in failure_counts.values()):
        failure_details = ", ".join(
            f"{cat}: {count}" for cat, count in failure_counts.items() if count > 0
        )
        raise AssertionError(f"Ibn present but no share failures: {failure_details}")


def test_zawj_or_zawja_not_both():
    """A case should not have both zawj and zawja present."""
    results = get_test_results()

    failures = collect_failures(
        results,
        lambda r: (
            r["original_case"].get("zawj", 0) > 0
            and r["original_case"].get("zawja", 0) > 0
        ),
    )

    # Save failures for analysis
    save_failures(failures, "test_zawj_or_zawja_not_both")

    # Assert no failures
    failure_counts = {cat: len(failures[cat]) for cat in CATEGORIES}
    if any(count > 0 for count in failure_counts.values()):
        failure_details = ", ".join(
            f"{cat}: {count}" for cat, count in failure_counts.items() if count > 0
        )
        raise AssertionError(f"Both zawj and zawja present: {failure_details}")


def test_positive_shares_only():
    """All shares should be positive when present."""
    results = get_test_results()

    failures = collect_failures(
        results, lambda r: any(share < 0 for share in r["numerators"].values())
    )

    # Save failures for analysis
    save_failures(failures, "test_positive_shares_only")

    # Assert no failures
    failure_counts = {cat: len(failures[cat]) for cat in CATEGORIES}
    if any(count > 0 for count in failure_counts.values()):
        failure_details = ", ".join(
            f"{cat}: {count}" for cat, count in failure_counts.items() if count > 0
        )
        raise AssertionError(f"Negative shares found: {failure_details}")


def test_daughters_always_inherit():
    """When bint is present, always gets at least one share."""
    results = get_test_results()

    failures = collect_failures(
        results,
        lambda r: (
            r["original_case"].get("bint", 0) > 0
            and r["distribution"].get("bint", 0) == 0
        ),
    )

    # Save failures for analysis
    save_failures(failures, "test_daughters_always_inherit")

    # Assert no failures
    failure_counts = {cat: len(failures[cat]) for cat in CATEGORIES}
    if any(count > 0 for count in failure_counts.values()):
        failure_details = ", ".join(
            f"{cat}: {count}" for cat, count in failure_counts.items() if count > 0
        )
        raise AssertionError(
            f"Daughter present but no share failures: {failure_details}"
        )
