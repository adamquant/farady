import sys
import os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from farady import calculate_from_dict, HEIR_FIELDS, COUNT_HEIRS, BOOLEAN_HEIRS
from test_tools import build_random_case


def test_total_always_one():
    sims = 100_000
    
    totals_ordinary = [calculate_from_dict(build_random_case()).total for _ in range(sims)]
    totals_no_fare = [calculate_from_dict(build_random_case(focus='no_descendants')).total for _ in range(sims)]
    totals_force_hawashi = [calculate_from_dict(build_random_case(focus='hawashi')).total for _ in range(sims)]
    assert all(t == 1.0 for t in totals_ordinary)
    assert all(t == 1.0 for t in totals_no_fare)
    assert all(t == 1.0 for t in totals_force_hawashi)
