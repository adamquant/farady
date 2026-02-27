from __future__ import annotations
from fractions import Fraction as frac
from math import gcd
from typing import TYPE_CHECKING
from farady.classes import Case
import math


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else (a or b)


def _compute_heads(case: Case) -> int:
    """Compute heads for taseeb distribution.

    For mixed male/female asibs (lizakari): males=2, females=1.
    For single-type asibs: return 1 (treating at type level).
    """

    if case.asib == "ibn-bint":
        return case.ibn.get("count", 0) * 2 + case.bint.get("count", 0)
    elif case.asib == "iibn-bibn":
        return case.iibn.get("count", 0) * 2 + case.bibn.get("count", 0)
    elif case.asib == "iiibn-biibn":
        return case.iiibn.get("count", 0) * 2 + case.biibn.get("count", 0)
    elif case.asib == "iiibn-biibn-bibn":
        return (
            case.iiibn.get("count", 0) * 2
            + case.biibn.get("count", 0)
            + case.bibn.get("count", 0)
        )
    elif case.asib == "shaqiq-shaqiqa":
        return case.shaqiq.get("count", 0) * 2 + case.shaqiqa.get("count", 0)
    elif case.asib == "aliab-uliab":
        return case.aliab.get("count", 0) * 2 + case.uliab.get("count", 0)

    return 1


def inkisaar(case: Case) -> Case:
    """Adjust raas when baqi is not divisible by heads.

    Tasheeh al-inkisaar

    """
    import math

    if math.gcd(case.heads, case.baqi) == 1:
        new_raas = case.heads * case.raas
    elif case.baqi > case.heads:
        new_raas = math.gcd(case.heads, case.baqi) * case.raas
    elif case.baqi < case.heads:
        new_raas = int((case.heads / case.baqi) * case.raas)

    
    multiplier = new_raas // case.raas

    for heir in case._all_heirs:
        shares = heir.get("shares")
        if shares:
            heir["shares"] = shares * multiplier

    case._raas_override = new_raas

    return case


def convert_fard_to_shares(case: Case) -> Case:
    """Convert fard fractions to integer shares based on raas.

    Bridges allocation phase to rebalancing phase.
    """
    raas = case.raas

    for heir in case._all_heirs:
        fard = heir.get("fard")
        if fard:
            heir["shares"] = int(fard * raas)

    return case


def zawjayn_step(case: Case) -> Case:
    """Calculate spouse share.

    Husband receives 1/4 if there are furoo (descendants), 1/2 otherwise.
    Wife receives 1/8 if there are furoo, 1/4 otherwise.
    """
    if case.zawj.get("count"):
        case.zawj["fard"] = frac("1/4") if case.has_any_furoo else frac("1/2")

    if case.zawja.get("count"):
        case.zawja["fard"] = frac("1/8") if case.has_any_furoo else frac("1/4")

    return case


def kalala_step(case: Case) -> Case:
    """Calculate kalala shares (when no descendants or male ascendants exist).

    Maternal half-siblings receive:
    - 1/6 if there is only one
    - 1/3 if there are two or more
    """
    lium_count = case.lium.get("count", 0)
    if lium_count:
        case.lium["fard"] = frac(1, 6) if lium_count == 1 else frac(1, 3)

    return case


def usool_step(case: Case) -> Case:
    """Calculate usool (roots) shares - parents and grandparents."""

    if case.has_any_furoo:
        if case.ab.get("count"):
            case.ab["fard"] = frac("1/6")
            if not case.has_m_furoo:
                case.asib = "ab"

        elif case.jadd.get("count"):
            case.jadd["fard"] = frac("1/6")
            if not case.has_m_furoo:
                case.asib = "jadd"

        if case.umm.get("count"):
            case.umm["fard"] = frac("1/6")
        elif case.jadda.get("count"):
            case.jadda["fard"] = frac("1/6")

    elif not case.has_any_furoo and not case.has_jame:
        if case.umm.get("count"):
            case.umm["fard"] = frac("1/3")
        elif case.jadda.get("count"):
            case.jadda["fard"] = frac("1/6")

    elif case.has_jame:
        if case.umm.get("count"):
            case.umm["fard"] = frac("1/6")
        elif case.jadda.get("count"):
            case.jadda["fard"] = frac("1/6")

    if not case.has_m_furoo:
        if case.ab.get("count"):
            case.asib = "ab"
        elif case.jadd.get("count"):
            case.asib = "jadd"

    return case


