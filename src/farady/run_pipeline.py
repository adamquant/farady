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
from farady.logging_config import (
    get_logger,
    log_calculation_start,
    log_calculation_end,
    log_validation_error,
    log_calculation_step,
)

from farady.formatting import (
    PRETTY_NAMES,
    HEIR_FIELDS,
    BOOLEAN_HEIRS,
    COUNT_HEIRS

)

_logger = get_logger(__name__)


from __future__ import annotations
from functools import cached_property
from fractions import Fraction as frac
from dataclasses import dataclass, field
from typing import Self, Any, TypedDict

from __future__ import annotations
from functools import cached_property
from fractions import Fraction as frac
from dataclasses import dataclass, field
from typing import Self, Any, TypedDict

type HeirKey = str
type FractionDict = dict[HeirKey, frac]
type DistributionDict = dict[HeirKey, float]
type CaseDict = dict[HeirKey, int | bool]

def calculate(self, case: Case) -> InheritanceResult:
        """Calculate inheritance distribution for a given family case.

        This is the main entry point for calculating inheritance distribution.

        Args:
            case: An Case object containing all family member counts

        Returns:
            An InheritanceResult object with the distribution and metadata
        """
        new = case.to_dict()

        log_calculation_start(_logger, {"case": new})

        ending = None
        asib = None

        finish = {k: v for k, v in new.items() if v != 0}
        finish = {k: (v if isinstance(v, bool) else 0) for k, v in new.items()}

        is_married = any([new.get("zawj"), new.get("zawja")])
        has_any_usool = any(
            [new.get("ab"), new.get("jadd"), new.get("umm"), new.get("jadda")]
        )
        has_m_usool = any([new.get("ab"), new.get("jadd")])
        has_m_furoo = any([new.get("ibn"), new.get("iibn"), new.get("iiibn")])
        has_any_furoo = any(
            [
                new.get("ibn"),
                new.get("bint"),
                new.get("iibn"),
                new.get("bibn"),
                new.get("iiibn"),
                new.get("biibn"),
            ]
        )
        has_jame = (
            sum(
                value
                for value in [
                    new.get("shaqiq"),
                    new.get("shaqiqa"),
                    new.get("aliab"),
                    new.get("uliab"),
                    new.get("lium"),
                ]
                if value is not None
            )
            > 1
        )
        has_hawashi = any(
            [
                new.get("shaqiq"),
                new.get("shaqiqa"),
                new.get("aliab"),
                new.get("uliab"),
                new.get("lium"),
                new.get("amm"),
                new.get("ibnamm_sh"),
                new.get("ibnamm_liab"),
            ]
        )

        bint_taking_half = False
        bints_taking_twothirds = False
        shaqiqa_taking_half = False
        shaqiqa_taking_twothirds = False

        is_kalala = not any([has_any_furoo, has_m_usool])
        asib_present = any(
            [
                has_m_usool,
                has_m_furoo,
                new.get("shaqiq"),
                new.get("aliab"),
                new.get("amm"),
                new.get("ibnamm_sh"),
                new.get("ibnamm_liab"),
            ]
        )

        is_umuriya1 = all(
            [
                new.get("ab"),
                new.get("umm"),
                new.get("zawj"),
                not any([has_jame, has_any_furoo]),
            ]
        )
        is_umuriya2 = all(
            [
                new.get("ab"),
                new.get("umm"),
                new.get("zawja"),
                not any([has_jame, has_any_furoo]),
            ]
        )
        is_umuriya = any([is_umuriya1, is_umuriya2])

        is_mushtaraka = False
        if new.get("lium"):
            is_mushtaraka = all(
                [
                    new.get("zawj"),
                    (new.get("umm") or new.get("jadda")),
                    new.get("lium") > 1,
                    new.get("shaqiq"),
                ]
            ) and not any([has_any_furoo, has_m_usool])

        if is_umuriya:
            if is_umuriya1:
                finish["zawj"] = frac("3/6")
                finish["ab"] = frac("2/6")
                finish["umm"] = frac("1/6")
                finish = {k: v for k, v in finish.items() if v != 0}
                ending = "umuriya1"
            elif is_umuriya2:
                finish["zawja"] = frac("1/4")
                finish["ab"] = frac("1/2")
                finish["umm"] = frac("1/4")
                ending = "umuriya2"

        elif is_mushtaraka:
            finish["zawj"] = frac("1/2")
            finish["all_full_siblings_maternal_half"] = frac("1/3") #@adam bug, 
            if new.get("umm"):
                finish["umm"] = frac("1/6")
            elif new.get("jadda"):
                finish["jadda"] = frac("1/6")
            ending = "mushtaraka"

        else:
            if is_married:
                finish = self._zawjayn(new, finish, has_any_furoo)

            if has_any_usool:
                finish, asib = self._usool(
                    new, finish, asib, has_any_furoo, has_m_furoo, has_jame
                )

            if has_any_furoo:
                finish, asib, bint_taking_half, bints_taking_twothirds = self._furoo(
                    new, finish, asib, has_hawashi
                )

            if has_hawashi:
                if not any([has_m_usool, has_m_furoo]):
                    finish, asib, shaqiqa_taking_half, shaqiqas_taking_twothirds = (
                        self._hawashi(
                            new,
                            finish,
                            asib,
                            bint_taking_half,
                            bints_taking_twothirds,
                            has_any_furoo,
                            has_m_usool,
                            has_m_furoo,
                            shaqiqa_taking_half,
                            shaqiqa_taking_twothirds,
                        )
                    )

            if is_kalala:
                finish = self._kalala(new, finish)

        finish = {k: v for k, v in finish.items() if v != 0}

        # Calculate initial raas from fard (predetermined) shares BEFORE taseeb/radd/awl
        raas = self._calculate_denominator(finish)

        total = sum(finish.values())

        if total > 1:
            log_calculation_step(_logger, "awl", {"total": float(total), "raas": raas})
            finish = self._awl(total, finish, raas)
            ending = "awl"

        if total < 1:
            if asib_present or asib:
                log_calculation_step(
                    _logger, "taseeb", {"total": float(total), "asib": asib}
                )
                finish, asib = self._taseeb(total, new, finish, asib, raas)
                ending = "taseeb"
            elif total > 0:
                log_calculation_step(_logger, "radd", {"total": float(total)})
                finish, ending = self._radd(total, finish, raas)

        finish = {k: v for k, v in finish.items() if v != 0}

        # Calculate final denominator after all adjustments
        denominator = self._calculate_denominator(finish)

        finish = {k: round(float(v), 4) for k, v in finish.items()}

        post_ending_total = sum(finish.values())

        if post_ending_total == 0 and ending is None:
            status = "Failed"
            ending = "No valid heirs."
        elif round(post_ending_total, 2) == 1.00:
            status = "Complete"
        else:
            status = "Unknown"

        final_total = sum(finish.values())

        # Calculate numerators for each heir
        numerators = {}
        if denominator:
            for heir, fraction in finish.items():
                if hasattr(fraction, "numerator"):
                    # Convert fraction to numerator: (numerator / denominator) * denominator
                    numerators[heir] = int(
                        fraction.numerator * denominator / fraction.denominator
                    )
                elif isinstance(fraction, (int, float)) and fraction > 0:
                    numerators[heir] = int(fraction * denominator)

        return InheritanceResult(
            distribution=finish,
            ending=ending,
            asib=asib,
            total=final_total,
            status=status,
            denominator=denominator,
            numerators=numerators,
        )

        log_calculation_end(
            _logger,
            {
                "distribution": finish,
                "ending": ending,
                "asib": asib,
                "total": final_total,
                "status": status,
                "denominator": denominator,
            },
        )

        return result


