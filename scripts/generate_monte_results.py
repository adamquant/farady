#!/usr/bin/env python
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
"""Run monte carlo tests and save only failures to disk.

Run this script to generate failure reports:
    poetry run python scripts/generate_monte_results.py

To customize the number of test cases (default is 1000 for faster iteration):
    FARADY_MONTE_LIMIT=5000 poetry run python scripts/generate_monte_results.py

Output (only if failures exist):
    tests/output/failures_{test_name}_{timestamp}.json

Each JSON file contains:
    {
        "category_name": [
            {
                "index": 123,
                "case": {...original case dict...},
                "result": {...result dict with distribution, total, etc...}
            },
            ...
        ]
    }

Load in Jupyter:
    import json
    with open("tests/output/failures_total_not_one_20260222.json") as f:
        failures = json.load(f)
    # failures["ordinary"][0]["case"] -> the input case
    # failures["ordinary"][0]["result"] -> the calculation result
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))
from conftest import (
    compute_all_results,
    run_all_tests_and_collect_failure_data,
    save_failures_to_disk,
)


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Timestamp: {timestamp}")
    print()

    print("Computing all results...")
    results = compute_all_results()
    total_cases = sum(len(v) for v in results.values())
    print(f"  Total cases: {total_cases:,}")

    print("\nRunning tests and collecting failures...")
    all_failures = run_all_tests_and_collect_failure_data(results)

    if not all_failures:
        print("\nAll tests passed! No failures to save.")
        return

    print(f"\nFound failures in {len(all_failures)} test(s):")
    for test_name, failures in all_failures.items():
        total = sum(len(v) for v in failures.values())
        print(f"  {test_name}: {total} failures")
        for cat, items in failures.items():
            print(f"    {cat}: {len(items)} failures")

        path = save_failures_to_disk(failures, test_name, timestamp)
        if path:
            print(f"    Saved to: {path}")


if __name__ == "__main__":
    main()
