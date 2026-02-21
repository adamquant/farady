"""
Data-Driven Test Template for Farady

This file provides a template for running data-driven tests from CSV files.
Edit the test cases and assertions to suit your needs.

CSV Format:
    Each column should be a valid family member name.
    Boolean values can be: True, False, 1, 0, Yes, No

    You can also add custom columns for expected results/assertions.

Example CSV (tests/test_data.csv):
    ibn,bint,zawja,expected_wife_share,expected_son_share
    2,1,True,0.125,0.7
    1,0,False,0,1.0
"""

import pytest
from farady import (
    InheritanceCase,
    InheritanceCalculator,
    process_csv_results,
    PRETTY_NAMES,
)


# Path to your CSV file - change this to point to your test data
TEST_DATA_PATH = "tests/test_data.csv"


def load_test_cases():
    """Load test cases from CSV file."""
    try:
        return process_csv_results(TEST_DATA_PATH)
    except FileNotFoundError:
        pytest.skip(f"Test data file not found: {TEST_DATA_PATH}")


class TestInheritanceCalculations:
    """Data-driven tests for inheritance calculations."""

    @pytest.mark.parametrize(
        "test_case", load_test_cases(), ids=lambda x: str(x["row_data"])
    )
    def test_inheritance_distribution(self, test_case):
        """Test inheritance distribution against expected values from CSV.

        Edit this test to add your specific assertions.
        """
        row = test_case["row_data"]
        case = test_case["case"]
        result = test_case["result"]

        # === YOUR ASSERTIONS HERE ===

        # Example: Check wife share
        # expected_wife = float(row.get('expected_wife_share', 0))
        # actual_wife = result.distribution.get('zawja', 0)
        # assert abs(actual_wife - expected_wife) < 0.001, f"Wife share mismatch: expected {expected_wife}, got {actual_wife}"

        # Example: Check son share
        # expected_son = float(row.get('expected_son_share', 0))
        # actual_son = result.distribution.get('ibn', 0)
        # assert abs(actual_son - expected_son) < 0.001, f"Son share mismatch"

        # Example: Check status
        # expected_status = row.get('expected_status', 'Complete')
        # assert result.status == expected_status, f"Status mismatch: {result.status}"

        pass  # Replace with your assertions

    def test_manual_case_1(self):
        """Manual test: son + daughter + wife"""
        case = InheritanceCase(ibn=1, bint=1, zawja=True)
        calc = InheritanceCalculator()
        result = calc.calculate(case)

        # === YOUR ASSERTIONS HERE ===
        # Example:
        # assert result.status == 'Complete'
        # assert abs(result.distribution.get('zawja', 0) - 0.125) < 0.001

        pass

    def test_manual_case_2(self):
        """Manual test: father + mother + wife (umuriya)"""
        case = InheritanceCase(ab=1, umm=1, zawja=True)
        calc = InheritanceCalculator()
        result = calc.calculate(case)

        # === YOUR ASSERTIONS HERE ===
        pass


# Helper functions you can use in your tests


def get_share(result, member_name):
    """Get share for a member by name or pretty name."""
    if member_name in result.distribution:
        return result.distribution[member_name]
    # Try pretty name
    for key, pretty in PRETTY_NAMES.items():
        if pretty == member_name and key in result.distribution:
            return result.distribution[key]
    return 0


def assert_share(result, member, expected, tolerance=0.001):
    """Assert that a member's share matches expected value."""
    actual = get_share(result, member)
    assert abs(actual - expected) < tolerance, (
        f"{member}: expected {expected}, got {actual}"
    )


def assert_total(result, expected=1.0, tolerance=0.001):
    """Assert that total distribution equals expected (default 1.0)."""
    assert abs(result.total - expected) < tolerance, (
        f"Total: expected {expected}, got {result.total}"
    )


def assert_status(result, expected):
    """Assert calculation status."""
    assert result.status == expected, (
        f"Status: expected {expected}, got {result.status}"
    )


# Run with: pytest tests/test_ddt.py -v
# Run specific test: pytest tests/test_ddt.py::TestInheritanceCalculations::test_manual_case_1 -v
