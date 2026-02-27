#!/usr/bin/env python
"""Analyze Monte Carlo test results.

This script loads test cases and runs analyses on them to identify patterns
and edge cases in the inheritance calculations.
"""

import json
import os
from collections import defaultdict
from pathlib import Path

import numpy as np

# Add the src directory to the path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from farady import calculate_from_dict, _build_distribution


def load_test_cases():
    """Load test cases from the test_cases.npz file."""
    data_path = Path(__file__).parent / "tests" / "data" / "test_cases.npz"
    if not data_path.exists():
        raise FileNotFoundError(f"Test data not found at {data_path}")

    data = np.load(data_path, allow_pickle=True)
    return list(data["ordinary"])


def case_to_result(case_dict):
    """Run calculation on a case and extract key results."""
    case = calculate_from_dict(case_dict)

    # Extract heir shares
    numerators = {
        name: int(heir.get("shares", 0))
        for name, heir in zip(case._all_heir_names, case._all_heirs)
        if heir.get("shares")
    }

    # Build distribution
    distribution = _build_distribution(case)

    # Calculate total from distribution
    total = (
        sum(item["fraction"] for item in distribution.values()) if distribution else 0
    )

    return {
        "original_case": case_dict,
        "distribution": distribution,
        "ending": case.ending,
        "asib": case.asib,
        "total": total,
        "status": case.status,
        "raas": case.raas,
        "numerators": numerators,
    }


def analyze_totals(results):
    """Analyze distribution totals."""
    print("=== TOTAL ANALYSIS ===")

    totals = [r[1]["total"] for r in results]

    print(f"\nOrdinary cases:")
    print(f"  Count: {len(totals)}")
    print(f"  Min: {min(totals):.4f}")
    print(f"  Max: {max(totals):.4f}")
    print(f"  Mean: {np.mean(totals):.4f}")
    print(f"  Std: {np.std(totals):.4f}")

    # Count how many are exactly 1.0
    exact_ones = sum(1 for t in totals if round(t, 2) == 1.0)
    print(f"  Exactly 1.0: {exact_ones} ({exact_ones / len(totals) * 100:.1f}%)")

    # Count anomalies
    anomalies = [
        (i, r[0], t)
        for i, (r, t) in enumerate(zip(results, totals))
        if round(t, 2) != 1.0
    ]
    print(f"  Anomalies: {len(anomalies)} ({len(anomalies) / len(totals) * 100:.1f}%)")

    if anomalies:
        print("  Sample anomalies:")
        for i, (idx, case, total) in enumerate(anomalies[:5]):
            print(f"    {i + 1}. Case {idx}: total={total:.4f}, case={case}")


def analyze_ibn_shares(results):
    """Analyze ibn share allocation."""
    print("\n=== IBN SHARE ANALYSIS ===")

    # Cases where ibn is present
    ibn_cases = [(i, r) for i, r in enumerate(results) if r[0].get("ibn", 0) > 0]
    # Cases where ibn is present but gets no share
    ibn_no_share = [
        (i, r) for i, r in ibn_cases if r[1]["numerators"].get("ibn", 0) == 0
    ]

    print(f"\nOrdinary cases:")
    print(f"  Cases with ibn: {len(ibn_cases)}")
    print(f"  Cases with ibn but no share: {len(ibn_no_share)}")
    if ibn_cases:
        print(
            f"  Percentage with no share: {len(ibn_no_share) / len(ibn_cases) * 100:.1f}%"
        )

    if ibn_no_share:
        print("  Sample cases with ibn but no share:")
        for i, (idx, (case, result)) in enumerate(ibn_no_share[:5]):
            print(f"    {i + 1}. Case {idx}: {case[0]}")


def analyze_endings(results):
    """Analyze calculation endings."""
    print("\n=== ENDING ANALYSIS ===")

    endings = defaultdict(int)

    for _, result in results:
        ending = result["ending"] or "none"
        endings[ending] += 1

    print(f"\nOrdinary cases:")
    for ending, count in sorted(endings.items()):
        print(f"  {ending}: {count} ({count / len(results) * 100:.1f}%)")


def load_failure_cases(test_name):
    """Load failure cases from JSON files."""
    output_dir = Path(__file__).parent / "tests" / "output"
    if not output_dir.exists():
        return {}

    failure_files = list(output_dir.glob(f"failures_{test_name}_*.json"))
    if not failure_files:
        return {}

    # Get the most recent file
    latest_file = sorted(failure_files)[-1]

    with open(latest_file) as f:
        return json.load(f)


def analyze_failures():
    """Analyze failure cases from tests."""
    print("\n=== FAILURE ANALYSIS ===")

    failure_data = load_failure_cases("test_total_always_one")
    if not failure_data:
        print("No failure data found.")
        return

    failures = failure_data.get("ordinary", [])
    if failures:
        print(f"\nOrdinary failures in total test:")
        print(f"  Count: {len(failures)}")
        print("  Sample failures:")
        for i, failure in enumerate(failures[:5]):
            case = failure["case"]
            result = failure["result"]
            print(f"    {i + 1}. Total={result['total']:.4f}, case={case}")


def main():
    """Main analysis function."""
    print("Loading test cases...")
    cases = load_test_cases()

    # Limit for analysis (default 1000 like in tests)
    limit = int(os.environ.get("FARADY_MONTE_LIMIT", "1000"))

    print(f"Processing {limit} cases...")
    cat_cases = cases[:limit] if limit > 0 else []
    results = [(c, case_to_result(c)) for c in cat_cases]
    print(f"  Ordinary: {len(cat_cases)} cases processed")

    # Run analyses
    analyze_totals(results)
    analyze_ibn_shares(results)
    analyze_endings(results)
    analyze_failures()

    print("\n=== ANALYSIS COMPLETE ===")


if __name__ == "__main__":
    main()
