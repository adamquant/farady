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

from fractions import Fraction as frac
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


PRETTY_NAMES = {
    "bint": "Daughter(s)",
    "ibn": "Son(s)",
    "bibn": "Granddaughter(s)",
    "iibn": "Grandson(s)",
    "biibn": "Great-granddaughter(s)",
    "iiibn": "Great-grandson(s)",
    "umm": "Mother",
    "jadda": "Grandmother(s)",
    "ab": "Father",
    "jadd": "Grandfather (nearest in relation)",
    "lium": "Maternal Half-sibling(s)",
    "shaqiqa": "Full Sister(s)",
    "shaqiq": "Full Brother(s)",
    "uliab": "Paternal Half-sister(s)",
    "aliab": "Paternal Half-brother(s)",
    "ibnamm_sh": "Full Nephew",
    "ibnamm_liab": "Half Nephew",
    "amm": "Uncle",
    "zawj": "Husband",
    "zawja": "Wife",
    "all_full_siblings_maternal_half": "All full siblings and maternal half siblings",
}


@dataclass
class InheritanceCase:
    """Represents a family case for inheritance calculation.

    Attributes:
        ibn: Number of sons
        bint: Number of daughters
        iibn: Number of grandsons (sons of sons)
        bibn: Number of granddaughters (daughters of sons)
        iiibn: Number of great-grandsons
        biibn: Number of great-granddaughters
        umm: Mother (0 or 1)
        jadda: Grandmother(s) (0 or 1)
        ab: Father (0 or 1)
        jadd: Grandfather (0 or 1)
        lium: Maternal half-siblings count
        shaqiqa: Full sisters count
        shaqiq: Full brothers count
        uliab: Paternal half-sisters count
        aliab: Paternal half-brothers count
        ibnamm_sh: Full nephew (brother's son) count
        ibnamm_liab: Half nephew (half-brother's son) count
        amm: Uncle (father's brother) count
        zawj: Husband (boolean)
        zawja: Wife (boolean)
    """

    ibn: int = 0
    bint: int = 0
    iibn: int = 0
    bibn: int = 0
    iiibn: int = 0
    biibn: int = 0
    umm: int = 0
    jadda: int = 0
    ab: int = 0
    jadd: int = 0
    lium: int = 0
    shaqiqa: int = 0
    shaqiq: int = 0
    uliab: int = 0
    aliab: int = 0
    ibnamm_sh: int = 0
    ibnamm_liab: int = 0
    amm: int = 0
    zawj: bool = False
    zawja: bool = False

    def to_dict(self) -> dict:
        """Convert case to dictionary format for calculation."""
        result = {}
        for k, v in self.__dict__.items():
            if v and v != 0:
                result[k] = v
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "InheritanceCase":
        """Create an InheritanceCase from a dictionary.

        Useful for loading from CSV or JSON data.

        Args:
            data: Dictionary with family member counts.
                  Example: {'ibn': 2, 'bint': 1, 'zawja': True}
                  String values like '1', 'True', 'yes' are handled intelligently:
                  - For spouse fields (zawj, zawja): '1', 'true', 'yes' → True
                  - For count fields: '1', '2', etc. → integer

        Returns:
            InheritanceCase instance
        """
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

        kwargs = {}
        for key, value in data.items():
            if key in valid_fields:
                if isinstance(value, str):
                    value = value.strip()
                    if key in boolean_fields:
                        if value.lower() in ("true", "1", "yes"):
                            kwargs[key] = True
                        elif value.lower() in ("false", "0", "no", ""):
                            kwargs[key] = False
                    else:
                        if value.lower() in ("true", "yes"):
                            kwargs[key] = 1
                        elif value.lower() in ("false", "no", ""):
                            pass
                        else:
                            try:
                                kwargs[key] = int(value)
                            except ValueError:
                                try:
                                    kwargs[key] = int(float(value))
                                except ValueError:
                                    pass
                elif isinstance(value, bool):
                    if key in boolean_fields:
                        kwargs[key] = value
                    else:
                        kwargs[key] = 1 if value else 0
                elif isinstance(value, (int, float)):
                    if key in boolean_fields:
                        kwargs[key] = bool(value)
                    else:
                        kwargs[key] = int(value)

        return cls(**kwargs)


