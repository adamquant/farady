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


def inkisaar(case: Case, heads: int) -> Case:
    """Adjust raas when baqi is not divisible by heads.

    Finds LCM of current raas and heads, then recalculates all shares.
    """
    old_raas = case.raas
    new_raas = _lcm(old_raas, heads)
    multiplier = new_raas // old_raas

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
    has_any_furoo = case.has_any_furoo
    has_m_furoo = case.has_m_furoo
    has_jame = case.has_jame

    if has_any_furoo:
        if case.ab.get("count"):
            case.ab["fard"] = frac("1/6")
            if not has_m_furoo:
                case.asib = "ab"

        if case.jadd.get("count"):
            case.jadd["fard"] = frac("1/6")
            if not has_m_furoo:
                case.asib = "jadd"

        if case.umm.get("count"):
            case.umm["fard"] = frac("1/6")
        elif case.jadda.get("count"):
            case.jadda["fard"] = frac("1/6")

    elif not has_any_furoo and not has_jame:
        if case.umm.get("count"):
            case.umm["fard"] = frac("1/3")
        elif case.jadda.get("count"):
            case.jadda["fard"] = frac("1/6")

    elif has_jame:
        if case.umm.get("count"):
            case.umm["fard"] = frac("1/6")
        elif case.jadda.get("count"):
            case.jadda["fard"] = frac("1/6")

    if not has_m_furoo:
        if case.ab.get("count"):
            case.asib = "ab"
        elif case.jadd.get("count"):
            case.asib = "jadd"

    return case


