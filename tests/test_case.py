# Copyright (C) 2018-2026  Adam Ahmed
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
Basic tests for calculation steps.
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


def test_lizakari1():
    case = calculate_from_dict({"ibn": "1", "bint": "1"})
    assert case.ibn.get("shares") == 2 * case.bint.get("shares")


def test_lizakari2():
    case = calculate_from_dict({"iibn": "1", "bibn": "1"})
    assert case.iibn.get("shares") == 2 * case.bibn.get("shares")


def test_lizakari3():
    case = calculate_from_dict({"iiibn": "1", "biibn": "1"})
    assert case.iiibn.get("shares") == 2 * case.biibn.get("shares")


def test_lizakari4():
    case = calculate_from_dict({"shaqiq": "1", "shaqiqa": "1"})
    assert case.shaqiq.get("shares") == 2 * case.shaqiqa.get("shares")


def test_lizakari5():
    case = calculate_from_dict({"aliab": "1", "uliab": "1"})
    assert case.aliab.get("shares") == 2 * case.uliab.get("shares")
