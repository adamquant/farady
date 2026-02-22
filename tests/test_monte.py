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
    }


def compute_all_results():
    """Run calculations on all test cases, cache results as (case, result) tuples."""
    cases = load_test_cases()
    results = {}
    for category in ["ordinary", "no_fare", "hawashi"]:
        results[category] = [
            (case, calculate_from_dict(case)) for case in cases[category]
        ]
    return results


def save_results_to_disk(results):
    """Save results to output folder with timestamp."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"monte_results_{timestamp}.json"

    output_data = {}
    for category, tuples in results.items():
        output_data[category] = [
            {"case": case, "result": result_to_dict(result)} for case, result in tuples
        ]

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    return output_file


# Cache results so we don't recompute for each test
_results = None


def get_results():
    global _results
    if _results is None:
        _results = compute_all_results()
    return _results


# ========== FAILING INDICES TRACKING ==========
# Reusable boilerplate for tracking failing indices in monte carlo tests.
# Copy this section when adding new test functions.
# ---------------------------------------------


def collect_failing_indices(results, category, predicate):
    """Collect indices where predicate(result) returns True.

    Args:
        results: Dict of category -> list of (case, result) tuples
        category: Category name (e.g., 'ordinary', 'no_fare', 'hawashi')
        predicate: Function that takes result and returns True if failed

    Returns:
        List of indices that failed the predicate
    """
    return [i for i, (_, r) in enumerate(results[category]) if predicate(r)]


def run_test_and_collect_failures(test_name, results, predicate, description):
    """Run a test across all categories and collect failing indices.

    Args:
        test_name: Name of the test (for error messages)
        results: Dict of category -> list of (case, result) tuples
        predicate: Function(result) -> bool, returns True if test fails
        description: Description of what the test checks (for error message)

    Returns:
        Dict of category -> list of failing indices

    Raises:
        AssertionError: If any failures found, with formatted error message
    """
    all_failures = {}
    for category in ["ordinary", "no_fare", "hawashi"]:
        failures = collect_failing_indices(results, category, predicate)
        if failures:
            all_failures[category] = failures

    if all_failures:
        error_parts = []
        for cat, indices in all_failures.items():
            error_parts.append(f"{cat}: indices {indices[:10]}...")
        raise AssertionError(f"{test_name}: {'; '.join(error_parts)}")

    return all_failures


# ---------------------------------------------
# End of failing indices boilerplate
# ===========================================


def test_total_always_one():
    """All inheritance distributions should sum to 1.0."""
    results = get_results()
    run_test_and_collect_failures(
        "test_total_always_one",
        results,
        lambda r: abs(r.total - 1.0) >= 1e-9,
        "total != 1.0",
    )


def test_status_is_complete():
    """All calculations should complete successfully."""
    results = get_results()
    run_test_and_collect_failures(
        "test_status_is_complete",
        results,
        lambda r: r.status != "Complete",
        "status != Complete",
    )


# ===========================================
# COPY BOILERPLATE BELOW FOR NEW TEST FUNCTIONS
# ===========================================
# Example:
#
# def test_your_new_check():
#     """Description of what this test checks."""
#     results = get_results()
#     run_test_and_collect_failures(
#         "test_your_new_check",
#         results,
#         lambda r: <your condition here>,
#         "<description of failure>"
#     )
# ===========================================


# Save results on module load (for debugging)
if __name__ != "__main__":
    try:
        output_path = save_results_to_disk(get_results())
        print(f"Results saved to: {output_path}")
    except Exception as e:
        print(f"Warning: Could not save results: {e}")