def furoo_step(case: Case) -> Case:
    """Calculate furoo (descendants) shares - children and grandchildren."""

    if case.ibn.get("count", 0) and not case.bint.get("count", 0):
        case.asib = "ibn"
    elif case.ibn.get("count", 0) and case.bint.get("count", 0):
        case.asib = "ibn-bint"
    elif not case.ibn.get("count", 0) and case.bint.get("count", 0):
        if case.bint.get("count", 0) == 1:
            case.bint["fard"] = frac(1, 2)
        else:
            case.bint["fard"] = frac(2, 3)

    if case.asib is None and (case.ibn.get("count", 0) or case.bibn.get("count", 0)):
        if case.ibn.get("count", 0):
            if not case.bibn.get("count", 0):
                case.asib = "iibn"
            else:
                case.asib = "iibn-bibn"
        elif case.bibn.get("count", 0) and case.is_bint_taking_half:
            case.bibn["fard"] = frac(1, 6)

        elif case.bibn.get("count", 0) and not (case.is_bint_taking_half or case.is_bint_taking_twothirds):
            if case.bibn.get("count", 0) == 1:
                case.bibn["fard"] = frac(1, 2)
            else:
                case.bibn["fard"] = frac(2, 3)

        elif case.is_bint_taking_twothirds and case.bibn.get("count", 0):
            pass

    if case.asib is None:
        if case.iiibn.get("count", 0):
            if not case.biibn.get("count", 0):
                case.asib = "iiibn"
            elif case.bibn.get("count", 0):
                case.asib = "iiibn-bibn"
            elif case.biibn.get("count", 0):
                case.asib = "iiibn-biibn"
            if case.bibn.get("count", 0) and case.biibn.get("count", 0):
                case.asib = "iiibn-biibn-bibn"
        elif case.biibn.get("count", 0) and case.is_bint_taking_half and not case.is_bint_taking_twothirds:
            case.biibn["fard"] = frac(1, 6)

        elif case.biibn.get("count", 0) and not (case.is_bint_taking_twothirds or case.is_bint_taking_half):
            if case.biibn.get("count", 0) == 1:
                case.biibn["fard"] = frac(1, 2)
            else:
                case.biibn["fard"] = frac(2, 3)

    return case


def hawashi_step(case: Case) -> Case:
    """Calculate hawashi (other relatives) shares.

    This handles:
    - Full and half siblings
    - Full and half nephews
    - Uncles
    """

    if case.shaqiq.get("count", 0) and not case.shaqiqa.get("count", 0):
        case.asib = "shaqiq"
    elif case.shaqiq.get("count", 0) and case.shaqiqa.get("count", 0):
        case.asib = "shaqiq-shaqiqa"
    elif not case.shaqiq.get("count", 0) and case.shaqiqa.get("count", 0) and not case.has_any_furoo:
        if case.shaqiqa.get("count", 0) == 1:
            case.shaqiqa["fard"] = frac("1/2")
        elif case.shaqiqa.get("count", 0) > 1:
            case.shaqiqa["fard"] = frac("2/3")

    elif (
        case.asib is None
        and case.shaqiqa.get("count", 0)
        and (case.is_bint_taking_half or case.is_bint_taking_twothirds)
    ):
        case.asib = "shaqiqa"

    if case.asib is None:
        if case.aliab.get("count", 0) and not case.uliab.get("count", 0):
            case.asib = "aliab"
        elif case.asib is None and case.aliab.get("count", 0) and case.uliab.get("count", 0):
            case.asib = "aliab-uliab"
        elif (
            case.asib is None
            and case.uliab.get("count", 0)
            and not case.shaqiqa.get("count", 0)
            and (case.is_bint_taking_half or case.is_bint_taking_twothirds)
        ):
            case.asib = "uliab"
        elif not case.aliab.get("count", 0):
            if (
                case.uliab.get("count", 0)
                and not case.has_any_furoo
                and case.shaqiqa.get("count", 0)
                and case.is_shaqiqa_taking_half
                and not any(
                    (
                        case.is_shaqiqa_taking_twothirds,
                        case.is_bint_taking_twothirds,
                        case.is_bint_taking_half,
                    )
                )
            ):
                case.uliab["fard"] = frac("1/6")
            elif (
                case.uliab.get("count", 0)
                and not case.has_any_furoo
                and not (case.shaqiqa.get("count", 0) or case.shaqiq.get("count", 0))
            ):
                case.uliab["fard"] = frac(1, 2) if case.uliab.get("count", 0) == 1 else frac(2, 3)

    if case.asib is None:
        if case.ibnamm_sh.get("count"):
            case.asib = "ibnamm_sh"
        
        elif case.ibnamm_liab.get("count"):
            case.asib = "ibnamm_liab"
        
        elif case.amm.get("count"):
            case.asib = "amm"

    return case


