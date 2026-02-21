"""Test utilities for Farady inheritance calculator.

This module provides helper functions for generating random test cases
and other utilities used in Monte Carlo testing and validation.

Usage:
    from test_tools import build_random_case
    case = build_random_case()
"""

import numpy as np

from farady import COUNT_HEIRS, BOOLEAN_HEIRS


def build_random_case(
    max_heirs: int = 5,
    max_count: int = 5,
    focus: str | None = None,
    force_heirs: dict | None = None,
    rng: np.random.Generator | None = None,
) -> dict:
    """Build a random inheritance case dictionary.

    Generates a random case with configurable constraints for Monte Carlo
    testing of the Farady inheritance calculator.

    Args:
        max_heirs: Maximum number of heir types to include in the case.
            Defaults to 5. Use 0 for no random heirs.
        max_count: Maximum count for each heir type.
            Defaults to 5. Each heir gets random count in range [0, max_count].
        focus: Optional constraint on which heirs to include.
            - None: Include all heir types randomly (ordinary case)
            - 'no_descendants': Exclude all descendants (ibn, bint, iibn, etc.)
            - 'hawashi': Exclude descendants AND male ascendants (ab, jadd)
            Defaults to None.
        force_heirs: Optional dict of heirs to force include.
            Keys are heir names, values are counts.
            For boolean heirs (zawj, zawja), the value is ignored - they're
            set to True.
            Example: {'umm': 1, 'zawja': True, 'ibn': 2}
            Defaults to None.
        rng: Optional numpy random generator for reproducibility.
            If None, creates a new default generator.
            Useful for seeding: rng=np.random.default_rng(42)
            Defaults to None.

    Returns:
        A dictionary representing a random inheritance case.
        Keys are heir names (e.g., 'ibn', 'zawja', 'umm').
        Values are either:
            - Boolean True for spouse heirs (zawj, zawja)
            - Integer count for other heirs

    Raises:
        No exceptions - invalid focus values are silently ignored.

    Examples:
        Basic random case:
            >>> case = build_random_case()
            >>> 'ibn' in case or 'umm' in case
            True

        Reproducible random case (seeded):
            >>> rng = np.random.default_rng(42)
            >>> case = build_random_case(rng=rng)

        Force include specific heirs:
            >>> case = build_random_case(force_heirs={'umm': 1, 'zawja': True})

        No descendants (for testing ascendant-only cases):
            >>> case = build_random_case(focus='no_descendants')

        Hawashi case (no descendants, no male ascendants):
            >>> case = build_random_case(focus='hawashi')

        Combined options:
            >>> case = build_random_case(
            ...     max_heirs=3,
            ...     focus='hawashi',
            ...     force_heirs={'umm': 1}
            ... )

    Notes:
        - Spouse (zawj/zawja) is randomly selected: 33% chance each,
          33% chance no spouse
        - If max_heirs=0, only spouse is randomly included
        - force_heirs overrides any random selection for those heirs
        - For boolean heirs in force_heirs, value is ignored (set to True)

    See Also:
        farady.calculate_from_dict: Function that processes these cases.
    """
    if rng is None:
        rng = np.random.default_rng()

    case = {}

    # Determine spouse (None, zawj, or zawja)
    # 33% chance each for zawj/zawja, 33% for no spouse
    spouse_options = [None, "zawj", "zawja"]
    spouse_choice = rng.choice(spouse_options)
    if spouse_choice:
        case[spouse_choice] = True

    # Define heir categories
    descendants = {"ibn", "bint", "iibn", "bibn", "iiibn", "biibn"}
    male_ascendants = {"ab", "jadd"}

    # Get available heirs based on focus
    available_heirs = list(COUNT_HEIRS)

    if focus == "no_descendants":
        # Exclude all descendants
        available_heirs = [h for h in available_heirs if h not in descendants]
    elif focus == "hawashi":
        # Exclude descendants and male ascendants (father, grandfather)
        excluded = descendants | male_ascendants
        available_heirs = [h for h in available_heirs if h not in excluded]

    # Random selection of heirs
    n_heirs = rng.integers(0, max_heirs + 1)
    if n_heirs > len(available_heirs):
        n_heirs = len(available_heirs)

    if n_heirs > 0:
        selected_heirs = rng.choice(available_heirs, size=n_heirs, replace=False)

        # Assign random counts to each selected heir
        for heir in selected_heirs:
            case[heir] = rng.integers(0, max_count + 1)

    # Apply forced heirs (overrides random selections)
    if force_heirs:
        for heir, count in force_heirs.items():
            if heir in BOOLEAN_HEIRS:
                case[heir] = True  # Boolean heirs just get set to True
            else:
                case[heir] = count  # Count heirs get the specified count

    return case