@dataclass
class InheritanceResult:
    """Result of an inheritance calculation.

    Attributes:
        distribution: Dictionary of heir names to their fractional shares
        ending: How the distribution ended (ta'seeb, awl, radd, umuriya, mushtaraka)
        asib: The 'aasib (residual heir) if present
        total: Total portion accounted for
        status: Calculation status (Complete, Failed, Unknown)
        denominator: The total number of shares (raas) for this inheritance case
    """

    distribution: dict = field(default_factory=dict)
    ending: Optional[str] = None
    asib: Optional[str] = None
    total: float = 0.0
    status: str = "Unknown"
    denominator: Optional[int] = None

    def to_pretty_dict(self) -> dict:
        """Convert to pretty-printed dictionary with human-readable names."""
        return {PRETTY_NAMES.get(k, k): v for k, v in self.distribution.items()}

    def get_member_fraction(self, member: str) -> Optional[float]:
        """Get the fraction for a specific family member."""
        return self.distribution.get(member)


class InheritanceCalculator:
    """Calculator for Islamic inheritance distribution (Faraid).

    This class implements the rules of Islamic inheritance law to calculate
    the proper distribution of a deceased person's assets among their heirs.
    """

    def __init__(self):
        """Initialize the calculator."""
        pass

    def _lizakari(
        self, n_male: int, n_female: int, remaining: frac, raas: int
    ) -> tuple:
        """Calculate male/female distribution for residual shares using Fractions.

        Males receive double the share of females.

        Args:
            n_male: Number of male heirs
            n_female: Number of female heirs
            remaining: Remaining portion to distribute (as Fraction)
            raas: Total shares denominator

        Returns:
            Tuple of (male_share, female_share) as Fractions
        """
        if n_male == 0 and n_female == 0:
            return frac(0), frac(0)

        total_parts = n_male * 2 + n_female
        male_ratio = frac(n_male * 2, total_parts)
        female_ratio = frac(n_female, total_parts)

        male_share = remaining * male_ratio
        female_share = remaining * female_ratio

        return male_share, female_share

    def _zawjayn(self, new: dict, finish: dict, has_any_furoo: bool) -> dict:
        """Calculate spouse share.

        Husband receives 1/4 if there are furoo (descendants), 1/2 otherwise.
        Wife receives 1/8 if there are furoo, 1/4 otherwise.

        Args:
            new: Family member counts
            finish: Current distribution dictionary
            has_any_furoo: Whether there are any descendants (furoo)

        Returns:
            Updated distribution dictionary
        """
        if new.get("zawj") and has_any_furoo:
            finish["zawj"] = frac("1/4")
        elif new.get("zawj") and not has_any_furoo:
            finish["zawj"] = frac("1/2")
        elif new.get("zawja") and has_any_furoo:
            finish["zawja"] = frac("1/8")
        elif new.get("zawja") and not has_any_furoo:
            finish["zawja"] = frac("1/4")

        return finish

    def _kalala(self, new: dict, finish: dict) -> dict:
        """Calculate kalala shares (when no descendants or parents exist).

        Maternal half-siblings receive:
        - 1/6 if there is only one
        - 1/3 if there are two or more

        Args:
            new: Family member counts
            finish: Current distribution dictionary

        Returns:
            Updated distribution dictionary
        """
        if new.get("lium"):
            if new.get("lium") == 1:
                finish["lium"] = frac(1, 6)
            elif new.get("lium") > 1:
                finish["lium"] = frac(1, 3)

        return finish

    def _usool(
        self,
        new: dict,
        finish: dict,
        asib: Optional[str],
        has_any_furoo: bool,
        has_m_furoo: bool,
        has_jame: bool,
    ) -> tuple:
        """Calculate usool (roots) shares - parents and grandparents.

        Father receives 1/6 if there are descendants, otherwise may get residual.
        Grandfather receives 1/6 if there are descendants or father.
        Mother receives 1/6 if there are descendants or siblings, 1/3 otherwise.
        Grandmother receives 1/6.

        Args:
            new: Family member counts
            finish: Current distribution dictionary
            asib: Current asib assignment
            has_any_furoo: Whether there are descendants
            has_m_furoo: Whether there are male descendants
            has_jame: Whether there are siblings

        Returns:
            Tuple of (updated finish, updated asib)
        """
        if has_any_furoo:
            if new.get("ab"):
                finish["ab"] = frac("1/6")
                if not has_m_furoo:
                    asib = "ab"
            elif new.get("jadd"):
                finish["jadd"] = frac("1/6")
                if not has_m_furoo:
                    asib = "jadd"

            if new.get("umm"):
                finish["umm"] = frac("1/6")
            elif new.get("jadda"):
                finish["jadda"] = frac("1/6")

        elif not has_any_furoo and not has_jame:
            if new.get("umm"):
                finish["umm"] = frac("1/3")
            elif new.get("jadda"):
                finish["jadda"] = frac("1/6")

        elif has_jame:
            if new.get("umm"):
                finish["umm"] = frac("1/6")
            elif new.get("jadda"):
                finish["jadda"] = frac("1/6")

        if not has_m_furoo:
            if new.get("ab"):
                asib = "ab"
            elif new.get("jadd"):
                asib = "jadd"

        return finish, asib

    def _furoo(
        self, new: dict, finish: dict, asib: Optional[str], has_hawashi: bool
    ) -> tuple:
        """Calculate furoo (descendants) shares - children and grandchildren.

        This handles:
        - Sons and daughters (direct descendants)
        - Grandsons and granddaughters
        - Great-grandsons and great-granddaughters

        Args:
            new: Family member counts
            finish: Current distribution dictionary
            asib: Current asib assignment
            has_hawashi: Whether there are hawashi (other relatives)

        Returns:
            Tuple of (updated finish, updated asib, bint_taking_half, bints_taking_twothirds)
        """
        bint_taking_half = False
        bints_taking_twothirds = False

        if new.get("ibn") and not new.get("bint"):
            asib = "ibn"
        elif new.get("ibn") and new.get("bint"):
            asib = "ibn-bint"
        elif not new.get("ibn") and new.get("bint"):
            if new.get("bint") == 1:
                finish["bint"] = frac(1, 2)
                bint_taking_half = True
            else:
                finish["bint"] = frac(2, 3)
                bints_taking_twothirds = True

        if asib is None and (new.get("iibn") or new.get("bibn")):
            if new.get("iibn"):
                if not new.get("bibn"):
                    asib = "iibn"
                else:
                    asib = "iibn-bibn"
            elif new.get("bibn") and bint_taking_half:
                finish["bibn"] = frac(1, 6)
                bints_taking_twothirds = True
            elif new.get("bibn") and not (bint_taking_half or bints_taking_twothirds):
                if new.get("bibn") == 1:
                    finish["bibn"] = frac(1, 2)
                    bint_taking_half = True
                else:
                    finish["bibn"] = frac(2, 3)
                    bints_taking_twothirds = True
            elif bints_taking_twothirds and new.get("bibn"):
                pass

        if asib is None:
            if new.get("iiibn"):
                if not new.get("biibn"):
                    asib = "iiibn"
                elif new.get("bibn"):
                    asib = "iiibn-bibn"
                elif new.get("biibn"):
                    asib = "iiibn-biibn"
                if new.get("bibn") and new.get("biibn"):
                    asib = "iiibn-biibn-bibn"
            elif new.get("biibn") and bint_taking_half and not bints_taking_twothirds:
                finish["biibn"] = frac(1, 6)
                bints_taking_twothirds = True
            elif new.get("biibn") and not (bints_taking_twothirds or bint_taking_half):
                if new.get("biibn") == 1:
                    finish["biibn"] = frac(1, 2)
                else:
                    finish["biibn"] = frac(2, 3)

        return finish, asib, bint_taking_half, bints_taking_twothirds

    def _hawashi(
        self,
        new: dict,
        finish: dict,
        asib: Optional[str],
        bint_taking_half: bool,
        bints_taking_twothirds: bool,
        has_any_furoo: bool,
        has_m_usool: bool,
        has_m_furoo: bool,
        shaqiqa_taking_half: bool,
        shaqiqas_taking_twothirds: bool,
    ) -> tuple:
        """Calculate hawashi (other relatives) shares.

        This handles:
        - Full and half siblings
        - Full and half nephews
        - Uncles

        Args:
            new: Family member counts
            finish: Current distribution dictionary
            asib: Current asib assignment
            bint_taking_half: Whether a daughter takes half
            bints_taking_twothirds: Whether daughters take 2/3
            has_any_furoo: Whether there are descendants
            has_m_usool: Whether there are male roots (father/grandfather)
            has_m_furoo: Whether there are male descendants
            shaqiqa_taking_half: Whether a sister takes half
            shaqiqas_taking_twothirds: Whether sisters take 2/3

        Returns:
            Tuple of (updated finish, updated asib, shaqiqa_taking_half, shaqiqas_taking_twothirds)
        """
        if new.get("shaqiq") and not new.get("shaqiqa"):
            asib = "shaqiq"
        elif new.get("shaqiq") and new.get("shaqiqa"):
            asib = "shaqiq-shaqiqa"
        elif not new.get("shaqiq") and new.get("shaqiqa") and not has_any_furoo:
            if new.get("shaqiqa") == 1:
                finish["shaqiqa"] = frac("1/2")
                shaqiqa_taking_half = True
            elif new.get("shaqiqa") > 1:
                finish["shaqiqa"] = frac("2/3")
                shaqiqas_taking_twothirds = True
        elif (
            asib is None
            and new.get("shaqiqa")
            and (bint_taking_half or bints_taking_twothirds)
        ):
            asib = "shaqiqa"

        if asib is None:
            if new.get("aliab") and not new.get("uliab"):
                asib = "aliab"
            elif asib is None and new.get("aliab") and new.get("uliab"):
                asib = "aliab-uliab"
            elif (
                asib is None
                and new.get("uliab")
                and not new.get("shaqiqa")
                and (bint_taking_half or bints_taking_twothirds)
            ):
                asib = "uliab"
            elif not new.get("aliab"):
                if (
                    new.get("uliab")
                    and not has_any_furoo
                    and new.get("shaqiqa")
                    and shaqiqa_taking_half
                    and not any(
                        [
                            shaqiqas_taking_twothirds,
                            bints_taking_twothirds,
                            bint_taking_half,
                        ]
                    )
                ):
                    finish["uliab"] = frac("1/6")
                elif (
                    new.get("uliab")
                    and not has_any_furoo
                    and not (new.get("shaqiqa") or new.get("shaqiq"))
                ):
                    if new.get("uliab") == 1:
                        finish["uliab"] = frac("1/2")
                    elif new.get("uliab") > 1:
                        finish["uliab"] = frac("2/3")

        return finish, asib, shaqiqa_taking_half, shaqiqas_taking_twothirds

    def _taseeb(
        self, total: frac, new: dict, finish: dict, asib: Optional[str], raas: int
    ) -> tuple:
        """Calculate ta'seeb (residual) shares using Fractions.

        When there are 'asib (residual heirs), they receive the remaining portion.

        Args:
            total: Current total allocated as Fraction
            new: Family member counts
            finish: Current distribution dictionary
            asib: The asib category
            raas: The denominator (total shares)

        Returns:
            Tuple of (updated finish, asib)
        """
        if raas is None:
            raas = 6
        current_total = sum(finish.values()) if finish else frac(0)
        remaining_shares = raas - (
            current_total.numerator * raas // current_total.denominator
        )
        baqi = frac(remaining_shares, raas)

        if asib == "ibn":
            finish["ibn"] = finish.get("ibn", frac(0)) + baqi
        elif asib == "iibn":
            finish["iibn"] = finish.get("iibn", frac(0)) + baqi
        elif asib == "iiibn":
            finish["iiibn"] = finish.get("iiibn", frac(0)) + baqi
        elif asib == "ibn-bint":
            male_baqi, female_baqi = self._lizakari(
                new.get("ibn", 0), new.get("bint", 0), baqi, raas
            )
            finish["ibn"] = finish.get("ibn", frac(0)) + male_baqi
            finish["bint"] = finish.get("bint", frac(0)) + female_baqi
        elif asib == "iibn-bibn":
            male_baqi, female_baqi = self._lizakari(
                new.get("iibn", 0), new.get("bibn", 0), baqi, raas
            )
            finish["iibn"] = finish.get("iibn", frac(0)) + male_baqi
            finish["bibn"] = finish.get("bibn", frac(0)) + female_baqi
        elif asib == "iiibn-biibn":
            male_baqi, female_baqi = self._lizakari(
                new.get("iiibn", 0), new.get("biibn", 0), baqi, raas
            )
            finish["iiibn"] = finish.get("iiibn", frac(0)) + male_baqi
            finish["biibn"] = finish.get("biibn", frac(0)) + female_baqi
        elif asib == "iiibn-biibn-bibn":
            n_male = new.get("iiibn", 0)
            n_female1 = new.get("biibn", 0)
            n_female2 = new.get("bibn", 0)
            n_female = n_female1 + n_female2
            male_baqi, female_baqi = self._lizakari(n_male, n_female, baqi, raas)
            finish["iiibn"] = finish.get("iiibn", frac(0)) + male_baqi
            if n_female:
                finish["biibn"] = (
                    finish.get("biibn", frac(0)) + (female_baqi / n_female) * n_female1
                )
                finish["bibn"] = (
                    finish.get("bibn", frac(0)) + (female_baqi / n_female) * n_female2
                )
        elif asib == "ab":
            finish["ab"] = finish.get("ab", frac(0)) + baqi
        elif asib == "jadd":
            finish["jadd"] = finish.get("jadd", frac(0)) + baqi
        elif asib == "shaqiq":
            finish["shaqiq"] = finish.get("shaqiq", frac(0)) + baqi
        elif asib == "shaqiqa":
            finish["shaqiqa"] = finish.get("shaqiqa", frac(0)) + baqi
        elif asib == "shaqiq-shaqiqa":
            male_baqi, female_baqi = self._lizakari(
                new.get("shaqiq", 0), new.get("shaqiqa", 0), baqi, raas
            )
            finish["shaqiq"] = finish.get("shaqiq", frac(0)) + male_baqi
            finish["shaqiqa"] = finish.get("shaqiqa", frac(0)) + female_baqi
        elif asib == "aliab":
            finish["aliab"] = finish.get("aliab", frac(0)) + baqi
        elif asib == "uliab":
            finish["uliab"] = finish.get("uliab", frac(0)) + baqi
        elif asib == "aliab-uliab":
            male_baqi, female_baqi = self._lizakari(
                new.get("aliab", 0), new.get("uliab", 0), baqi, raas
            )
            finish["aliab"] = finish.get("aliab", frac(0)) + male_baqi
            finish["uliab"] = finish.get("uliab", frac(0)) + female_baqi
        elif new.get("ibnamm_sh"):
            finish["ibnamm_sh"] = baqi
        elif new.get("ibnamm_liab"):
            finish["ibnamm_liab"] = finish.get("ibnamm_liab", frac(0)) + baqi
        elif new.get("amm"):
            finish["amm"] = finish.get("amm", frac(0)) + baqi

        return finish, asib

    def _calculate_denominator(self, finish: dict) -> Optional[int]:
        """Calculate the denominator (raas) for inheritance shares.

        Uses the LCM of all fraction denominators to determine total shares.

        Args:
            finish: Dictionary of heir names to their fractional shares

        Returns:
            Integer denominator (total shares), or None if calculation fails
        """
        from math import gcd

        def lcm(a, b):
            return abs(a * b) // gcd(a, b) if a and b else (a or b)

        denominators = []
        for v in finish.values():
            if hasattr(v, "denominator"):  # It's a Fraction
                if v.denominator not in denominators:
                    denominators.append(v.denominator)
            elif isinstance(v, float) and v > 0:
                # For floats, try to find a reasonable denominator
                # This handles residual shares from taseeb
                pass

        if not denominators:
            return None

        # Calculate LCM of all denominators
        result = denominators[0]
        for d in denominators[1:]:
            result = lcm(result, d)

        return result

    def _awl(self, total: frac, finish: dict, raas: Optional[int]) -> dict:
        """Apply 'awl (reduction) when shares exceed 1 using Fractions.

        When the total of fard (predetermined) shares exceeds 1,
        all shares are reduced proportionally.

        Args:
            total: Current total as Fraction (should be > 1)
            finish: Current distribution dictionary
            raas: The denominator (total shares)

        Returns:
            Updated distribution dictionary
        """
        if raas is None:
            raas = 6
        if total > 1:
            awl_factor = frac(1, total.numerator) * total.denominator
            finish = {k: v * awl_factor for k, v in finish.items()}
        return finish

    def _radd(self, total: frac, finish: dict, raas: Optional[int]) -> tuple:
        """Apply radd (return) when there is leftover after all shares using Fractions.

        The remaining portion is distributed among heirs proportionally,
        excluding spouses.

        Args:
            total: Current total as Fraction (should be < 1)
            finish: Current distribution dictionary
            raas: The denominator (total shares)

        Returns:
            Tuple of (updated finish, ending description)
        """
        if raas is None:
            raas = 6
        ziyada = 1 - total
        radd_factors = finish.copy()
        radd_factors = {
            k: v for k, v in radd_factors.items() if k not in ("zawj", "zawja")
        }

        if len(radd_factors) > 1:
            temp_total = sum(radd_factors.values())
            if temp_total == 0:
                return finish, "Unallocated baqi"
            else:
                radd_factors = {k: v / temp_total for k, v in radd_factors.items()}
                for k, v in radd_factors.items():
                    finish[k] = finish.get(k, frac(0)) + v * ziyada
                return finish, "radd"
        elif len(radd_factors) == 1:
            k, v = next(iter(radd_factors.items()))
            finish[k] = frac(1, 1)
            return finish, "radd"
        else:
            return finish, "radd"

    def calculate(self, case: InheritanceCase) -> InheritanceResult:
        """Calculate inheritance distribution for a given family case.

        This is the main entry point for calculating inheritance distribution.

        Args:
            case: An InheritanceCase object containing all family member counts

        Returns:
            An InheritanceResult object with the distribution and metadata
        """
        new = case.to_dict()

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
            finish["all_full_siblings_maternal_half"] = frac("1/3")
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
            finish = self._awl(total, finish, raas)
            ending = "awl"

        if total < 1:
            if asib_present or asib:
                finish, asib = self._taseeb(total, new, finish, asib, raas)
                ending = "taseeb"
            elif total > 0:
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

        return InheritanceResult(
            distribution=finish,
            ending=ending,
            asib=asib,
            total=final_total,
            status=status,
            denominator=denominator,
        )


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
    case = InheritanceCase(**family_members)
    calculator = InheritanceCalculator()
    return calculator.calculate(case)


