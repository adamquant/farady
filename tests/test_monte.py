import sys
import os
import numpy as np
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from farady import calculate_from_dict
def load_test_cases():
    """Load pre-generated test cases from disk."""
    data_path = Path(__file__).parent / "test_cases.npz"
    data = np.load(data_path, allow_pickle=True)
    return {
        "ordinary": list(data["ordinary"]),
        "no_fare": list(data["no_fare"]),
        "hawashi": list(data["hawashi"]),
    }
def compute_all_results():
    """Run calculations on all test cases, cache results."""
    cases = load_test_cases()
    return {
        "ordinary": [calculate_from_dict(c) for c in cases["ordinary"]],
        "no_fare": [calculate_from_dict(c) for c in cases["no_fare"]],
        "hawashi": [calculate_from_dict(c) for c in cases["hawashi"]],
    }
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
        totals = [r.total for r in results[category]]
        failed = [i for i, t in enumerate(totals) if abs(t - 1.0) >= 1e-9]
        assert not failed, f"{category}: indices {failed[:10]}... have total != 1.0"
def test_status_is_complete():
    """All calculations should complete successfully."""
    results = get_results()
    
    for category in ["ordinary", "no_fare", "hawashi"]:
        statuses = [r.status for r in results[category]]
        failed = [i for i, s in enumerate(statuses) if s != "Complete"]
        assert not failed, f"{category}: indices {failed[:10]}... have status != Complete"