import numpy as np
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from farady import build_random_case
# CONFIG
SIMS = 500_000
SEED = 42
OUTPUT_DIR = Path(__file__).parent / 'test_data'
OUTPUT_FILE = OUTPUT_DIR / "test_cases.npz"
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
    # Generate
    print("  Generating ordinary cases...")
    ordinary = [build_random_case(rng=rng) for _ in range(SIMS)]
    print("  Generating no_fare cases...")
    no_fare = [build_random_case(focus='no_descendants', rng=rng) for _ in range(SIMS)]
    print("  Generating hawashi cases...")
    hawashi = [build_random_case(focus='hawashi', rng=rng) for _ in range(SIMS)]
    # Deduplicate
    print("Deduplicating...")
    ordinary = deduplicate_cases(ordinary)
    no_fare = deduplicate_cases(no_fare)
    hawashi = deduplicate_cases(hawashi)
    print(f"Unique cases:")
    print(f"  ordinary: {len(ordinary):,}")
    print(f"  no_fare:  {len(no_fare):,}")
    print(f"  hawashi:  {len(hawashi):,}")
    # Save
    print(f"Saving to {OUTPUT_FILE}...")
    np.savez_compressed(
        OUTPUT_FILE,
        ordinary=ordinary,
        no_fare=no_fare,
        hawashi=hawashi
    )
    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"Done! Size: {size_mb:.1f} MB")
if __name__ == "__main__":
    main()