def calculate_from_dict(family_data: dict) -> InheritanceResult:
    """Calculate inheritance from a dictionary.

    Convenience function that creates an InheritanceCase from a dict
    and calculates the distribution. Useful for CSV data.

    Args:
        family_data: Dictionary with family member counts.
                     Example: {'ibn': 2, 'bint': 1, 'zawja': True}
                     String values like '1', 'True', 'yes' are also handled.

    Returns:
        InheritanceResult with distribution and metadata

    Example:
        >>> data = {'ibn': 2, 'bint': 1, 'zawja': True}
        >>> result = calculate_from_dict(data)
    """
    zawj_val = family_data.get("zawj", False)
    zawja_val = family_data.get("zawja", False)

    if isinstance(zawj_val, str):
        zawj_val = zawj_val.strip().lower() in ("true", "1", "yes")
    if isinstance(zawja_val, str):
        zawja_val = zawja_val.strip().lower() in ("true", "1", "yes")

    if zawj_val and zawja_val:
        return InheritanceResult(
            distribution={},
            ending="invalid_input",
            asib=None,
            total=0.0,
            status="Failed",
            denominator=None,
        )

    case = InheritanceCase.from_dict(family_data)
    calculator = InheritanceCalculator()
    return calculator.calculate(case)


def load_csv_cases(csv_path: str) -> list:
    """Load inheritance cases from a CSV file.

    Each row in the CSV should have column headers matching valid family
    member names. Values can be integers, or strings like 'True', '1', 'yes'.

    Args:
        csv_path: Path to CSV file

    Returns:
        List of InheritanceCase objects

    Example CSV format:
        ibn,bint,zawja,expected_wife_share
        2,1,True,0.125
        1,0,False,0
    """
    import csv

    cases = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case = InheritanceCase.from_dict(row)
            cases.append(case)

    return cases


def process_csv_results(csv_path: str) -> list:
    """Load CSV and calculate results for each case.

    Returns a list of dicts with both the input data and calculated results.

    Args:
        csv_path: Path to CSV file

    Returns:
        List of dicts with keys: 'case' (InheritanceCase),
        'result' (InheritanceResult), 'row_data' (original dict)
    """
    import csv

    results = []
    calculator = InheritanceCalculator()

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case = InheritanceCase.from_dict(row)
            result = calculator.calculate(case)
            results.append({"case": case, "result": result, "row_data": row})

    return results