def taseeb_step(case: Case) -> Case:
    """Calculate ta'seeb (residual) shares.
    you only get here is an asib is present. I like tha tbhavior and i want to standardise it.
    When there are asib (residual heirs), they receive the remaining portion.
    For mixed male/female asibs (lizakari): uses heads calculation.
    For single-type asibs: baqi goes directly to that type.
    """

    if case.baqi == 0:
        return case

    case.heads = _compute_heads(case)
    if case.heads == 0:
        return case # when would htis ever be @adam?

    # RUN INKISAAR STEP

    if case.baqi % case.heads != 0:
        case = inkisaar(case)

    taseeb_unit = case.baqi // case.heads

    if case.asib == "ibn":
        case.ibn["shares"] = case.ibn.get("shares", 0) + case.baqi
    elif case.asib == "iibn":
        case.iibn["shares"] = case.iibn.get("shares", 0) + case.baqi
    elif case.asib == "iiibn":
        case.iiibn["shares"] = case.iiibn.get("shares", 0) + case.baqi
    elif case.asib == "ibn-bint":
        case.ibn["shares"] = (
            case.ibn.get("shares", 0) + case.ibn.get("count", 0) * 2 * taseeb_unit
        )
        case.bint["shares"] = (
            case.bint.get("shares", 0) + case.bint.get("count", 0) * taseeb_unit
        )
    elif case.asib == "iibn-bibn":
        case.iibn["shares"] = (
            case.iibn.get("shares", 0) + case.iibn.get("count", 0) * 2 * taseeb_unit
        )
        case.bibn["shares"] = (
            case.bibn.get("shares", 0) + case.bibn.get("count", 0) * taseeb_unit
        )
    elif case.asib == "iiibn-biibn":
        case.iiibn["shares"] = (
            case.iiibn.get("shares", 0) + case.iiibn.get("count", 0) * 2 * taseeb_unit
        )
        case.biibn["shares"] = (
            case.biibn.get("shares", 0) + case.biibn.get("count", 0) * taseeb_unit
        )
    elif case.asib == "iiibn-biibn-bibn":
        case.iiibn["shares"] = (
            case.iiibn.get("shares", 0) + case.iiibn.get("count", 0) * 2 * taseeb_unit
        )
        case.biibn["shares"] = (
            case.biibn.get("shares", 0) + case.biibn.get("count", 0) * taseeb_unit
        )
        case.bibn["shares"] = (
            case.bibn.get("shares", 0) + case.bibn.get("count", 0) * taseeb_unit
        )
    elif case.asib == "ab":
        case.ab["shares"] = case.ab.get("shares", 0) + case.baqi
    elif case.asib == "jadd":
        case.jadd["shares"] = case.jadd.get("shares", 0) + case.baqi
    elif case.asib == "shaqiq":
        case.shaqiq["shares"] = case.shaqiq.get("shares", 0) + case.baqi
    elif case.asib == "shaqiqa":
        case.shaqiqa["shares"] = case.shaqiqa.get("shares", 0) + case.baqi
    elif case.asib == "shaqiq-shaqiqa":
        case.shaqiq["shares"] = (
            case.shaqiq.get("shares", 0) + case.shaqiq.get("count", 0) * 2 * taseeb_unit
        )
        case.shaqiqa["shares"] = (
            case.shaqiqa.get("shares", 0) + case.shaqiqa.get("count", 0) * taseeb_unit
        )
    elif case.asib == "aliab":
        case.aliab["shares"] = case.aliab.get("shares", 0) + case.baqi
    elif case.asib == "uliab":
        case.uliab["shares"] = case.uliab.get("shares", 0) + case.baqi
    elif case.asib == "aliab-uliab":
        case.aliab["shares"] = (
            case.aliab.get("shares", 0) + case.aliab.get("count", 0) * 2 * taseeb_unit
        )
        case.uliab["shares"] = (
            case.uliab.get("shares", 0) + case.uliab.get("count", 0) * taseeb_unit
        )
    elif case.asib == "ibnamm_sh":
        case.ibnamm_sh["shares"] = case.ibnamm_sh.get("shares", 0) + case.baqi
    elif case.asib == "ibnamm_liab":
        case.ibnamm_liab["shares"] = case.ibnamm_liab.get("shares", 0) + case.baqi
    elif case.asib == "amm":
        case.amm["shares"] = case.amm.get("shares", 0) + case.baqi
    case.ending = "taseeb"
    
    return case


