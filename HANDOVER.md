# Farady Refactor Handover

## Context

Farady is an Islamic Inheritance Calculator. A deep refactor replaced the old dict-based architecture with a `Case` dataclass. This broke some functionality which has been partially fixed.

**Critical:** User (Adam) is the SME for Islamic inheritance law. Defer to him on all fiqh questions. Never assert domain correctness in tests.

---

## Architecture

### Old (distribution_v1.py)
- `new` dict for input, `finish` dict for output
- Stored fractions directly

### New
- `Case` dataclass with `HeirData` TypedDict per heir
- Fields: `count`, `fard` (Fraction), `shares` (int), `asib` (bool), `mahjub` (bool)
- Computed properties auto-calculate on read

### Key Concepts
| Term | Meaning |
|------|---------|
| `fard` | Fixed share as Fraction (e.g., 1/4) |
| `shares` | Integer representation after LCM conversion |
| `raas` | LCM of all fard denominators (total shares in estate) |
| `baqi` | Remaining shares: `raas - sum(shares)` |
| `asib` | Residual heir who receives baqi |
| `taseeb` | Process of distributing baqi to asibs |
| `heads` | Weighted count for lizakari scenarios (male=2, female=1) |
| `inkisaar` | Adjustment when baqi not divisible by heads |
| `awl` | Reduction when fard shares exceed raas |
| `radd` | Return of excess to non-spouse fard holders |
| `lizakari` | Male gets 2x female share in mixed asib scenarios |

### Calculation Pipeline
```
Input → zawjayn_step → usool_step → furoo_step → hawashi_step → kalala_step
      → convert_fard_to_shares → awl_step OR (taseeb_step + inkisaar) OR radd_step
      → Output
```

---

## What Works

- `Case` class with computed properties (raas, baqi, total, is_mushtaraka, heads)
- `convert_fard_to_shares()` - converts fard fractions to integer shares
- `taseeb_step()` - distributes baqi to asibs with lizakari logic
- `inkisaar()` - adjusts raas when baqi not divisible by heads
- `radd_step()` - returns excess to non-spouse fard holders
- `_compute_heads()` - returns 1 for single-type asibs, weighted for mixed
- Fallback asib assignment (amm, ibnamm_sh, ibnamm_liab) in hawashi_step

### Verified Test Cases
- `ibn=1, bint=1, zawja=True` → inkisaar (raas 8→24), ibn:14, bint:7, zawja:3
- `bint=1, zawja=True` → radd, daughter:7/8, wife:1/8
- `bint=1, zawj=True, amm=1` → amm as asib gets 1/4 baqi
- `bint=1, zawj=True, shaqiqa=1` → shaqiqa as female asib gets baqi

---

## What's Broken

1. **CLI** (`src/farady/cli.py`) - imports non-existent `farady.distribution`
2. **Tests** (`tests/test_generic.py`) - imports old `InheritanceCase`, `InheritanceCalculator`
3. **`_build_distribution()`** - not yet implemented/fixed
4. **`distribution` property** - not added to Case class

---

## Pending Work

1. Split `calculation_functions.py` into allocation vs rebalancing modules
2. Fix `_build_distribution()` to produce final output
3. Add `distribution` property to Case class
4. Fix CLI imports
5. Fix test imports
6. Test edge case: "asib waiting but no shares left"

---

## Key Files

| File | Purpose |
|------|---------|
| `src/farady/classes.py` | Case dataclass, HeirData TypedDict, computed properties |
| `src/farady/calculation_functions.py` | FP calculation steps |
| `src/farady/run_pipeline.py` | Main calculate() function |
| `src/farady/distribution_v1.py` | Old implementation (reference only) |

---

## Development Notes

- Use FP style for calculation steps (pure functions: Case → Case)
- Keep computed properties on Case class
- Work on main branch
- Don't run tests without user direction
- User will provide test scenarios
