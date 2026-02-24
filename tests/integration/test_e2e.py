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
"""End-to-end tests for SunnaAssets integration.

These tests run complete scenarios through the farady module
to verify real-world inheritance calculations work correctly.
"""

import pytest
from farady import calculate_from_dict, calculate_inheritance


class TestBasicScenarios:
    """Basic inheritance scenarios that must work in production."""

    def test_son_daughter_wife(self) -> None:
        """Standard case: son, daughter, wife."""
        result = calculate_inheritance(ibn=1, bint=1, zawja=True)

        assert result.status == "Complete"
        assert result.total == 1.0
        assert "zawja" in result.distribution
        assert "ibn" in result.distribution
        assert "bint" in result.distribution
        assert result.distribution["zawja"] == 0.125

    def test_two_sons_wife(self) -> None:
        """Two sons, wife - sons share equally as asib."""
        result = calculate_inheritance(ibn=2, zawja=True)

        assert result.status == "Complete"
        assert result.distribution["zawja"] == 0.125
        assert result.distribution["ibn"] == 0.875

    def test_daughters_only(self) -> None:
        """Two daughters with no other heirs."""
        result = calculate_inheritance(bint=2)

        assert result.status == "Complete"
        assert result.distribution["bint"] == 1.0

    def test_parents_with_children(self) -> None:
        """Father and mother with children."""
        result = calculate_inheritance(ibn=1, ab=1, umm=1)

        assert result.status == "Complete"
        assert result.distribution["ab"] == 1 / 6
        assert result.distribution["umm"] == 1 / 6
        assert result.distribution["ibn"] == 2 / 3


class TestAwlScenarios:
    """Awl cases where shares exceed 1."""

    def test_two_daughters_wife_awl(self) -> None:
        """Awl case: shares exceed 1."""
        result = calculate_inheritance(bint=2, zawja=True)

        assert result.status == "Complete"
        assert result.distribution["bint"] > 0
        assert result.distribution["zawja"] > 0


class TestRaddScenarios:
    """Radd cases where there's leftover after fixed shares."""

    def test_single_daughter_radd(self) -> None:
        """Single daughter gets radd."""
        result = calculate_inheritance(bint=1)

        assert result.status == "Complete"
        assert result.distribution["bint"] == 1.0


class TestComplexScenarios:
    """Complex multi-heir scenarios."""

    def test_full_family(self) -> None:
        """Complex case with multiple heir types."""
        result = calculate_inheritance(
            ibn=2,
            bint=1,
            umm=1,
            ab=1,
            zawja=True,
        )

        assert result.status == "Complete"
        assert abs(result.total - 1.0) < 0.0001

        assert "zawja" in result.distribution
        assert "umm" in result.distribution
        assert "ibn" in result.distribution
        assert "bint" in result.distribution

        assert result.distribution["zawja"] == 1 / 8
        assert result.distribution["umm"] == 1 / 6

    def test_siblings_case(self) -> None:
        """Full siblings with spouse."""
        result = calculate_inheritance(
            shaqiq=1,
            shaqiqa=2,
            zawj=True,
        )

        assert result.status == "Complete"
        assert "zawj" in result.distribution


class TestEdgeCases:
    """Edge cases that should be handled gracefully."""

    def test_no_heirs(self) -> None:
        """No valid heirs should return failed status."""
        result = calculate_inheritance()

        assert result.status == "Failed"

    def test_grandchildren_with_children(self) -> None:
        """Grandchildren blocked by children."""
        result = calculate_inheritance(ibn=1, iibn=2)

        assert result.status == "Complete"
        assert "ibn" in result.distribution
        assert "iibn" not in result.distribution


class TestFormInputSimulation:
    """Simulate form input from web applications."""

    def test_string_numbers(self) -> None:
        """Form input with string numbers."""
        result = calculate_from_dict(
            {
                "ibn": "2",
                "bint": "1",
                "zawja": "true",
            }
        )

        assert result.status == "Complete"
        assert result.distribution["zawja"] == 0.125

    def test_mixed_types(self) -> None:
        """Form input with mixed types."""
        result = calculate_from_dict(
            {
                "ibn": 1,
                "bint": "2",
                "umm": True,
                "zawja": "yes",
            }
        )

        assert result.status == "Complete"
        assert "umm" in result.distribution
        assert "zawja" in result.distribution

    def test_empty_strings_ignored(self) -> None:
        """Empty strings should be ignored."""
        result = calculate_from_dict(
            {
                "ibn": "1",
                "bint": "",
                "zawja": "true",
            }
        )

        assert result.status == "Complete"
        assert "bint" not in result.distribution
