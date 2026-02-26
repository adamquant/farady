from __future__ import annotations
from fractions import Fraction as frac
from math import gcd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from farady.classes import Case


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else (a or b)


def _compute_heads(case: Case) -> int:
    """Compute heads for taseeb distribution.

    For mixed male/female asibs (lizakari): males=2, females=1.
    For single-type asibs: return 1 (treating at type level).
    """
    asib = case.asib

    if asib == "ibn-bint":
        return case.ibn.get("count", 0) * 2 + case.bint.get("count", 0)
    elif asib == "iibn-bibn":
        return case.iibn.get("count", 0) * 2 + case.bibn.get("count", 0)
    elif asib == "iiibn-biibn":
        return case.iiibn.get("count", 0) * 2 + case.biibn.get("count", 0)
    elif asib == "iiibn-biibn-bibn":
        return (
            case.iiibn.get("count", 0) * 2
            + case.biibn.get("count", 0)
            + case.bibn.get("count", 0)
        )
    elif asib == "shaqiq-shaqiqa":
        return case.shaqiq.get("count", 0) * 2 + case.shaqiqa.get("count", 0)
    elif asib == "aliab-uliab":
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
            case.bint_taking_half = True
        else:
            case.bint["fard"] = frac(2, 3)
            case.bints_taking_twothirds = True

    if case.asib is None and (case.ibn.get("count", 0) or case.bibn.get("count", 0)):
        if case.ibn.get("count", 0):
            if not case.bibn.get("count", 0):
                case.asib = "iibn"
            else:
                case.asib = "iibn-bibn"
        elif case.bibn.get("count", 0) and case.bint_taking_half:
            case.bibn["fard"] = frac(1, 6)
            case.bints_taking_twothirds = True
        elif case.bibn.get("count", 0) and not (case.bint_taking_half or case.bints_taking_twothirds):
            if case.bibn.get("count", 0) == 1:
                case.bibn["fard"] = frac(1, 2)
                case.bint_taking_half = True
            else:
                case.bibn["fard"] = frac(2, 3)
                case.bints_taking_twothirds = True
        elif case.bints_taking_twothirds and case.bibn.get("count", 0):
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
        elif case.biibn.get("count", 0) and case.bint_taking_half and not case.bints_taking_twothirds:
            case.biibn["fard"] = frac(1, 6)
            case.bints_taking_twothirds = True
        elif case.biibn.get("count", 0) and not (case.bints_taking_twothirds or case.bint_taking_half):
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

    case.shaqiqa_taking_half = False
    case.shaqiqas_taking_twothirds = False

    if case.shaqiq.get("count", 0) and not case.shaqiqa.get("count", 0):
        case.asib = "shaqiq"
    elif case.shaqiq.get("count", 0) and case.shaqiqa.get("count", 0):
        case.asib = "shaqiq-shaqiqa"
    elif not case.shaqiq.get("count", 0) and case.shaqiqa.get("count", 0) and not case.has_any_furoo:
        if case.shaqiqa.get("count", 0) == 1:
            case.shaqiqa["fard"] = frac("1/2")
            case.shaqiqa_taking_half = True
        elif case.shaqiqa.get("count", 0) > 1:
            case.shaqiqa["fard"] = frac("2/3")
            case.shaqiqas_taking_twothirds = True 
    elif (
        case.asib is None
        and case.shaqiqa.get("count", 0)
        and (case.bint_taking_half or case.bints_taking_twothirds) # @adam double check these
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
            and (case.bint_taking_half or case.bints_taking_twothirds)
        ):
            case.asib = "uliab"
        elif not case.aliab.get("count", 0):
            if (
                case.uliab.get("count", 0)
                and not case.has_any_furoo
                and case.shaqiqa.get("count", 0)
                and case.shaqiqa_taking_half
                and not any(
                    (
                        case.shaqiqas_taking_twothirds,
                        case.bints_taking_twothirds,
                        case.bint_taking_half,
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

    if case.asib_present and case.asib is None:
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

    asib = case.asib
    taseeb_unit = case.baqi // case.heads

    if asib == "ibn":
        case.ibn["shares"] = case.ibn.get("shares", 0) + case.baqi
    elif asib == "iibn":
        case.iibn["shares"] = case.iibn.get("shares", 0) + case.baqi
    elif asib == "iiibn":
        case.iiibn["shares"] = case.iiibn.get("shares", 0) + case.baqi
    elif asib == "ibn-bint":
        case.ibn["shares"] = (
            case.ibn.get("shares", 0) + case.ibn.get("count", 0) * 2 * taseeb_unit
        )
        case.bint["shares"] = (
            case.bint.get("shares", 0) + case.bint.get("count", 0) * taseeb_unit
        )
    elif asib == "iibn-bibn":
        case.iibn["shares"] = (
            case.iibn.get("shares", 0) + case.iibn.get("count", 0) * 2 * taseeb_unit
        )
        case.bibn["shares"] = (
            case.bibn.get("shares", 0) + case.bibn.get("count", 0) * taseeb_unit
        )
    elif asib == "iiibn-biibn":
        case.iiibn["shares"] = (
            case.iiibn.get("shares", 0) + case.iiibn.get("count", 0) * 2 * taseeb_unit
        )
        case.biibn["shares"] = (
            case.biibn.get("shares", 0) + case.biibn.get("count", 0) * taseeb_unit
        )
    elif asib == "iiibn-biibn-bibn":
        case.iiibn["shares"] = (
            case.iiibn.get("shares", 0) + case.iiibn.get("count", 0) * 2 * taseeb_unit
        )
        case.biibn["shares"] = (
            case.biibn.get("shares", 0) + case.biibn.get("count", 0) * taseeb_unit
        )
        case.bibn["shares"] = (
            case.bibn.get("shares", 0) + case.bibn.get("count", 0) * taseeb_unit
        )
    elif asib == "ab":
        case.ab["shares"] = case.ab.get("shares", 0) + case.baqi
    elif asib == "jadd":
        case.jadd["shares"] = case.jadd.get("shares", 0) + case.baqi
    elif asib == "shaqiq":
        case.shaqiq["shares"] = case.shaqiq.get("shares", 0) + case.baqi
    elif asib == "shaqiqa":
        case.shaqiqa["shares"] = case.shaqiqa.get("shares", 0) + case.baqi
    elif asib == "shaqiq-shaqiqa":
        case.shaqiq["shares"] = (
            case.shaqiq.get("shares", 0) + case.shaqiq.get("count", 0) * 2 * taseeb_unit
        )
        case.shaqiqa["shares"] = (
            case.shaqiqa.get("shares", 0) + case.shaqiqa.get("count", 0) * taseeb_unit
        )
    elif asib == "aliab":
        case.aliab["shares"] = case.aliab.get("shares", 0) + case.baqi
    elif asib == "uliab":
        case.uliab["shares"] = case.uliab.get("shares", 0) + case.baqi
    elif asib == "aliab-uliab":
        case.aliab["shares"] = (
            case.aliab.get("shares", 0) + case.aliab.get("count", 0) * 2 * taseeb_unit
        )
        case.uliab["shares"] = (
            case.uliab.get("shares", 0) + case.uliab.get("count", 0) * taseeb_unit
        )
    elif asib == "ibnamm_sh":
        case.ibnamm_sh["shares"] = case.ibnamm_sh.get("shares", 0) + case.baqi
    elif asib == "ibnamm_liab":
        case.ibnamm_liab["shares"] = case.ibnamm_liab.get("shares", 0) + case.baqi
    elif asib == "amm":
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

    print(f"DEBUG RADD STARTING...: {case.total, case.total_shares, case.raas, case.baqi}")

    for name, heir in zip(case._all_heir_names, case._all_heirs):
        if name in ("zawj", "zawja"):
            continue
        if heir.get("shares", 0):
            case.radd_heirs.append((name, heir, heir.get("shares", 0)))
            case.total_shares_radd += heir.get("shares", 0)

    print(f'radd heirs list 1: { case.radd_heirs}')
    print(f"DEBUG: radd shares totoa: {case.total_shares_radd}, other stuff {case.total, case.total_shares, case.raas, case.baqi}")
    print(f'case obj is: {case}')
    
    
    # assign to zawj or zawja in absence of radd heads.
    if len(case.radd_heirs) == 0 or case.total_shares_radd == 0:
        for name in ("zawj", "zawja"):
            heir = getattr(case, name)
            if heir.get("shares", 0):
                heir["shares"] = heir.get("shares", 0) + case.baqi
                break
        print(f"DEBUG: assinged radd to spouse")

###==== RADD: ONE SINF, NO ZAWJAYN ===###

    if len(case.radd_heirs) == 1 and not case.is_married:
        case._raas_override = 1   
        heir_name, heir_data, _ = case.radd_heirs[0]        
        heir_data["shares"] = 1
        setattr(case, heir_name, heir_data)
        return case

###==== RADD: MULTI SINF, NO ZAWJAYN ===###

    elif not case.is_married: 
        new_raas = case.total_shares_radd
        case._raas_override = new_raas


###==== RADD: ONE SINF, WITH ZAWJAYN ===###
    elif (case.zawj.get("count", 0) or case.zawja.get("count", 0) and :


###==== RADD: MULTI SINF, WITH ZAWJAYN ===###       
        
        case.baqi % case.total_shares_radd != 0:
        old_raas = case.raas
        new_raas = _lcm(old_raas, case.total_shares_radd)
        multiplier = new_raas // old_raas

        for heir in case._all_heirs:
            shares = heir.get("shares")
            if shares:
                heir["shares"] = shares * multiplier

        case._raas_override = new_raas
        case.total_shares_radd *= multiplier
        case.radd_heirs = [(n, h, h.get("shares", 0)) for n, h, _ in case.radd_heirs] # wth? overriding?
    print(f'radd ehirs {case.radd_heirs}')

    # Use fractional arithmetic for precise radd calculation
    total_shares = sum(shares for _, _, shares in case.radd_heirs)
    print(f"DEBUG: {case.total, case.total_shares, case.raas, case.baqi}")

    # Calculate and distribute radd portions
    total_radd_distributed = 0
    for i, (name, heir, shares) in enumerate(case.radd_heirs):
        # Calculate exact fractional radd portion
        radd_fraction = frac(case.baqi) * frac(shares, total_shares)
        radd_portion = int(radd_fraction)  # Integer division to get whole shares
        # Handle remainder - distribute it to the first heir to avoid fractional shares
        if i == 0:
            remainder = case.baqi - sum(
                int(frac(case.baqi) * frac(h_shares, total_shares))
                for _, _, h_shares in case.radd_heirs
            )
            radd_portion += remainder

        current_shares = heir.get("shares", 0)
        heir["shares"] = current_shares + radd_portion
        total_radd_distributed += radd_portion
    print(f"DEBUG: {case.total, case.total_shares, case.raas, case.baqi}")

    case.ending = "radd"

    return case
