#!/usr/bin/env python
"""Generate and save monte carlo test results.

Run this script to generate results and failing indices:
    poetry run python tests/save_monte_results.py

Output:
    tests/output/monte_results_YYYYMMDD_HHMMSS.json
    tests/output/failing_indices_YYYYMMDD_HHMMSS.json
"""

import sys
import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from farady import calculate_from_dict


def load_test_cases():
    """Load pre-generated test cases from disk."""
    data_path = Path(__file__).parent / "data" / "test_cases.npz"
    data = np.load(data_path, allow_pickle=True)
    return {
        "ordinary": list(data["ordinary"]),
        "no_fare": list(data["no_fare"]),
        "hawashi": list(data["hawashi"]),
    }


def result_to_dict(result):
    """Convert InheritanceResult to JSON-serializable dict."""
    return {
        "distribution": result.distribution,
        "ending": result.ending,
        "asib": result.asib,
        "total": result.total,
        "status": result.status,
        "denominator": result.denominator,
        "numerators": result.numerators,
    }


def compute_all_results():
    """Run calculations on all test cases."""
    print("Loading test cases...")
    cases = load_test_cases()

    results = {}
    for category in ["ordinary", "no_fare", "hawashi"]:
        print(f"  Computing {category}...")
        results[category] = [
            (case, calculate_from_dict(case)) for case in cases[category]
        ]

    return results


def save_results_to_disk(results, timestamp):
    """Save results to output folder."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"monte_results_{timestamp}.json"

    print("Saving results...")
    output_data = {}
    for category, tuples in results.items():
        output_data[category] = [
            {"case": case, "result": result_to_dict(result)} for case, result in tuples
        ]

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    return output_file


def collect_failing_indices(results, category, predicate):
    """Collect indices where predicate(result) returns True."""
    return [i for i, (_, r) in enumerate(results[category]) if predicate(r)]


def run_all_tests_and_collect_failures(results):
    """Run all monte carlo tests and collect failing indices."""
    all_failures = {}

    tests = [
        ("test_total_always_one", lambda r: abs(r.total - 1.0) >= 1e-9),
        ("test_status_is_complete", lambda r: r.status != "Complete"),
    ]

    print("Running tests and collecting failures...")
    for test_name, predicate in tests:
        test_failures = {}
        for category in ["ordinary", "no_fare", "hawashi"]:
            failures = collect_failing_indices(results, category, predicate)
            if failures:
                test_failures[category] = failures

        if test_failures:
            all_failures[test_name] = test_failures

    return all_failures


def save_failing_indices(all_failures, timestamp):
    """Save failing indices to JSON file."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"failing_indices_{timestamp}.json"

    print("Saving failing indices...")
    with open(output_file, "w") as f:
        json.dump(all_failures, f, indent=2)

    return output_file


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Timestamp: {timestamp}")
    print()

    # Generate results
    results = compute_all_results()

    # Save full results
    output_path = save_results_to_disk(results, timestamp)
    print(f"Results saved to: {output_path}")

    # Collect and save failing indices
    all_failures = run_all_tests_and_collect_failures(results)
    indices_path = save_failing_indices(all_failures, timestamp)
    print(f"Failing indices saved to: {indices_path}")

    # Print summary
    print()
    if all_failures:
        print("Failed tests:")
        for test_name, categories in all_failures.items():
            total_failed = sum(len(indices) for indices in categories.values())
            print(f"  {test_name}: {total_failed} failures")
            for cat, indices in categories.items():
                print(f"    {cat}: {len(indices)} failures")
    else:
        print("All tests passed!")


if __name__ == "__main__":
    main()