def awl_step(case: Case) -> Case:
    """Apply 'awl (reduction) when shares exceed 1.

    When the total of fard (predetermined) shares exceeds 1,
    all shares are reduced proportionally.
    """
    total_fard = sum(
        heir.get("fard", frac(0)) for heir in case._all_heirs if heir.get("fard")
    )

    if total_fard > 1:
        awl_factor = frac(1, total_fard.numerator) * total_fard.denominator
        for heir in case._all_heirs:
            if heir.get("fard"):
                heir["fard"] = heir["fard"] * awl_factor

    case.ending = "awl"

    return case


def radd_step(case: Case) -> Case:
    """Apply radd (return) when shares are less than 1.

    When the total of fard shares is less than 1, the remaining (baqi)
    goes back to fard holders proportionally, INCLUDING spouses in this build - future functionality will allow for a choice of classic vs contemporary spousal treatment w/r radd (AA)
    """

    ### DETERMINE RADD HEADS ###
    for name, heir in zip(case._all_heir_names, case._all_heirs):
        if name in ("zawj", "zawja"):
            continue
        if heir.get("shares", 0):
            case.radd_heirs.append((name, heir, heir.get("shares", 0)))
            case.total_shares_radd += heir.get("shares", 0)
    
    
    # assign to zawj or zawja in absence of radd heads.
    if len(case.radd_heirs) == 0 or case.total_shares_radd == 0:
        for name in ("zawj", "zawja"):
            heir = getattr(case, name)
            if heir.get("shares", 0):
                heir["shares"] = heir.get("shares", 0) + case.baqi
                break

###==== RADD: ONE SINF, NO ZAWJAYN ===###

    if len(case.radd_heirs) == 1 and not case.is_married:
        return radd_single_no_spouse(case)

###==== RADD: MULTI SINF, NO ZAWJAYN ===###
    elif len(case.radd_heirs) > 1 and not case.is_married: 
        return radd_multi_no_spouse(case)

###==== RADD: ONE SINF, WITH ZAWJAYN ===###
    elif len(case.radd_heirs) == 1 and case.is_married:
        return radd_single_with_spouse(case)
        

###==== RADD: MULTI SINF, WITH ZAWJAYN ===###       
        
    else:
        return radd_multi_with_spouse(case)

    case.ending = "radd"

    return case


###=== RADD FUNCTIONS ===####

def radd_single_no_spouse(case):
    case._raas_override = 1   
    heir_name, heir_data, _ = case.radd_heirs[0]        
    heir_data["shares"] = 1
    setattr(case, heir_name, heir_data)
    return case

def radd_multi_no_spouse(case):
    case._raas_override = case.total_shares_radd
    return case

def radd_single_with_spouse(case):
    
    if case.has_husband:
        spouse_denominator = case.zawj.get("fard", 0).denominator
        spouse_heir = getattr(case, 'zawja')
        spouse_heir['shares'] = 1
        setattr(case, 'zawj', spouse_heir)
    elif case.has_wife:
        spouse_denominator = case.zawja.get("fard", 0).denominator
        spouse_heir = getattr(case, 'zawja')
        spouse_heir['shares'] = 1
        setattr(case, 'zawja', spouse_heir)

    case._raas_override = spouse_denominator
    heir_name, heir_data, _ = case.radd_heirs[0]        
    heir_data["shares"] = spouse_denominator -1   
    setattr(case, heir_name, heir_data)
    
    return case


def radd_multi_with_spouse(case):
   
   #### ==== REQUIRES NEW MINI CASE ===###
    mini_case_spouse = create_mini_case_for_spouses(case)
    mini_case_radd = create_mini_case_for_radd(case)

    ###=== PREPARE FACTORS AND REBALANCING ===####

    mini_case_radd = assign_values_for_radd_conversion(mini_case_radd)
    radd_comparison_factor = math.lcm(mini_case_radd.get("raas", 0), mini_case_spouse.baqi)
    spousal_factor = radd_comparison_factor // mini_case_spouse.baqi
    radd_group_factor = radd_comparison_factor // mini_case_radd.get("raas", 0)
    case._raas_override = int(mini_case_spouse.raas * spousal_factor)

    ####=== UPDATE NEW SHARES ==###
    case = update_case_with_radd_shares(case, mini_case_radd, radd_group_factor, mini_case_spouse, spousal_factor)
    #assert case.total_shares == case.raas and case.baqi == 0, "Radd failed"
    return case


