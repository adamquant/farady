PRETTY_NAMES: dict[HeirKey, str] = {
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

HEIR_FIELDS = {
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

BOOLEAN_HEIRS = {"zawj", "zawja"}

COUNT_HEIRS = HEIR_FIELDS - BOOLEAN_HEIRS

def load_csv_cases(csv_path: str) -> list:
    """Load inheritance cases from a CSV file.

    Each row in the CSV should have column headers matching valid family
    member names. Values can be integers, or strings like 'True', '1', 'yes'.

    Args:
        csv_path: Path to CSV file

    Returns:
        List of Case objects

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
            case = Case.from_dict(row)
            cases.append(case)

    return cases


def process_csv_results(csv_path: str) -> list:
    """Load CSV and calculate results for each case.

    Returns a list of dicts with both the input data and calculated results.

    Args:
        csv_path: Path to CSV file

    Returns:
        List of dicts with keys: 'case' (Case),
        'result' (InheritanceResult), 'row_data' (original dict)
    """
    import csv

    results = []
    calculator = InheritanceCalculator()

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case = Case.from_dict(row)
            result = calculator.calculate(case)
            results.append({"case": case, "result": result, "row_data": row})

    return results