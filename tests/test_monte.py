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

from farady import calculate_from_dict, _build_distribution


def load_test_cases():
    """Load test cases from the test_cases_v2.npz file."""
    data_path = Path(__file__).parent / "data" / "test_cases_v2.npz"
    if not data_path.exists():
        raise FileNotFoundError(f"Test data not found at {data_path}")

    data = np.load(data_path, allow_pickle=True)
    # Return a single array of cases instead of categorized dict
    return list(data["ordinary"])


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

    # Extract heir shares (already done above, removing duplicate)
    # Create a detailed heir breakdown
    heir_details = {}
    for name, heir in zip(case._all_heir_names, case._all_heirs):
        if heir.get("count", 0) > 0 or heir.get("shares", 0) > 0:
            heir_details[name] = {
                "count": heir.get("count", 0),
                "shares": heir.get("shares", 0),
                "fard": str(heir.get("fard", "")) if heir.get("fard") else None,
                "asib": heir.get("asib", False),
            }

    # Create a more detailed string representation of the Case object
    case_repr = f"Case("
    heir_info = []
    for name, heir in zip(case._all_heir_names, case._all_heirs):
        if heir.get("count", 0) > 0 or heir.get("shares", 0) > 0:
            heir_str = f"{name}={{'count': {heir.get('count', 0)}"
            if heir.get("fard") is not None:
                heir_str += f", 'fard': {heir['fard']}"
            if heir.get("shares") is not None:
                heir_str += f", 'shares': {heir['shares']}"
            if heir.get("asib"):
                heir_str += f", 'asib': {heir['asib']}"
            heir_str += "}"
            heir_info.append(heir_str)

    attrs = []
    if case.ending:
        attrs.append(f"ending='{case.ending}'")
    if case.asib:
        attrs.append(f"asib='{case.asib}'")
    if case.status:
        attrs.append(f"status='{case.status}'")
    if case.heads is not None:
        attrs.append(f"heads={case.heads}")
    if case._raas_override is not None:
        attrs.append(f"_raas_override={case._raas_override}")
    if case.total_shares_radd:
        attrs.append(f"total_shares_radd={case.total_shares_radd}")

    all_info = heir_info + attrs
    case_repr += ", ".join(all_info) + ")" if all_info else ")"

    return {
        "original_case": case_dict,
        "case_str": case_repr,  # String representation of the full Case object
        "distribution": distribution,
        "ending": case.ending,
        "asib": case.asib,
        "total": case.total,
        "status": case.status,
        "total_shares": case.total_shares,
        "raas": case.raas,
        "numerators": numerators,
        "heir_details": heir_details,
        "baqi": case.baqi,
    }


def collect_all_results(limit=None):
    cases = load_test_cases()

    # Apply limit if specified
    if limit is None:
        limit = int(os.environ.get("LIMIT", "257000"))

    # Apply limit to cases
    cases = cases[:limit] if limit > 0 else cases
    results = [(c, case_to_result(c)) for c in cases]

    return results


def save_failures(failures, test_name):
    # Check if there are any failures (now a single list instead of dict)
    if isinstance(failures, dict):
        # Old format with categories
        if not any(failures.values()):
            return None
    else:
        # New format with single list
        if not failures:
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
    return [
        {"index": i, "case": c, "result": r}
        for i, (c, r) in enumerate(results)
        if predicate(r)
    ]


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
    failures_dict = {"ordinary": failures}
    save_failures(failures_dict, "test_total_always_one")

    # Assert no failures
    failure_count = len(failures)
    if failure_count > 0:
        raise AssertionError(f"Total != 1.0 failures: {failure_count}")


def test_ibn_has_share_when_present():
    """When ibn is present, it should always have a share."""
    results = get_test_results()

    failures = collect_failures(
        results,
        lambda r: (
            r["original_case"].get("ibn", 0) > 0  # Ibn is present
            and r["distribution"].get("ibn", 0) == 0  # But gets no share
            and r["ending"] == "taseeb"  # Only in taseeb cases
            and r["status"]
            in ["Complete", "Unknown"]  # Only flag if status is Complete or Unknown
        ),
    )

    failures_dict = {"ordinary": failures}
    save_failures(failures_dict, "test_ibn_has_share_when_present")

    # Assert no failures
    failure_count = len(failures)
    if failure_count > 0:
        raise AssertionError(f"Ibn present but no share failures: {failure_count}")