def calculate_inheritance(**family_members) -> InheritanceResult:
    """Convenience function to calculate inheritance distribution.

    Args:
        **family_members: Keyword arguments for each family member count.
                        Example: ibn=2, bint=3, umm=1, zawja=True

    Returns:
        InheritanceResult with distribution and metadata

    Example:
        >>> result = calculate_inheritance(ibn=2, bint=1, umm=1, zawja=True)
        >>> print(result.distribution)
    """
    case = Case(**family_members)
    calculator = InheritanceCalculator()
    return calculator.calculate(case)


def calculate_from_dict(family_data: dict) -> InheritanceResult:
    """Calculate inheritance from a dictionary.

    Convenience function that creates an Case from a dict
    and calculates the distribution. Useful for CSV data.

    Args:
        family_data: Dictionary with family member counts.
                     Example: {'ibn': 2, 'bint': 1, 'zawja': True}
                     String values like '1', 'True', 'yes' are also handled.
                     Accepts numpy types (np.str_, np.int64, etc.) for compatibility
                     with numpy-generated data.

    Returns:
        InheritanceResult with distribution and metadata

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
    count_fields = valid_fields - boolean_fields

    for key, value in family_data.items():
        if key not in valid_fields:
            log_validation_error(
                _logger,
                field=key,
                value=value,
                reason="Unknown field name",
            )
            return InheritanceResult(
                distribution={},
                ending="invalid_input",
                asib=None,
                total=0.0,
                status="Failed",
                denominator=None,
            )

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
                    return InheritanceResult(
                        distribution={},
                        ending="invalid_input",
                        asib=None,
                        total=0.0,
                        status="Failed",
                        denominator=None,
                    )
            elif not isinstance(value, (int, float)):
                log_validation_error(
                    _logger,
                    field=key,
                    value=value,
                    reason="Invalid type for boolean field",
                )
                return InheritanceResult(
                    distribution={},
                    ending="invalid_input",
                    asib=None,
                    total=0.0,
                    status="Failed",
                    denominator=None,
                )
        else:
            if isinstance(value, (int, float)):
                if value < 0:
                    log_validation_error(
                        _logger,
                        field=key,
                        value=value,
                        reason="Negative count value",
                    )
                    return InheritanceResult(
                        distribution={},
                        ending="invalid_input",
                        asib=None,
                        total=0.0,
                        status="Failed",
                        denominator=None,
                    )
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
                        return InheritanceResult(
                            distribution={},
                            ending="invalid_input",
                            asib=None,
                            total=0.0,
                            status="Failed",
                            denominator=None,
                        )
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
                        return InheritanceResult(
                            distribution={},
                            ending="invalid_input",
                            asib=None,
                            total=0.0,
                            status="Failed",
                            denominator=None,
                        )
            elif not isinstance(value, bool):
                log_validation_error(
                    _logger,
                    field=key,
                    value=value,
                    reason="Invalid type for count field",
                )
                return InheritanceResult(
                    distribution={},
                    ending="invalid_input",
                    asib=None,
                    total=0.0,
                    status="Failed",
                    denominator=None,
                )

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
        return InheritanceResult(
            distribution={},
            ending="invalid_input",
            asib=None,
            total=0.0,
            status="Failed",
            denominator=None,
        )

    case = Case.from_dict(family_data)
    calculator = InheritanceCalculator()
    return calculator.calculate(case)