def furoo_step(case: Case) -> Case:
    """Calculate furoo (descendants) shares - children and grandchildren."""
    bint_taking_half = False
    bints_taking_twothirds = False

    ibn_count = case.ibn.get("count", 0)
    bint_count = case.bint.get("count", 0)
    iibn_count = case.iibn.get("count", 0)
    bibn_count = case.bibn.get("count", 0)
    iiibn_count = case.iiibn.get("count", 0)
    biibn_count = case.biibn.get("count", 0)

    if ibn_count and not bint_count:
        case.asib = "ibn"
    elif ibn_count and bint_count:
        case.asib = "ibn-bint"
    elif not ibn_count and bint_count:
        if bint_count == 1:
            case.bint["fard"] = frac(1, 2)
            bint_taking_half = True
        else:
            case.bint["fard"] = frac(2, 3)
            bints_taking_twothirds = True

    if case.asib is None and (iibn_count or bibn_count):
        if iibn_count:
            if not bibn_count:
                case.asib = "iibn"
            else:
                case.asib = "iibn-bibn"
        elif bibn_count and bint_taking_half:
            case.bibn["fard"] = frac(1, 6)
            bints_taking_twothirds = True
        elif bibn_count and not (bint_taking_half or bints_taking_twothirds):
            if bibn_count == 1:
                case.bibn["fard"] = frac(1, 2)
                bint_taking_half = True
            else:
                case.bibn["fard"] = frac(2, 3)
                bints_taking_twothirds = True
        elif bints_taking_twothirds and bibn_count:
            pass

    if case.asib is None:
        if iiibn_count:
            if not biibn_count:
                case.asib = "iiibn"
            elif bibn_count:
                case.asib = "iiibn-bibn"
            elif biibn_count:
                case.asib = "iiibn-biibn"
            if bibn_count and biibn_count:
                case.asib = "iiibn-biibn-bibn"
        elif biibn_count and bint_taking_half and not bints_taking_twothirds:
            case.biibn["fard"] = frac(1, 6)
            bints_taking_twothirds = True
        elif biibn_count and not (bints_taking_twothirds or bint_taking_half):
            if biibn_count == 1:
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
    bint_taking_half = case.bint_taking_half
    bints_taking_twothirds = case.bints_taking_twothirds
    has_any_furoo = case.has_any_furoo

    shaqiq_count = case.shaqiq.get("count", 0)
    shaqiqa_count = case.shaqiqa.get("count", 0)
    aliab_count = case.aliab.get("count", 0)
    uliab_count = case.uliab.get("count", 0)

    shaqiqa_taking_half = False
    shaqiqas_taking_twothirds = False

    if shaqiq_count and not shaqiqa_count:
        case.asib = "shaqiq"
    elif shaqiq_count and shaqiqa_count:
        case.asib = "shaqiq-shaqiqa"
    elif not shaqiq_count and shaqiqa_count and not has_any_furoo:
        if shaqiqa_count == 1:
            case.shaqiqa["fard"] = frac("1/2")
            shaqiqa_taking_half = True
        elif shaqiqa_count > 1:
            case.shaqiqa["fard"] = frac("2/3")
            shaqiqas_taking_twothirds = True
    elif (
        case.asib is None
        and shaqiqa_count
        and (bint_taking_half or bints_taking_twothirds)
    ):
        case.asib = "shaqiqa"

    if case.asib is None:
        if aliab_count and not uliab_count:
            case.asib = "aliab"
        elif case.asib is None and aliab_count and uliab_count:
            case.asib = "aliab-uliab"
        elif (
            case.asib is None
            and uliab_count
            and not shaqiqa_count
            and (bint_taking_half or bints_taking_twothirds)
        ):
            case.asib = "uliab"
        elif not aliab_count:
            if (
                uliab_count
                and not has_any_furoo
                and shaqiqa_count
                and shaqiqa_taking_half
                and not any(
                    (
                        shaqiqas_taking_twothirds,
                        bints_taking_twothirds,
                        bint_taking_half,
                    )
                )
            ):
                case.uliab["fard"] = frac("1/6")
            elif (
                uliab_count
                and not has_any_furoo
                and not (shaqiqa_count or shaqiq_count)
            ):
                case.uliab["fard"] = frac(1, 2) if uliab_count == 1 else frac(2, 3)

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

    When there are asib (residual heirs), they receive the remaining portion.
    For mixed male/female asibs (lizakari): uses heads calculation.
    For single-type asibs: baqi goes directly to that type.
    """
    if case.baqi <= 0:
        return case

    heads = _compute_heads(case)
    case.heads = heads

    if heads == 0:
        return case

    if case.baqi % heads != 0:
        case = inkisaar(case, heads)

    baqi = case.baqi
    asib = case.asib
    taseeb_unit = baqi // heads

    if asib == "ibn":
        case.ibn["shares"] = case.ibn.get("shares", 0) + baqi
    elif asib == "iibn":
        case.iibn["shares"] = case.iibn.get("shares", 0) + baqi
    elif asib == "iiibn":
        case.iiibn["shares"] = case.iiibn.get("shares", 0) + baqi
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
        case.ab["shares"] = case.ab.get("shares", 0) + baqi
    elif asib == "jadd":
        case.jadd["shares"] = case.jadd.get("shares", 0) + baqi
    elif asib == "shaqiq":
        case.shaqiq["shares"] = case.shaqiq.get("shares", 0) + baqi
    elif asib == "shaqiqa":
        case.shaqiqa["shares"] = case.shaqiqa.get("shares", 0) + baqi
    elif asib == "shaqiq-shaqiqa":
        case.shaqiq["shares"] = (
            case.shaqiq.get("shares", 0) + case.shaqiq.get("count", 0) * 2 * taseeb_unit
        )
        case.shaqiqa["shares"] = (
            case.shaqiqa.get("shares", 0) + case.shaqiqa.get("count", 0) * taseeb_unit
        )
    elif asib == "aliab":
        case.aliab["shares"] = case.aliab.get("shares", 0) + baqi
    elif asib == "uliab":
        case.uliab["shares"] = case.uliab.get("shares", 0) + baqi
    elif asib == "aliab-uliab":
        case.aliab["shares"] = (
            case.aliab.get("shares", 0) + case.aliab.get("count", 0) * 2 * taseeb_unit
        )
        case.uliab["shares"] = (
            case.uliab.get("shares", 0) + case.uliab.get("count", 0) * taseeb_unit
        )
    elif asib == "ibnamm_sh":
        case.ibnamm_sh["shares"] = case.ibnamm_sh.get("shares", 0) + baqi
    elif asib == "ibnamm_liab":
        case.ibnamm_liab["shares"] = case.ibnamm_liab.get("shares", 0) + baqi
    elif asib == "amm":
        case.amm["shares"] = case.amm.get("shares", 0) + baqi

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

    return case


def radd_step(case: Case) -> Case:
    """Apply radd (return) when shares are less than 1.

    When the total of fard shares is less than 1, the remaining (baqi)
    goes back to fard holders proportionally, INCLUDING spouses in this build - future fucntionality will allow for a choice of classic vs conemporary spousal treatment w/r radd (AA)
    """
    baqi = case.baqi
    if baqi <= 0:
        return case

    radd_heirs = []
    radd_shares_total = 0

    for name, heir in zip(case._all_heir_names, case._all_heirs):
        if name in ("zawj", "zawja"):
            continue
        shares = heir.get("shares", 0)
        if shares:
            radd_heirs.append((name, heir, shares))
            radd_shares_total += shares

    if not radd_heirs or radd_shares_total == 0:
        if not case.asib:
            for name in ("zawj", "zawja"):
                heir = getattr(case, name)
                if heir.get("shares", 0) > 0:
                    heir["shares"] = heir.get("shares", 0) + baqi
                    break
        return case

    if baqi % radd_shares_total != 0:
        old_raas = case.raas
        new_raas = _lcm(old_raas, radd_shares_total)
        multiplier = new_raas // old_raas

        for heir in case._all_heirs:
            shares = heir.get("shares")
            if shares:
                heir["shares"] = shares * multiplier

        case._raas_override = new_raas
        baqi = case.baqi
        radd_shares_total *= multiplier
        radd_heirs = [(n, h, h.get("shares", 0)) for n, h, _ in radd_heirs]

    # Use fractional arithmetic for precise radd calculation
    total_shares = sum(shares for _, _, shares in radd_heirs)

    # Use fractional arithmetic for precise radd calculation
    total_shares = sum(shares for _, _, shares in radd_heirs)

    for name, heir, shares in radd_heirs:
        # Calculate exact fractional radd portion
        radd_fraction = frac(baqi) * frac(shares, total_shares)
        radd_portion = radd_fraction.numerator // radd_fraction.denominator

        # If there's a remainder, distribute it proportionally
        remainder = radd_fraction.numerator % radd_fraction.denominator
        if remainder:
            # Distribute remainder proportionally to avoid truncation
            if radd_heirs.index((name, heir, shares)) == 0:
                radd_portion += 1

        heir["shares"] = heir.get("shares", 0) + radd_portion

    return case
