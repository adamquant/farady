# Copyright (C) 2018-2026  Adam Ahmed
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Farady - Islamic Inheritance Distribution Calculator.

This module provides functionality to calculate the distribution of assets
according to Islamic inheritance law (Faraid).

Family Member Parameters:
    --ibn: Son(s)
    --bint: Daughter(s)
    --iibn: Grandson(s) (son of son)
    --bibn: Granddaughter(s) (daughter of son)
    --iiibn: Great-grandson(s) (son of grandson)
    --biibn: Great-granddaughter(s) (daughter of grandson)
    --umm: Mother
    --jadda: Grandmother(s)
    --ab: Father
    --jadd: Grandfather (nearest in relation)
    --lium: Maternal Half-sibling(s)
    --shaqiqa: Full Sister(s)
    --shaqiq: Full Brother(s)
    --uliab: Paternal Half-sister(s)
    --aliab: Paternal Half-brother(s)
    --ibnamm_sh: Full Nephew (brother's son)
    --ibnamm_liab: Half Nephew (half-brother's son)
    --amm: Uncle (brother of father)
    --zawj: Husband
    --zawja: Wife
"""

from __future__ import annotations
from fractions import Fraction as frac

from farady.logging_config import (
    get_logger,
    log_calculation_start,
    log_calculation_end,
    log_validation_error,
    log_calculation_step,
)

from farady.processing import (
    PRETTY_NAMES,
    HEIR_FIELDS,
    BOOLEAN_HEIRS,
    COUNT_HEIRS,
)

from farady.classes import Case
from farady.calculation_functions import (
    convert_fard_to_shares,
    zawjayn_step,
    kalala_step,
    usool_step,
    furoo_step,
    hawashi_step,
    taseeb_step,
    awl_step,
    radd_step,
)

_logger = get_logger(__name__)


def calculate(case: Case) -> Case:
    """Calculate inheritance distribution for a given family case.

    This is the main entry point for calculating inheritance distribution.

    Args:
        case: A Case object containing all family member counts

    Returns:
        The same Case object with all calculation results populated
    """
    log_calculation_start(_logger, {"case": case.to_dict()})


    ###=== VALIDATION +++###

    # Validate umm (mother) - should not be more than 1
    umm_count = case.umm.get('count', 0) if case.umm else 0
    if not (case.umm is None or (isinstance(umm_count, (int, float)) and 0 <= umm_count <= 1)):
        case.ending = "invalid_input"
        case.status = "Failed"
        return case
    # Validate ab (father) - should not be more than 1
    ab_count = case.ab.get('count', 0) if case.ab else 0
    if not (case.ab is None or (isinstance(ab_count, (int, float)) and 0 <= ab_count <= 1)):
        case.ending = "invalid_input"
        case.status = "Failed"
        return case
    # Validate zawj (husband) - should not be more than 1
    zawj_count = case.zawj.get('count', 0) if case.zawj else 0
    if not (case.zawj is None or isinstance(zawj_count, bool) or 
            (isinstance(zawj_count, (int, float)) and 0 <= zawj_count <= 1)):
        case.ending = "invalid_input"
        case.status = "Failed"
        return case
    # Validate zawja (wives) - should not be more than 4
    zawja_count = case.zawja.get('count', 0) if case.zawja else 0
    if not (case.zawja is None or isinstance(zawja_count, bool) or 
            (isinstance(zawja_count, (int, float)) and 0 <= zawja_count <= 4)):
        case.ending = "invalid_input"
        case.status = "Failed"
        return case
    # Validate jadd (paternal grandfather) - should not be more than 1
    jadd_count = case.jadd.get('count', 0) if case.jadd else 0
    if not (case.jadd is None or (isinstance(jadd_count, (int, float)) and 0 <= jadd_count <= 1)):
        case.ending = "invalid_input"
        case.status = "Failed"
        return case


    ###+++ SPECIAL CASES +++###

    if case.is_umuriya:
        if case.is_umuriya1:
            case.zawj["fard"] = frac("3/6")
            case.ab["fard"] = frac("2/6")
            case.umm["fard"] = frac("1/6")
            case.ending = "umuriya1"
        elif case.is_umuriya2:
            case.zawja["fard"] = frac("1/4")
            case.ab["fard"] = frac("1/2")
            case.umm["fard"] = frac("1/4")
            case.ending = "umuriya2"

    elif case.is_mushtaraka:
        case.zawj["fard"] = frac("1/2")
        case.lium["fard"] = frac("1/3")
        if case.umm.get("count"):
            case.umm["fard"] = frac("1/6")
        elif case.jadda.get("count"):
            case.jadda["fard"] = frac("1/6")
        case.ending = "mushtaraka"

    ###=== REGULAR CASES ===###
    
    else:
        if case.is_married:
            case = zawjayn_step(case)

        if case.has_any_usool:
            case = usool_step(case)

        if case.has_any_furoo:
            case = furoo_step(case)

        if case.has_hawashi:
            if not (case.has_m_usool or case.has_m_furoo): # hanbali for now @adam
                case = hawashi_step(case)

        if case.is_kalala:
            case = kalala_step(case)

    case = convert_fard_to_shares(case)

    ###+++ GRACEFUL ENDINGS +++###

    if case.baqi < 0:
        case = awl_step(case)
        case.ending = "awl"
    
    elif case.baqi > 0:
        if case.asib_present or case.asib:
            case = taseeb_step(case)
            case.ending = "taseeb"
        elif case.total > 0:
            case = radd_step(case)
            case.ending = "radd"

    case.status = _determine_status(case)


    return case


def _determine_status(case: Case) -> str:
    """Determine the status of the calculation."""
    if case.total == 0 and case.ending is None:
        return "Failed"
    elif round(case.total, 3) == 1.00:
        return "Complete"
    else:
        return "Unknown"


def _build_distribution(case: Case) -> dict[str, int]:
    """Build simplified distribution dict from case with heir name and share value only."""
    distribution = {}

    for name, heir in zip(case._all_heir_names, case._all_heirs):
        shares = heir.get("shares")

        # Only include heirs with positive shares
        if shares is not None and shares > 0:
            # Convert to integer if it's a float (shouldn't happen with our fixes)
            distribution[name] = int(shares)

    return distribution


def calculate_inheritance(**family_members) -> Case:
    """Convenience function to calculate inheritance distribution.

    Args:
        **family_members: Keyword arguments for each family member count.
                        Example: ibn=2, bint=3, umm=1, zawja=True

    Returns:
        Case object with calculation results

    Example:
        >>> result = calculate_inheritance(ibn=2, bint=1, umm=1, zawja=True)
    """
    case = Case.from_dict(family_members)
    return calculate(case)


def debug_calculate(case: Case, original_input: dict | None = None) -> dict:
    """Calculate inheritance with full debugging information.

    Args:
        case: Case object to calculate
        original_input: Optional original input data for debugging context

    Returns:
        dict with debugging information:
        - 'input': Original input data (if provided)
        - 'case': Full calculated Case object
        - 'distribution': Simplified distribution card
        - 'summary': Key calculation metrics
    """
    # Perform calculation
    result_case = calculate(case)

    # Build distribution card
    distribution = _build_distribution(result_case)

    # Create summary
    summary = {
        "total_shares": result_case.total_shares,
        "raas": result_case.raas,
        "total_fraction": float(result_case.total),
        "ending": result_case.ending,
        "asib": result_case.asib,
        "status": result_case.status,
    }

    # Return comprehensive debug info
    debug_info = {
        "case": result_case,
        "distribution": distribution,
        "summary": summary,
    }

    if original_input is not None:
        debug_info["input"] = original_input

    return debug_info


def calculate_from_dict(family_data: dict) -> Case:
    """Calculate inheritance from a dictionary.

    Convenience function that creates a Case from a dict
    and calculates the distribution. Useful for CSV data.

    Args:
        family_data: Dictionary with family member counts.
                     Example: {'ibn': 2, 'bint': 1, 'zawja': True}
                     String values like '1', 'True', 'yes' are also handled.
                     Accepts numpy types (np.str_, np.int64, etc.) for compatibility
                     with numpy-generated data.

    Returns:
        Case object with calculation results

    Example:
        >>> data = {'ibn': 2, 'bint': 1, 'zawja': True}
        >>> result = calculate_from_dict(data)
    """
    normalized = {}
    for k, v in family_data.items():
        key = str(k) if hasattr(k, "item") and "numpy" in type(k).__module__ else k
        if hasattr(v, "item") and "numpy" in type(v).__module__:
            val = v.item()
        else:
            val = v
        normalized[key] = val
    family_data = normalized

    valid_fields = {
        "ibn",
        "bint",
        "iibn",
        "bibn",
        "iiibn",
        "biibn",
        "umm",
        "jadda",
        "ab",
        "jadd",
        "lium",
        "shaqiqa",
        "shaqiq",
        "uliab",
        "aliab",
        "ibnamm_sh",
        "ibnamm_liab",
        "amm",
        "zawj",
        "zawja",
    }
    boolean_fields = {"zawj", "zawja"}

    for key, value in family_data.items():
        if key not in valid_fields:
            log_validation_error(
                _logger, field=key, value=value, reason="Unknown field name"
            )
            case = Case()
            case.ending = "invalid_input"
            case.status = "Failed"
            return case

        if key in boolean_fields:
            if isinstance(value, bool):
                continue
            if isinstance(value, str):
                if value.strip().lower() not in (
                    "true",
                    "false",
                    "1",
                    "0",
                    "yes",
                    "no",
                    "",
                ):
                    log_validation_error(
                        _logger,
                        field=key,
                        value=value,
                        reason="Invalid boolean field value",
                    )
                    case = Case()
                    case.ending = "invalid_input"
                    case.status = "Failed"
                    return case
            elif not isinstance(value, (int, float)):
                log_validation_error(
                    _logger,
                    field=key,
                    value=value,
                    reason="Invalid type for boolean field",
                )
                case = Case()
                case.ending = "invalid_input"
                case.status = "Failed"
                return case
        else:
            if isinstance(value, (int, float)):
                if value < 0:
                    log_validation_error(
                        _logger, field=key, value=value, reason="Negative count value"
                    )
                    case = Case()
                    case.ending = "invalid_input"
                    case.status = "Failed"
                    return case
            elif isinstance(value, str):
                if value.strip().lower() in ("true", "yes"):
                    continue
                if value.strip().lower() in ("false", "no", ""):
                    continue
                try:
                    int_val = int(value)
                    if int_val < 0:
                        log_validation_error(
                            _logger,
                            field=key,
                            value=value,
                            reason="Negative count value from string",
                        )
                        case = Case()
                        case.ending = "invalid_input"
                        case.status = "Failed"
                        return case
                except ValueError:
                    try:
                        int(float(value))
                    except ValueError:
                        log_validation_error(
                            _logger,
                            field=key,
                            value=value,
                            reason="Could not convert string to int for count field",
                        )
                        case = Case()
                        case.ending = "invalid_input"
                        case.status = "Failed"
                        return case
            elif not isinstance(value, bool):
                log_validation_error(
                    _logger,
                    field=key,
                    value=value,
                    reason="Invalid type for count field",
                )
                case = Case()
                case.ending = "invalid_input"
                case.status = "Failed"
                return case

    zawj_val = family_data.get("zawj", False)
    zawja_val = family_data.get("zawja", False)

    if isinstance(zawj_val, str):
        zawj_val = zawj_val.strip().lower() in ("true", "1", "yes")
    if isinstance(zawja_val, str):
        zawja_val = zawja_val.strip().lower() in ("true", "1", "yes")

    if zawj_val and zawja_val:
        log_validation_error(
            _logger,
            field="zawj/zawja",
            value=f"zawj={zawj_val}, zawja={zawja_val}",
            reason="Both husband and wife present (invalid)",
        )
        case = Case()
        case.ending = "invalid_input"
        case.status = "Failed"
        return case

    case = Case.from_dict(family_data)
    return calculate(case)
