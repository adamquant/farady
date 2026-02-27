from __future__ import annotations
from functools import reduce
from fractions import Fraction as frac
from dataclasses import dataclass, field
from typing import Self, Any, TypedDict


type HeirKey = str
type FractionDict = dict[HeirKey, frac]
type DistributionDict = dict[HeirKey, float]
type CaseDict = dict[HeirKey, int | bool]


class HeirData(TypedDict, total=False):
    count: int
    yarith: bool | None
    fard: frac | None
    asib: bool | None
    pct: float | None
    shares: int | None


def _default_heir_data() -> HeirData:
    return {}


@dataclass
class Case:
    ibn: HeirData = field(default_factory=_default_heir_data)
    bint: HeirData = field(default_factory=_default_heir_data)
    iibn: HeirData = field(default_factory=_default_heir_data)
    bibn: HeirData = field(default_factory=_default_heir_data)
    iiibn: HeirData = field(default_factory=_default_heir_data)
    biibn: HeirData = field(default_factory=_default_heir_data)
    umm: HeirData = field(default_factory=_default_heir_data)
    jadda: HeirData = field(default_factory=_default_heir_data)
    ab: HeirData = field(default_factory=_default_heir_data)
    jadd: HeirData = field(default_factory=_default_heir_data)
    lium: HeirData = field(default_factory=_default_heir_data)
    shaqiqa: HeirData = field(default_factory=_default_heir_data)
    shaqiq: HeirData = field(default_factory=_default_heir_data)
    uliab: HeirData = field(default_factory=_default_heir_data)
    aliab: HeirData = field(default_factory=_default_heir_data)
    ibnamm_sh: HeirData = field(default_factory=_default_heir_data)
    ibnamm_liab: HeirData = field(default_factory=_default_heir_data)
    amm: HeirData = field(default_factory=_default_heir_data)
    zawj: HeirData = field(default_factory=_default_heir_data)
    zawja: HeirData = field(default_factory=_default_heir_data)
    
    ending: str | None = None
    asib: str | None = None
    status: str | None = None
    heads: int | None = None
    _raas_override: int | None = None
    radd_heirs: list = field(default_factory=list)
    total_shares_radd: int = 0

    # Calculation state tracking attributes
    shaqiqa_taking_half: bool | None = None
    shaqiqas_taking_twothirds: bool | None = None
    bint_taking_half: bool | None = None
    bints_taking_twothirds: bool | None = None

    @property
    def has_husband(self) -> bool:
        return bool(self.zawj.get("count", 0))
    @property
    def has_wife(self) -> bool:
        return bool(self.zawja.get("count", 0))

    @property
    def _all_heirs(self) -> list[HeirData]:
        return [
            self.ibn,
            self.bint,
            self.iibn,
            self.bibn,
            self.iiibn,
            self.biibn,
            self.umm,
            self.jadda,
            self.ab,
            self.jadd,
            self.lium,
            self.shaqiqa,
            self.shaqiq,
            self.uliab,
            self.aliab,
            self.ibnamm_sh,
            self.ibnamm_liab,
            self.amm,
            self.zawj,
            self.zawja,
        ]

    @property
    def _all_heir_names(self) -> list[str]:
        return [
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
        ]

    @property
    def total_children(self) -> int:
        return self.ibn.get("count", 0) + self.bint.get("count", 0)

    @property
    def is_married(self) -> bool:
        return any((self.zawj.get("count", 0), self.zawja.get("count", 0)))

    @property
    def has_any_usool(self) -> bool:
        return any(
            (
                self.ab.get("count", 0),
                self.jadd.get("count", 0),
                self.umm.get("count", 0),
                self.jadda.get("count", 0),
            )
        )

    @property
    def has_m_usool(self) -> bool:
        return any((self.ab.get("count", 0), self.jadd.get("count", 0)))

    @property
    def has_m_furoo(self) -> bool:
        return any(
            (
                self.ibn.get("count", 0),
                self.iibn.get("count", 0),
                self.iiibn.get("count", 0),
            )
        )

    @property
    def has_any_furoo(self) -> bool:
        return any(
            (
                self.ibn.get("count", 0),
                self.bint.get("count", 0),
                self.iibn.get("count", 0),
                self.bibn.get("count", 0),
                self.iiibn.get("count", 0),
                self.biibn.get("count", 0),
            )
        )

    @property
    def has_jame(self) -> bool:
        return (
            sum(
                [
                    self.shaqiq.get("count", 0),
                    self.shaqiqa.get("count", 0),
                    self.aliab.get("count", 0),
                    self.uliab.get("count", 0),
                    self.lium.get("count", 0),
                ]
            )
            > 1
        )

    @property
    def has_hawashi(self) -> bool:
        return any(
            (
                self.shaqiq.get("count", 0),
                self.shaqiqa.get("count", 0),
                self.aliab.get("count", 0),
                self.uliab.get("count", 0),
                self.lium.get("count", 0),
                self.amm.get("count", 0),
                self.ibnamm_sh.get("count", 0),
                self.ibnamm_liab.get("count", 0),
            )
        )

    @property
    def is_asib(self) -> bool:
        return any(heir.get("asib", False) for heir in self._all_heirs)

    @property
    def is_bint_taking_half(self) -> bool:
        bint_heirs = [self.bint, self.bibn, self.biibn]
        return any(heir.get("fard") == frac(1, 2) for heir in bint_heirs)

    @property
    def is_bints_taking_twothirds(self) -> bool:
        bint_heirs = [self.bint, self.bibn, self.biibn]
        return any(heir.get("fard") == frac(2, 3) for heir in bint_heirs)

    @property
    def is_shaqiqa_taking_half(self) -> bool:
        return self.shaqiqa.get("fard") == frac(1, 2)

    @property
    def is_shaqiqa_taking_twothirds(self) -> bool:
        return self.shaqiqa.get("fard") == frac(2, 3)

    @property
    def is_kalala(self) -> bool:
        return not (self.has_any_furoo or self.has_m_usool)

    @property
    def asib_present(self) -> bool:
        return any(
            (
                self.has_m_usool,
                self.has_m_furoo,
                self.shaqiq.get("count", 0),
                self.aliab.get("count", 0),
                self.amm.get("count", 0),
                self.ibnamm_sh.get("count", 0),
                self.ibnamm_liab.get("count", 0),
            )
        )

    @property
    def is_umuriya1(self) -> bool:
        return all(
            (
                self.ab.get("count", 0),
                self.umm.get("count", 0),
                self.zawj.get("count", 0),
                not (self.has_jame or self.has_any_furoo),
            )
        )

    @property
    def is_umuriya2(self) -> bool:
        return all(
            (
                self.ab.get("count", 0),
                self.umm.get("count", 0),
                self.zawja.get("count", 0),
                not (self.has_jame or self.has_any_furoo),
            )
        )

    @property
    def is_umuriya(self) -> bool:
        return self.is_umuriya1 or self.is_umuriya2

    @property
    def is_mushtaraka(self) -> bool:
        if not self.lium.get("count"):
            return False
        return all(
            [
                self.zawj.get("count"),
                (self.umm.get("count") or self.jadda.get("count")),
                self.lium.get("count", 0) > 1,
                self.shaqiq.get("count"),
            ]
        ) and not (self.has_any_furoo or self.has_m_usool)

    @property
    def raas(self) -> int:
        """Calculate total shares (denominator) from all fard values.

        If _raas_override is set (by inkisaar), returns that instead.
        """
        if self._raas_override is not None:
            return self._raas_override

        def lcm(a: int, b: int) -> int: # @adam update to newer built in since 3.9
            from math import gcd

            return abs(a * b) // gcd(a, b) if a and b else (a or b)

        denominators = [
            heir.get("fard", frac(0)).denominator
            for heir in self._all_heirs
            if heir.get("fard") and heir.get("fard").denominator != 1
        ]

        if not denominators:
            return 1

        return reduce(lcm, denominators)

    @property
    def total_shares(self) -> int:
        """Calculate total shares allocated from all heirs' shares."""
        return sum(
            heir.get("shares", 0)
            for heir in self._all_heirs
            if isinstance(heir.get("shares"), int)
        )

    @property
    def total(self) -> float:
        """Calculate total portion as a fraction of raas."""
        if self.raas == 0:
            return 0.0
        return float(self.total_shares) / float(self.raas)

    @property
    def baqi(self) -> int:
        """Calculate remaining shares after allocation (raas - sum of shares)."""
        return self.raas - self.total_shares

    def to_dict(self) -> CaseDict:
        """Convert case to dictionary format."""
        result: CaseDict = {}
        for name, heir in zip(self._all_heir_names, self._all_heirs):
            if heir.get("count", 0):
                result[name] = heir.get("count", 0)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a Case from a dictionary.

        Useful for loading from CSV or JSON data.

        Args:
            data: Dictionary with family member counts.
                  Example: {'ibn': 2, 'bint': 1, 'zawja': True}

        Returns:
            Case instance
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

        # Define heirs that should be limited to a maximum count of 1
        single_person_heirs = {"umm", "ab", "jadd", "zawj", "zawja"}

        kwargs = {}
        for key, value in data.items():
            if key not in valid_fields:
                continue

            if isinstance(value, str):
                value = value.strip().lower()
                if value in ("true", "1", "yes"):
                    count = 1
                elif value in ("false", "0", "no", ""):
                    count = 0
                else:
                    try:
                        count = int(float(value))
                    except ValueError:
                        continue
            elif isinstance(value, bool):
                count = 1 if value else 0
            elif isinstance(value, (int, float)):
                count = int(value)
            else:
                continue

            # Apply constraint: certain heirs can never be more than 1
            if key in single_person_heirs and count > 1:
                count = 1

            kwargs[key] = {"count": count}

        return cls(**kwargs)


@dataclass
class InheritanceResult:  # depricated
    """Result of an inheritance calculation.

    Attributes:
        distribution: Dictionary of heir names to their decimal shares
        ending: How the distribution ended (ta'seeb, awl, radd, umuriya, mushtaraka)
        asib: The 'aasib (residual heir) if present
        total: Total portion accounted for
        status: Calculation status (Complete, Failed, Unknown)
        denominator: The total number of shares (raas) for this inheritance case
        numerators: Dict of heir names to their share numerator (heir -> numerator)
    """

    distribution: DistributionDict = field(default_factory=dict)
    ending: str | None = None
    asib: str | None = None
    total: float = 0.0
    status: str = "Unknown"
    denominator: int | None = None
    numerators: dict = field(default_factory=dict)

    def to_pretty_dict(self) -> dict[str, float]:
        """Convert from Arabic codified names to pretty-printed dictionary with English and human-readable names."""
        return {PRETTY_NAMES.get(k, k): v for k, v in self.distribution.items()}

    def get_member_fraction(
        self, member: str
    ) -> float | None:  # wrong change this to decimal @adam
        """Get the fraction for a specific family member."""
        return self.distribution.get(member)