def assign_values_for_radd_conversion(mini_case_radd):
    """
    Only used for cases of multi with a spouse (Radd Case 4)
    
    Returns the mini_case_radd dict with computed raas value and new_share values for each heir
    """
    import math
    from fractions import Fraction
    
    # Extract fractions from heirs who have fard values
    shares_list = []
    heirs_with_fard = []
    
    for name, heir_data in mini_case_radd.items():
        if heir_data.get("fard"):
            shares_list.append(heir_data["fard"])
            heirs_with_fard.append(name)
    
    # If no heirs with fard values, set raas to 1
    if not shares_list:
        mini_case_radd["raas"] = 1
        return mini_case_radd
    
    # Calculate LCD of all denominators
    dens = [f.denominator for f in shares_list]
    lcd = math.lcm(*dens)
    
    # Calculate new shares for each heir and store in their entry
    total_new_shares = 0
    for i, name in enumerate(heirs_with_fard):
        f = mini_case_radd[name]["fard"]
        multiplier = lcd // f.denominator
        new_num = f.numerator * multiplier
        
        # Store the new numerator in the heir's entry
        mini_case_radd[name]["new_share"] = new_num
        total_new_shares += new_num
    
    # Add computed raas value to the dictionary
    mini_case_radd["raas"] = total_new_shares
    
    return mini_case_radd

def update_case_with_radd_shares(case, mini_case_radd, radd_group_factor, mini_case_spouse, spousal_factor):
    """
    Update case object directly with new share values (mutating function)
    
    Args:
        case: Main Case object to update directly
        mini_case_radd: Dictionary containing heir data with new_share values
        radd_group_factor: Factor to multiply new shares by
        mini_case_spouse: Spouse case object
        spousal_factor: Factor to multiply spouse shares by
        
    Returns:
        Updated Case object (same reference)
    """
    from fractions import Fraction
    
    # First update spouse shares
    if hasattr(mini_case_spouse, 'zawj') and mini_case_spouse.zawj.get("count", 0):
        spouse_heir = getattr(case, 'zawj')
        spouse_heir['shares'] = int(mini_case_spouse.zawj.get("shares", 0) * spousal_factor)
        setattr(case, 'zawj', spouse_heir)
    elif hasattr(mini_case_spouse, 'zawja') and mini_case_spouse.zawja.get("count", 0):
        spouse_heir = getattr(case, 'zawja')
        spouse_heir['shares'] = int(mini_case_spouse.zawja.get("shares", 0) * spousal_factor)
        setattr(case, 'zawja', spouse_heir)
    
    # Update shares for each heir in mini_case_radd
    for heir_name, heir_data in mini_case_radd.items():
        # Skip the special 'raas' key and ensure heir_data is a dict with 'new_share'
        if (heir_name != 'raas' and 
            isinstance(heir_data, dict) and 
            'new_share' in heir_data and
            heir_data['new_share'] is not None):
            
            # Get the current heir data from the case
            heir_obj = getattr(case, heir_name)
            
            # Calculate the new share value
            new_share_value = heir_data["new_share"] * radd_group_factor
            
            # Update the shares in the heir data
            heir_obj["shares"] = int(new_share_value)
            
            # Set the updated heir data back to the case
            setattr(case, heir_name, heir_obj)
    
    return case

def create_mini_case_for_radd(case):
    mini_case_radd = {}
    for name in case._all_heir_names:
        if name not in ("zawj", "zawja"): 
            heir_data = getattr(case, name)
            if heir_data.get("fard"):
                mini_case_radd[name] = {
                    "fard": heir_data["fard"],
                    "new_shares": 0
                }
    return mini_case_radd

def create_mini_case_for_spouses(case):
    mini_case_spouse = Case(
        zawj=case.zawj.copy() if (case.zawj.get("count", 0) or case.zawj.get("shares", 0)) else {},
        zawja=case.zawja.copy() if (case.zawja.get("count", 0) or case.zawja.get("shares", 0)) else {}
    )
    mini_case_spouse._raas_override = mini_case_spouse.raas
    
    # crucial to fix raas:
    mini_case_spouse._raas_override = mini_case_spouse.zawj.get("fard").denominator if mini_case_spouse.has_husband else mini_case_spouse.zawja.get("fard").denominator
    if mini_case_spouse.zawja.get("fard"):
        mini_case_spouse.zawja["shares"] = int(mini_case_spouse.zawja["fard"] * mini_case_spouse.raas)
    if mini_case_spouse.zawj.get("fard"):
        mini_case_spouse.zawj["shares"] = int(mini_case_spouse.zawj["fard"] * mini_case_spouse.raas)
    return mini_case_spouse