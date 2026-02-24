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
        lambda r: round(r["total"], 2) != 1.0,
        "total != 1.0",
    )


def test_status_is_complete():
    """All calculations should complete successfully."""
    results = get_results()
    run_test_and_collect_failures(
        "test_status_is_complete",
        results,
        lambda r: r["status"] != "Complete",
        "status != Complete",
    )
