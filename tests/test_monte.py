"""Monte carlo tests for inheritance calculations.

These tests verify that all calculations produce valid results
across a large number of randomly generated test cases.
"""

import pytest

from conftest import get_results, run_test_and_collect_failures


def test_total_always_one():
    """All inheritance distributions should sum to 1.0."""
    results = get_results()
    run_test_and_collect_failures(
        "test_total_always_one",
        results,
        lambda r: round(r.total, 2) == 1.0 - 1.0),
        "total != 1.0",
    )


def test_status_is_complete():
    """All calculations should complete successfully."""
    results = get_results()
    run_test_and_collect_failures(
        "test_status_is_complete",
        results,
        lambda r: r.status != "Complete",
        "status != Complete",
    )
