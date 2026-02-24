from __future__ import annotations
from fractions import Fraction as frac
from math import gcd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from farady.classes import Case


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else (a or b)


def lizakari_step(
    n_male: int, n_female: int, remaining: frac, raas: int
) -> tuple[frac, frac]:
    """Calculate male/female distribution for residual shares using Fractions.

    Males receive double the share of females.
    """
    if n_male == 0 and n_female == 0:
        return frac(0), frac(0)

    total_parts = n_male * 2 + n_female
    male_ratio = frac(n_male * 2, total_parts)
    female_ratio = frac(n_female, total_parts)

    male_share = remaining * male_ratio
    female_share = remaining * female_ratio

    return male_share, female_share


def zawjayn_step(case: Case) -> Case:
    """Calculate spouse share.

    Husband receives 1/4 if there are furoo (descendants), 1/2 otherwise.
    Wife receives 1/8 if there are furoo, 1/4 otherwise.
    """
    has_any_furoo = case.has_any_furoo

    if case.zawj.get("count"):
        case.zawj["fard"] = frac("1/4") if has_any_furoo else frac("1/2")

    if case.zawja.get("count"):
        case.zawja["fard"] = frac("1/8") if has_any_furoo else frac("1/4")

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

    return case


def taseeb_step(case: Case) -> Case:
    """Calculate ta'seeb (residual) shares.

    When there are asib (residual heirs), they receive the remaining portion.
    """
    baqi = case.baqi
    raas = case.raas
    asib = case.asib

    if asib == "ibn":
        case.ibn["shares"] = case.ibn.get("shares", 0) + baqi.numerator
    elif asib == "iibn":
        case.iibn["shares"] = case.iibn.get("shares", 0) + baqi.numerator
    elif asib == "iiibn":
        case.iiibn["shares"] = case.iiibn.get("shares", 0) + baqi.numerator
    elif asib == "ibn-bint":
        male_baqi, female_baqi = lizakari_step(
            case.ibn.get("count", 0), case.bint.get("count", 0), baqi, raas
        )
        case.ibn["shares"] = case.ibn.get("shares", 0) + male_baqi.numerator
        case.bint["shares"] = case.bint.get("shares", 0) + female_baqi.numerator
    elif asib == "iibn-bibn":
        male_baqi, female_baqi = lizakari_step(
            case.iibn.get("count", 0), case.bibn.get("count", 0), baqi, raas
        )
        case.iibn["shares"] = case.iibn.get("shares", 0) + male_baqi.numerator
        case.bibn["shares"] = case.bibn.get("shares", 0) + female_baqi.numerator
    elif asib == "iiibn-biibn":
        male_baqi, female_baqi = lizakari_step(
            case.iiibn.get("count", 0), case.biibn.get("count", 0), baqi, raas
        )
        case.iiibn["shares"] = case.iiibn.get("shares", 0) + male_baqi.numerator
        case.biibn["shares"] = case.biibn.get("shares", 0) + female_baqi.numerator
    elif asib == "iiibn-biibn-bibn":
        n_male = case.iiibn.get("count", 0)
        n_female1 = case.biibn.get("count", 0)
        n_female2 = case.bibn.get("count", 0)
        n_female = n_female1 + n_female2
        male_baqi, female_baqi = lizakari_step(n_male, n_female, baqi, raas)
        case.iiibn["shares"] = case.iiibn.get("shares", 0) + male_baqi.numerator
        if n_female:
            case.biibn["shares"] = (
                case.biibn.get("shares", 0) + (female_baqi / n_female) * n_female1
            )
            case.bibn["shares"] = (
                case.bibn.get("shares", 0) + (female_baqi / n_female) * n_female2
            )
    elif asib == "ab":
        case.ab["shares"] = case.ab.get("shares", 0) + baqi.numerator
    elif asib == "jadd":
        case.jadd["shares"] = case.jadd.get("shares", 0) + baqi.numerator
    elif asib == "shaqiq":
        case.shaqiq["shares"] = case.shaqiq.get("shares", 0) + baqi.numerator
    elif asib == "shaqiqa":
        case.shaqiqa["shares"] = case.shaqiqa.get("shares", 0) + baqi.numerator
    elif asib == "shaqiq-shaqiqa":
        male_baqi, female_baqi = lizakari_step(
            case.shaqiq.get("count", 0), case.shaqiqa.get("count", 0), baqi, raas
        )
        case.shaqiq["shares"] = case.shaqiq.get("shares", 0) + male_baqi.numerator
        case.shaqiqa["shares"] = case.shaqiqa.get("shares", 0) + female_baqi.numerator
    elif asib == "aliab":
        case.aliab["shares"] = case.aliab.get("shares", 0) + baqi.numerator
    elif asib == "uliab":
        case.uliab["shares"] = case.uliab.get("shares", 0) + baqi.numerator
    elif asib == "aliab-uliab":
        male_baqi, female_baqi = lizakari_step(
            case.aliab.get("count", 0), case.uliab.get("count", 0), baqi, raas
        )
        case.aliab["shares"] = case.aliab.get("shares", 0) + male_baqi.numerator
        case.uliab["shares"] = case.uliab.get("shares", 0) + female_baqi.numerator
    elif case.ibnamm_sh.get("count"):
        case.ibnamm_sh["shares"] = baqi.numerator
    elif case.ibnamm_liab.get("count"):
        case.ibnamm_liab["shares"] = case.ibnamm_liab.get("shares", 0) + baqi.numerator
    elif case.amm.get("count"):
        case.amm["shares"] = case.amm.get("shares", 0) + baqi.numerator

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

    When the total of fard shares is less than 1, the remaining
    goes to the residuary heirs proportionally.
    """
    total_fard = sum(
        heir.get("fard", frac(0)) for heir in case._all_heirs if heir.get("fard")
    )

    if total_fard < 1 and case.asib:
        radd_factor = frac(1, total_fard.numerator) * total_fard.denominator
        for heir in case._all_heirs:
            if heir.get("fard"):
                heir["fard"] = heir["fard"] * radd_factor

    return case
