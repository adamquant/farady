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
"""Generate test data for monte carlo tests.

Run this script to generate test cases:
    poetry run python scripts/generate_test_data.py

Output:
    tests/data/test_cases.npz
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Heir categories
DESCENDANTS = ["ibn", "bint", "iibn", "bibn", "iiibn", "biibn"]
ASCENDANTS = ["umm", "jadda", "ab", "jadd"]
SIBLINGS = ["lium", "shaqiqa", "shaqiq", "uliab", "aliab"]
OTHER_RELATIVES = ["ibnamm_sh", "ibnamm_liab", "amm"]
SPOUSES = ["zawj", "zawja"]

ALL_HEIRS = DESCENDANTS + ASCENDANTS + SIBLINGS + OTHER_RELATIVES + SPOUSES

# Boolean heirs (can only be 0 or 1)
BOOLEAN_HEIRS = {"zawj", "zawja"}

# Maximum counts for different heir types
MAX_COUNTS = {
    "ibn": 5,
    "bint": 5,
    "iibn": 5,
    "bibn": 5,
    "iiibn": 5,
    "biibn": 5,
    "umm": 1,
    "jadda": 2,
    "ab": 1,
    "jadd": 1,
    "lium": 5,
    "shaqiqa": 5,
    "shaqiq": 5,
    "uliab": 5,
    "aliab": 5,
    "ibnamm_sh": 5,
    "ibnamm_liab": 5,
    "amm": 3,
    "zawj": 1,
    "zawja": 4,  # Up to 4 wives
}

SIMS = 500_000
SEED = 42
OUTPUT_FILE = Path(__file__).parent.parent / "tests" / "data" / "test_cases.npz"


def build_random_case(rng=None, focus=None):
    """Build a random inheritance case.

    Args:
        rng: Random number generator
        focus: Focus area ('no_descendants', 'hawashi', or None)
    """
    if rng is None:
        rng = np.random.default_rng()

    case = {}

    # Determine which heirs to include based on focus
    if focus == "no_descendants":
        # Exclude descendants
        heirs_to_consider = ASCENDANTS + SIBLINGS + OTHER_RELATIVES + SPOUSES
    elif focus == "hawashi":
        # Focus on siblings and other relatives
        heirs_to_consider = SIBLINGS + OTHER_RELATIVES + SPOUSES
    else:
        # Include all heirs
        heirs_to_consider = ALL_HEIRS

    # Randomly select which heirs to include (at least one)
    num_heirs = rng.integers(1, min(len(heirs_to_consider) + 1, 8))  # At least 1, max 7
    selected_heirs = rng.choice(heirs_to_consider, size=num_heirs, replace=False)

    # Assign counts to selected heirs
    for heir in selected_heirs:
        if heir in BOOLEAN_HEIRS:
            # Boolean heirs are just present or not
            case[heir] = True
        else:
            # Count heirs get a random count
            max_count = MAX_COUNTS.get(heir, 5)
            count = rng.integers(1, max_count + 1)  # At least 1
            case[heir] = count

    return case


def filter_valid_cases(cases):
    """Filter out invalid cases (empty dicts or cases with no people).

    A valid case must have at least one heir with a count > 0.
    """
    valid_cases = []
    for case in cases:
        # Check if case is not empty
        if not case:
            continue

        # Check if at least one heir has a valid count
        has_valid_heir = False
        for heir, value in case.items():
            if heir in BOOLEAN_HEIRS:
                if value:  # True means present
                    has_valid_heir = True
                    break
            else:
                if isinstance(value, (int, float)) and value > 0:
                    has_valid_heir = True
                    break

        if has_valid_heir:
            valid_cases.append(case)

    return valid_cases


def deduplicate_cases(cases):
    """Remove duplicate dicts from list of test cases."""
    seen = set()
    unique = []
    for case in cases:
        key = tuple(sorted(case.items()))
        if key not in seen:
            seen.add(key)
            unique.append(case)
    return unique


def main():
    rng = np.random.default_rng(SEED)
    print(f"Generating {SIMS:,} cases per category with seed={SEED}...")
    print("  Generating ordinary cases...")
    ordinary = [build_random_case(rng=rng) for _ in range(SIMS)]
    ordinary = filter_valid_cases(ordinary)  # Filter out empty/invalid cases

    print("  Generating no_fare cases...")
    no_fare = [build_random_case(focus="no_descendants", rng=rng) for _ in range(SIMS)]
    no_fare = filter_valid_cases(no_fare)  # Filter out empty/invalid cases

    print("  Generating hawashi cases...")
    hawashi = [build_random_case(focus="hawashi", rng=rng) for _ in range(SIMS)]
    hawashi = filter_valid_cases(hawashi)  # Filter out empty/invalid cases

    print("Deduplicating...")
    ordinary = deduplicate_cases(ordinary)
    no_fare = deduplicate_cases(no_fare)
    hawashi = deduplicate_cases(hawashi)

    print(f"Unique cases:")
    print(f"  ordinary: {len(ordinary):,}")
    print(f"  no_fare:  {len(no_fare):,}")
    print(f"  hawashi:  {len(hawashi):,}")
    print(f"Saving to {OUTPUT_FILE}...")
    np.savez_compressed(
        OUTPUT_FILE, ordinary=ordinary, no_fare=no_fare, hawashi=hawashi
    )
    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"Done! Size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