# def test_zawj_or_zawja_not_both():
#     """A case should not have both zawj and zawja present."""
#     results = get_test_results()

#     failures = collect_failures(
#         results,
#         lambda r: (
#             r["original_case"].get("zawj", 0) > 0
#             and r["original_case"].get("zawja", 0) > 0
#         ),
#     )

#     # Save failures for analysis
#     save_failures(failures, "test_zawj_or_zawja_not_both")

#     # Assert no failures
#     failure_count = len(failures)
#     if failure_count > 0:
#         raise AssertionError(f"Both zawj and zawja present: {failure_count}")


# def test_positive_shares_only():
#     """All shares should be positive when present."""
#     results = get_test_results()

#     failures = collect_failures(
#         results, lambda r: any(share < 0 for share in r["numerators"].values())
#     )

#     # Save failures for analysis
#     save_failures(failures, "test_positive_shares_only")

#     # Assert no failures
#     failure_count = len(failures)
#     if failure_count > 0:
#         raise AssertionError(f"Negative shares found: {failure_count}")


def test_unknown_status_should_fail():
    """Test that fails if any case has 'Unknown' status.

    This test will fail pytest if any case has 'Unknown' status, and will save
    all such cases to a failure file for analysis.
    """
    results = get_test_results()

    # Check for 'Unknown' status cases
    unknown_failures = [
        {"index": i, "case": c, "result": r}
        for i, (c, r) in enumerate(results)
        if r["status"] == "Unknown"
    ]

    # Wrap in dict for save_failures function
    unknown_failures_dict = {"ordinary": unknown_failures}

    # Save all 'Unknown' cases for analysis
    if len(unknown_failures) > 0:
        save_failures(unknown_failures_dict, "test_unknown_status_should_fail")
        print(f"Saved {len(unknown_failures)} 'Unknown' cases to failure file")

        # Fail the test - we don't want any 'Unknown' cases
        raise AssertionError(
            f"Found {len(unknown_failures)} cases with 'Unknown' status"
        )


def test_other_non_complete_cases():
    """Record all other non-complete cases (Failed, etc.).

    This test will not fail pytest, but will save all other non-complete cases
    to a failure file for analysis.
    """
    results = get_test_results()

    # Check for non-'Complete' and non-'Unknown' cases
    other_non_complete = [
        {"index": i, "case": c, "result": r}
        for i, (c, r) in enumerate(results)
        if r["status"] != "Complete" and r["status"] != "Unknown"
    ]

    # Also collect 'Unknown' cases for comprehensive logging (but don't fail)
    unknown_cases = [
        {"index": i, "case": c, "result": r}
        for i, (c, r) in enumerate(results)
        if r["status"] == "Unknown"
    ]

    # Combine all non-complete cases for logging
    all_non_complete = other_non_complete + unknown_cases

    # Wrap in dict for save_failures function
    all_non_complete_dict = {"ordinary": all_non_complete}

    # Save all non-complete cases for analysis (only if there are any)
    if len(all_non_complete) > 0:
        save_failures(all_non_complete_dict, "test_other_non_complete_cases")
        print(f"Saved {len(all_non_complete)} other non-complete cases to failure file")


def test_daughters_always_inherit():
    """When bint is present, should get at least one share if status is Complete or Unknown."""
    results = get_test_results()

    failures = collect_failures(
        results,
        lambda r: (
            r["original_case"].get("bint", 0) > 0  # Daughter is present
            and r["distribution"].get("bint", 0) == 0  # But gets no share
            and r["status"]
            in ["Complete", "Unknown"]  # Only flag if status is Complete or Unknown
        ),
    )

    # Save failures for analysis
    failures_dict = {"ordinary": failures}
    save_failures(failures_dict, "test_daughters_always_inherit")

    # Assert no failures
    failure_count = len(failures)
    if failure_count > 0:
        raise AssertionError(f"Daughter present but no share failures: {failure_count}")
