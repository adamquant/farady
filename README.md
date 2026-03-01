# Farady - Islamic Inheritance Distribution Calculator

[![License: AGPLv3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![CI](https://github.com/adamquant/farady-dev/actions/workflows/ci.yml/badge.svg)](https://github.com/adamquant/farady-dev/actions/workflows/ci.yml)
[![Coverage](https://github.com/adamquant/farady-dev/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/adamquant/farady-dev/actions/workflows/ci.yml)
[![Pytest](https://img.shields.io/badge/pytest-passing-success)](https://github.com/adamquant/farady-dev/actions/workflows/ci.yml)

A Python library and CLI tool for calculating Islamic inheritance distribution according to Faraid (Islamic inheritance law).

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Core Classes](#core-classes)
  - [Main Functions](#main-functions)
  - [CSV/Batch Processing](#csvbatch-processing)
- [Case Fields](#case-fields)
- [CLI Usage](#cli-usage)
- [Examples](#examples)

---

## Installation

```bash
pip install farady
```

Development mode:

```bash
pip install -e .
```

---

## Quick Start

```python
from farady import calculate_from_dict

# Simple case: 1 son, 1 daughter, wife
case = calculate_from_dict({"ibn": 1, "bint": 1, "zawja": True})

# Access results
print(case.distribution)   # {'zawja': 0.125, 'ibn': 0.5833, 'bint': 0.2917}
print(case.ending)         # 'taseeb'
print(case.total)          # 1.0
print(case.status)         # 'Complete'
print(case.asib)           # 'ibn-bint'
```

---

## API Reference

### Core Classes

#### `Case`

Data class representing a family configuration for inheritance calculation.

```python
from farady import Case

case = Case.from_dict({
    "ibn": 2,        # 2 sons
    "bint": 1,       # 1 daughter
    "zawja": True,   # Wife present
    "umm": 1,        # Mother present
    "ab": 1,         # Father present
})
```

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `distribution` | `dict` | Heir -> share mapping |
| `ending` | `str` | Distribution method used |
| `asib` | `str` | Residual heir (if any) |
| `total` | `float` | Total of all shares |
| `status` | `str` | Calculation status |
| `raas` | `int` | Total shares (denominator) |
| `total_shares` | `int` | Sum of all allocated shares |

**Class Methods:**

| Method | Description |
|--------|-------------|
| `Case.from_dict(data)` | Create from dictionary (handles string conversion) |
| `case.to_dict()` | Convert to dictionary (excludes zero/false values) |

---

### Main Functions

#### `calculate(case)`

Main function to calculate inheritance distribution.

```python
from farady import Case, calculate

case = Case.from_dict({"ibn": 2, "bint": 1, "zawja": True})
result = calculate(case)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `case` | `Case` | Case object with family member counts |

**Returns:** `Case` with populated results

#### `calculate_from_dict(data)`

Calculate inheritance from a dictionary. Useful for loading from JSON, CSV, or form data.

```python
from farady import calculate_from_dict

# From a dictionary
data = {"ibn": "2", "bint": "1", "zawja": "True"}  # Strings are converted
case = calculate_from_dict(data)

# From form data with mixed types
data = {"ibn": 1, "bint": 2, "zawja": True, "umm": "1"}
case = calculate_from_dict(data)
```

**String Conversion Rules:**

| Field Type | String Value | Converted To |
|------------|--------------|--------------|
| Spouse (`zawj`, `zawja`) | `"True"`, `"1"`, `"yes"` | `True` |
| Spouse (`zawj`, `zawja`) | `"False"`, `"0"`, `"no"`, `""` | `False` |
| Count fields | `"1"`, `"2"`, etc. | `int` |
| Count fields | `"True"`, `"yes"` | `1` |
| Count fields | `"False"`, `"no"`, `""` | (excluded) |

**Returns:** `Case` with populated results

#### `calculate_inheritance(**kwargs)`

Calculate inheritance directly from keyword arguments.

```python
from farady import calculate_inheritance

case = calculate_inheritance(ibn=2, bint=1, zawja=True)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ibn` | `int` | Number of sons |
| `bint` | `int` | Number of daughters |
| `iibn` | `int` | Number of grandsons |
| `bibn` | `int` | Number of granddaughters |
| `iiibn` | `int` | Number of great-grandsons |
| `biibn` | `int` | Number of great-granddaughters |
| `umm` | `int` | Mother (0 or 1) |
| `jadda` | `int` | Grandmother(s) (0 or 1) |
| `ab` | `int` | Father (0 or 1) |
| `jadd` | `int` | Grandfather (0 or 1) |
| `lium` | `int` | Maternal half-sibling count |
| `shaqiqa` | `int` | Full sister count |
| `shaqiq` | `int` | Full brother count |
| `uliab` | `int` | Paternal half-sister count |
| `aliab` | `int` | Paternal half-brother count |
| `ibnamm_sh` | `int` | Full nephew count |
| `ibnamm_liab` | `int` | Half nephew count |
| `amm` | `int` | Uncle count |
| `zawj` | `bool` | Husband present |
| `zawja` | `bool` | Wife present |

**Returns:** `Case` with populated results

---

### CSV/Batch Processing

#### `load_csv_cases(csv_path)`

Load inheritance cases from a CSV file.

```python
from farady import load_csv_cases

cases = load_csv_cases("tests/test_cases.csv")
# Returns: List[Case]

for case in cases:
    print(case.to_dict())
```

**CSV Format:**

```csv
ibn,bint,zawja,expected_total,notes
1,1,True,1.0,Son + daughter + wife
2,0,True,1.0,Two sons + wife
0,2,True,1.125,Two daughters + wife (awl)
```

- Column headers must match valid field names (Arabic: `ibn`, `bint`, `zawja`, etc.)
- Extra columns (like `notes`, `expected_total`) are ignored
- String values are converted using same rules as `from_dict()`

**Returns:** `List[Case]`

#### `process_csv_results(csv_path)`

Load CSV and calculate results for each row. Returns full context for testing/debugging.

```python
from farady import process_csv_results

results = process_csv_results("tests/test_cases.csv")

for item in results:
    row = item["row_data"]       # Original CSV row (dict)
    case = item["case"]          # Case object (before calculation)
    result = item["result"]      # Case object (after calculation)
    
    print(f"Case: {row.get('notes')}")
    print(f"  Distribution: {result.distribution}")
    print(f"  Ending: {result.ending}")
    print(f"  Total: {result.total}")
    print(f"  Status: {result.status}")
```

**Returns:** `List[Dict]` with keys:

| Key | Type | Description |
|-----|------|-------------|
| `row_data` | `dict` | Original CSV row data |
| `case` | `Case` | Parsed case object |
| `result` | `Case` | Calculated result case |

---

## Case Fields

### Family Member Fields (Arabic Names)

| Field | Type | Description | Fixed Share |
|-------|------|-------------|-------------|
| `ibn` | `int` | Sons | Variable (asib) |
| `bint` | `int` | Daughters | 1/2 (single), 2/3 (multiple), or variable |
| `iibn` | `int` | Grandsons (son's sons) | Variable |
| `bibn` | `int` | Granddaughters (son's daughters) | Variable |
| `iiibn` | `int` | Great-grandsons | Variable |
| `biibn` | `int` | Great-granddaughters | Variable |
| `umm` | `int` | Mother | 1/6 (with children) or 1/3 |
| `jadda` | `int` | Grandmother(s) | 1/6 (if mother absent) |
| `ab` | `int` | Father | 1/6 (with children) or variable |
| `jadd` | `int` | Grandfather | Variable |
| `lium` | `int` | Maternal half-siblings | 1/3 (collectively) |
| `shaqiqa` | `int` | Full sisters | Variable |
| `shaqiq` | `int` | Full brothers | Variable (asib) |
| `uliab` | `int` | Paternal half-sisters | Variable |
| `aliab` | `int` | Paternal half-brothers | Variable |
| `ibnamm_sh` | `int` | Full nephews | Variable |
| `ibnamm_liab` | `int` | Half nephews | Variable |
| `amm` | `int` | Uncles | Variable |
| `zawj` | `bool` | Husband | 1/2 (no kids) or 1/4 |
| `zawja` | `bool` | Wife | 1/4 (no kids) or 1/8 |

### Pretty Names Reference

```python
from farady import PRETTY_NAMES

PRETTY_NAMES = {
    'ibn': 'Son(s)',
    'bint': 'Daughter(s)',
    'iibn': 'Grandson(s)',
    'bibn': 'Granddaughter(s)',
    'iiibn': 'Great-grandson(s)',
    'biibn': 'Great-granddaughter(s)',
    'umm': 'Mother',
    'jadda': 'Grandmother(s)',
    'ab': 'Father',
    'jadd': 'Grandfather (nearest in relation)',
    'lium': 'Maternal Half-sibling(s)',
    'shaqiqa': 'Full Sister(s)',
    'shaqiq': 'Full Brother(s)',
    'uliab': 'Paternal Half-sister(s)',
    'aliab': 'Paternal Half-brother(s)',
    'ibnamm_sh': 'Full Nephew',
    'ibnamm_liab': 'Half Nephew',
    'amm': 'Uncle',
    'zawj': 'Husband',
    'zawja': 'Wife',
}
```

---

## CLI Usage

```bash
# Basic usage
farady --ibn 2 --bint 1 --zawja

# Verbose output (shows ending, asib, status)
farady --ibn 2 --bint 1 --zawja --verbose

# All flags
farady --ibn 1 --bint 2 --iibn 0 --bibn 0 --umm 1 --ab 1 --zawja
```

---

## Examples

### Example 1: Basic Case

```python
from farady import calculate_from_dict

case = calculate_from_dict({"ibn": 1, "bint": 1, "zawja": True})

print(f"Distribution: {case.distribution}")
# Distribution: {'zawja': 0.125, 'ibn': 0.5833, 'bint': 0.2917}

print(f"Ending: {case.ending}")
# Ending: taseeb

print(f"Raas: {case.raas}")
# Raas: 24

# For document generation:
# "Divide into 24 shares: 3 to Wife, 14 to Son(s), 7 to Daughter(s)"
```

### Example 2: Awl Case (Shares Exceed 1)

```python
case = calculate_from_dict({"bint": 2, "zawja": True})

print(f"Total: {case.total}")       # 1.125 (exceeds 1)
print(f"Ending: {case.ending}")     # awl
```

### Example 3: Radd Case (Leftover After Fixed Shares)

```python
case = calculate_from_dict({"bint": 2})

print(f"Distribution: {case.distribution}")  # {'bint': 1.0}
print(f"Total: {case.total}")                # 1.0
print(f"Ending: {case.ending}")              # radd
# Two daughters: 2/3 fixed, remaining 1/3 returned via radd
```

### Example 4: CSV Batch Processing

```python
from farady import process_csv_results

results = process_csv_results("test_cases.csv")

for item in results:
    row = item["row_data"]
    result = item["result"]
    
    # Debug output
    print(f"Case: {row.get('case_name', 'unnamed')}")
    print(f"  Ending method: {result.ending}")
    print(f"  Total: {result.total}")
    print(f"  Status: {result.status}")
    if result.asib:
        print(f"  Residual heir: {result.asib}")
    print()
```

### Example 5: Form Data Integration

```python
from farady import calculate_from_dict

# From web form (strings)
form_data = {
    "ibn": "2",
    "bint": "1",
    "zawja": "yes",  # Will be converted to True
    "umm": "1",
}

case = calculate_from_dict(form_data)

# Use raas for will document
if case.raas:
    shares_text = []
    for heir, share in case.distribution.items():
        num_shares = round(share * case.raas)
        shares_text.append(f"{num_shares} shares to {heir}")
    
    print(f"Divide into {case.raas} shares:")
    print("\n".join(shares_text))
```

---

## License

**GNU Affero General Public License v3.0 (AGPLv3)**

This software is licensed under AGPLv3. See the [LICENSE](LICENSE) file for the full text.

### Key Points of AGPLv3

- **Commercial Use Allowed**: You may use this software for commercial purposes
- **Source Required**: If you modify this software and run it as a network service, you must make your modifications available to users
- **Share Alike**: If you distribute modified versions, they must be licensed under AGPLv3
- **Attribution**: You must give appropriate credit to Adam Ahmed

### Enterprise & Commercial Use

AGPLv3 is a strong copyleft license. If you:
- Use it as-is: No restrictions
- Host it as a service: You must provide source code to users
- Modify it: Must distribute your modifications under AGPLv3

For traditional commercial licensing (to avoid copyleft obligations), please contact the author.
## PyPI Release Test
This is a test entry for verifying the PyPI release workflow.

Another test line
