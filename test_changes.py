#!/usr/bin/env python3

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from farady import calculate_from_dict

# Test case from the issue (with corrected constraints)
test_case = {"umm": 1, "shaqiqa": 3, "uliab": 5}

print("Testing case:", test_case)
result = calculate_from_dict(test_case)

# Import the distribution builder
from farady.pipelines import _build_distribution

print("Result:")
distribution = _build_distribution(result)
print("  Distribution:", distribution)
print("  Ending:", result.ending)
print("  Asib:", result.asib)
print("  Total shares:", result.total_shares)
print("  Total fraction:", result.total)
print("  Raas:", result.raas)
print("  Status:", result.status)
