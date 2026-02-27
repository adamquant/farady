#!/usr/bin/env python3
"""
Example showing how to use the _share_override functionality for individual heirs.
"""

from farady.classes import Case
from farady.calculation_functions import convert_fard_to_shares
from farady.pipelines import calculate
from fractions import Fraction as frac


def example_usage():
    # Create a case with some heirs that have fard values
    case = Case(
        bint={"count": 1},  # This will get fard = 1/2
        umm={"count": 1},  # This will get fard = 1/6
        zawj={"count": 1},  # This will get fard = 1/4
    )

    # Run the normal calculation pipeline first
    case = calculate(case)

    print("Before override:")
    print(f"RAAS: {case.raas}")
    print(f"Bint shares: {case.bint.get('shares', 0)} (fard: {case.bint.get('fard')})")
    print(f"Umm shares: {case.umm.get('shares', 0)} (fard: {case.umm.get('fard')})")
    print(f"Zawj shares: {case.zawj.get('shares', 0)} (fard: {case.zawj.get('fard')})")

    # Show the calculation for bint
    if case.bint.get("fard"):
        expected_shares = int(case.bint["fard"] * case.raas)
        print(
            f"\nBint's share calculated as fard * raas: {case.bint['fard']} * {case.raas} = {expected_shares}"
        )

    # Now let's override the bint's share calculation
    case.bint["_share_override"] = True

    # We need to rerun the share conversion to apply the override
    case = convert_fard_to_shares(case)

    print("\nAfter overriding bint share calculation:")
    print(f"RAAS: {case.raas}")
    print(f"Bint shares: {case.bint.get('shares', 0)} (fard: {case.bint.get('fard')})")
    print(f"Umm shares: {case.umm.get('shares', 0)} (fard: {case.umm.get('fard')})")
    print(f"Zawj shares: {case.zawj.get('shares', 0)} (fard: {case.zawj.get('fard')})")

    # Show the calculation
    if case.bint.get("fard"):
        expected_shares = int(case.bint["fard"] * case.raas)
        print(
            f"\nBint's share recalculated as fard * raas: {case.bint['fard']} * {case.raas} = {expected_shares}"
        )


if __name__ == "__main__":
    example_usage()
