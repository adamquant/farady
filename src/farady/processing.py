# Copyright (C) 2018-2026  Adam Ahmed

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

from __future__ import annotations

# Type alias (compatible with older Python versions)
HeirKey = str

PRETTY_NAMES: dict[HeirKey, str] = {
    "bint": "Daughter(s)",
    "ibn": "Son(s)",
    "bibn": "Granddaughter(s)",
    "iibn": "Grandson(s)",
    "biibn": "Great-granddaughter(s)",
    "iiibn": "Great-grandson(s)",
    "umm": "Mother",
    "jadda": "Grandmother(s)",
    "ab": "Father",
    "jadd": "Grandfather (nearest in relation)",
    "lium": "Maternal Half-sibling(s)",
    "shaqiqa": "Full Sister(s)",
    "shaqiq": "Full Brother(s)",
    "uliab": "Paternal Half-sister(s)",
    "aliab": "Paternal Half-brother(s)",
    "ibnamm_sh": "Full Nephew",
    "ibnamm_liab": "Half Nephew",
    "amm": "Uncle",
    "zawj": "Husband",
    "zawja": "Wife",
    "all_full_siblings_maternal_half": "All full siblings and maternal half siblings",
}

HEIR_FIELDS = {
    "ibn",
    "bint",
    "iibn",
    "bibn",
    "iiibn",
    "biibn",
    "umm",
    "jadda",
    "ab",
    "jadd",
    "lium",
    "shaqiqa",
    "shaqiq",
    "uliab",
    "aliab",
    "ibnamm_sh",
    "ibnamm_liab",
    "amm",
    "zawj",
    "zawja",
}

BOOLEAN_HEIRS = {"zawj", "zawja"}

COUNT_HEIRS = HEIR_FIELDS - BOOLEAN_HEIRS


def load_csv_cases(csv_path: str) -> list:
    """Load inheritance cases from a CSV file."""
    import csv
    from farady.classes import Case

    cases = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case = Case.from_dict(row)
            cases.append(case)

    return cases


def process_csv_results(csv_path: str) -> list:
    """Load CSV and calculate results for each case."""
    import csv
    from farady.pipelines import calculate

    results = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            from farady.classes import Case

            case = Case.from_dict(row)
            result = calculate(case)
            results.append({"case": case, "result": result, "row_data": row})

    return results
