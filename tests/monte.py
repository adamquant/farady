import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from farady import calculate_from_dict, HEIR_FIELDS, COUNT_HEIRS, BOOLEAN_HEIRS


from numpy.random import default_rng

rng = default_rng()

nums = rng.integers(0,5)
print(nums)


# case = {'iibn' : 4,'zawj' : True, 'zawja' : True, 'jadd' : 1, 'zawj': True}

# result = calculate_from_dict(case)


# def never_over_one():
    
    
#     count_heirs = 
    
    
#     sims = 1_000_000
#     for _ in range(sims):
