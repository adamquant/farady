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


def test_total_always_one():
    """All inheritance distributions should sum to 1.0."""
    results = get_results()

    for category in ["ordinary", "no_fare", "hawashi"]:
        totals = [r.total for _, r in results[category]]
        failed = [i for i, t in enumerate(totals) if abs(t - 1.0) >= 1e-9]
        assert not failed, f"{category}: indices {failed[:10]}... have total != 1.0"


def test_status_is_complete():
    """All calculations should complete successfully."""
    results = get_results()

    for category in ["ordinary", "no_fare", "hawashi"]:
        statuses = [r.status for _, r in results[category]]
        failed = [i for i, s in enumerate(statuses) if s != "Complete"]
        assert not failed, (
            f"{category}: indices {failed[:10]}... have status != Complete"
        )


# Save results on module load (for debugging)
if __name__ != "__main__":
    try:
        output_path = save_results_to_disk(get_results())
        print(f"Results saved to: {output_path}")
    except Exception as e:
        print(f"Warning: Could not save results: {e}")
