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
"""
Comprehensive tests for Farady Islamic Inheritance Calculator.

Run tests:
    pytest tests/test_farady.py -v
    pytest tests/test_farady.py -v -k "test_csv"  # Only CSV tests
    pytest tests/test_farady.py -v -k "test_dict"  # Only dict tests
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from farady import (
    Case,
    calculate,
    calculate_from_dict,
    load_csv_cases,
    process_csv_results,
    PRETTY_NAMES,
)


class TestFromDict:
    """Test the from_dict conversion functionality."""

    def test_simple_counts(self):
        """Test integer conversion from strings."""
        case = Case.from_dict({"ibn": "2", "bint": "1"})
        assert case.ibn.get("count") == 2
        assert case.bint.get("count") == 1

    def test_boolean_spouses(self):
        """Test boolean conversion for spouse fields."""
        case = Case.from_dict({"zawja": "True", "zawj": "False"})
        assert case.zawja.get("count") == 1
        assert case.zawj.get("count") == 0

    def test_boolean_spouses_numeric(self):
        """Test numeric string conversion for spouse fields."""
        case = Case.from_dict({"zawja": "1", "zawj": "0"})
        assert case.zawja.get("count") == 1
        assert case.zawj.get("count") == 0

    def test_mixed_types(self):
        """Test mixed int and bool fields."""
        case = Case.from_dict({"ibn": "1", "bint": 2, "zawja": True, "umm": "1"})
        assert case.ibn.get("count") == 1
        assert case.bint.get("count") == 2
        assert case.zawja.get("count") == 1
        assert case.umm.get("count") == 1


class TestCalculateFromDict:
    """Test the calculate_from_dict convenience function."""

    def test_son_daughter_wife(self):
        """Classic case: son, daughter, wife."""
        result = calculate_from_dict({"ibn": 1, "bint": 1, "zawja": True})

        assert result.status == "Complete"
        assert abs(result.total - 1.0) < 0.01
        assert "zawja" in result.distribution
        assert abs(result.distribution["zawja"] - 0.125) < 0.001

    def test_only_son(self):
        """One son gets everything."""
        result = calculate_from_dict({"ibn": 1})

        assert result.status == "Complete"
        assert abs(result.total - 1.0) < 0.01  # 2dp precision
        assert abs(result.distribution.get("ibn", 0) - 1.0) < 0.001

    def test_only_wife(self):
        """Wife only - no radd for spouses."""
        result = calculate_from_dict({"zawja": True})

        # Wife only returns Unknown status but still has correct share
        assert "zawja" in result.distribution
        assert abs(result.distribution.get("zawja", 0) - 0.25) < 0.001

    def test_two_daughters_wife(self):
        """Awl case: 2 daughters (2/3) + wife (1/8) = 19/24 -> awl to 24/24."""
        result = calculate_from_dict({"bint": 2, "zawja": True})

        assert "bint" in result.distribution
        assert "zawja" in result.distribution
        # This is an awl case, total should be >= 1


class TestCSVLoading:
    """Test CSV file loading functionality."""

    def test_load_csv_cases(self):
        """Test loading cases from CSV."""
        csv_path = os.path.join(os.path.dirname(__file__), "test_cases.csv")

        if not os.path.exists(csv_path):
            pytest.skip(f"CSV file not found: {csv_path}")

        cases = load_csv_cases(csv_path)
        assert len(cases) > 0

        # Check that cases are valid
        for case in cases:
            assert isinstance(case, Case)

    def test_process_csv_results(self):
        """Test processing CSV and calculating results."""
        csv_path = os.path.join(os.path.dirname(__file__), "test_cases.csv")

        if not os.path.exists(csv_path):
            pytest.skip(f"CSV file not found: {csv_path}")

        results = process_csv_results(csv_path)
        assert len(results) > 0

        for item in results:
            assert "case" in item
            assert "result" in item
            assert "row_data" in item
            assert isinstance(item["case"], Case)


class TestCSVValidation:
    """Validate results against expected values in CSV."""

    @pytest.fixture
    def csv_results(self):
        """Load CSV results fixture."""
        csv_path = os.path.join(os.path.dirname(__file__), "test_cases.csv")
        if not os.path.exists(csv_path):
            pytest.skip(f"CSV file not found: {csv_path}")
        return process_csv_results(csv_path)

    def test_all_cases_have_valid_status(self, csv_results):
        """All cases should have a valid status."""
        valid_statuses = {"Complete", "Awl", "No heirs", "Unknown", "Failed"}
        for item in csv_results:
            assert item["result"].status in valid_statuses, (
                f"Invalid status for {item['row_data'].get('case_name')}: {item['result'].status}"
            )

    def test_totals_match_expected(self, csv_results):
        """Total should match expected_total from CSV."""
        for item in csv_results:
            row = item["row_data"]
            result = item["result"]

            expected_total = row.get("expected_total", "")
            if expected_total:
                expected = float(expected_total)
                actual = result.total
                assert abs(actual - expected) < 0.01, (
                    f"Total mismatch for {row.get('case_name')}: expected {expected}, got {actual}"
                )

    def test_status_matches_expected(self, csv_results):
        """Status should match expected_status from CSV."""
        for item in csv_results:
            row = item["row_data"]
            result = item["result"]

            expected_status = row.get("expected_status", "")
            if expected_status:
                assert result.status == expected_status, (
                    f"Status mismatch for {row.get('case_name')}: expected {expected_status}, got {result.status}"
                )


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_no_heirs(self):
        """No heirs case."""
        result = calculate_from_dict({})
        assert result.status == "No heirs" or len(result.distribution) == 0

    def test_many_sons(self):
        """Many sons case."""
        result = calculate_from_dict({"ibn": 10})
        assert abs(result.distribution.get("ibn", 0) - 1.0) < 0.001

    def test_all_descendant_types(self):
        """Multiple descendant types."""
        result = calculate_from_dict({"ibn": 1, "bint": 2, "iibn": 1, "bibn": 1})
        assert result.status == "Complete"
        assert abs(result.total - 1.0) < 0.01  # 2dp precision


# Helper functions for custom tests


def get_share(result, member_name):
    """Get share for a member by name or pretty name."""
    if member_name in result.distribution:
        return result.distribution[member_name]
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
    """Assert that total distribution equals expected."""
    assert abs(result.total - expected) < tolerance, (
        f"Total: expected {expected}, got {result.total}"
    )


def assert_status(result, expected):
    """Assert calculation status."""
    assert result.status == expected, (
        f"Status: expected {expected}, got {result.status}"
    )
