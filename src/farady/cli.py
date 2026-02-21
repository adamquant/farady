"""Farady CLI - Command-line interface for Islamic Inheritance Calculator.

Usage:
    farady --ibn 2 --bint 1 --umm 1 --zawja
    farady --son 2 --daughter 1 --mother --wife
    farady --help

Family Member Arguments:
    These arguments specify the number (or presence) of each family member.
    Integer arguments (0 or positive) represent count, boolean flags represent presence.

    --ibn, --son           Number of sons
    --bint, --daughter    Number of daughters
    --iibn, --grandson    Number of grandsons (son's son)
    --bibn, --granddaughter Number of granddaughters (son's daughter)
    --iiibn, --great-grandson   Number of great-grandsons
    --biibn, --great-granddaughter Number of great-granddaughters
    --umm, --mother        Mother (0 or 1)
    --jadda, --grandmother Grandmother(s) (0 or 1)
    --ab, --father         Father (0 or 1)
    --jadd, --grandfather  Grandfather (0 or 1)
    --lium, --maternal-half-sibling  Maternal half-sibling(s) count
    --shaqiqa, --full-sister   Full sister(s) count
    --shaqiq, --full-brother    Full brother(s) count
    --uliab, --paternal-half-sister  Paternal half-sister(s) count
    --aliab, --paternal-half-brother Paternal half-brother(s) count
    --ibnamm-sh, --full-nephew     Full nephew (brother's son) count
    --ibnamm-liab, --half-nephew    Half nephew (half-brother's son) count
    --amm, --uncle          Uncle (father's brother) count
    --zawj, --husband       Husband present
    --zawja, --wife         Wife present

Examples:
    # Deceased has 2 sons, 1 daughter, and a wife
    farady --ibn 2 --bint 1 --zawja

    # Deceased has only a mother and wife (no descendants)
    farady --umm 1 --zawj

    # Complex case with multiple family members
    farady --ibn 1 --bint 2 --ab 1 --umm 1 --zawja
"""

import argparse
import sys
from typing import Union, Dict, Any

from farady.distribution import InheritanceCase, InheritanceCalculator, PRETTY_NAMES


def format_fraction(value: Union[float, Any]) -> str:
    """Format a fractional value for display."""
    if hasattr(value, "numerator"):
        return f"{float(value):.4f}"
    return f"{float(value):.4f}"


def format_percentage(value: Union[float, Any]) -> str:
    """Format a value as a percentage."""
    return f"{float(value) * 100:.2f}%"


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all family member options."""

    parser = argparse.ArgumentParser(
        prog="farady",
        description="Islamic Inheritance Distribution Calculator (Faraid)",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    descendants_group = parser.add_argument_group("Descendants (Furoo)")
    descendants_group.add_argument(
        "--ibn", "--son", "-s", type=int, default=0, metavar="N", help="Number of sons"
    )
    descendants_group.add_argument(
        "--bint",
        "--daughter",
        "-d",
        type=int,
        default=0,
        metavar="N",
        help="Number of daughters",
    )
    descendants_group.add_argument(
        "--iibn",
        "--grandson",
        type=int,
        default=0,
        metavar="N",
        help="Number of grandsons (son of son)",
    )
    descendants_group.add_argument(
        "--bibn",
        "--granddaughter",
        type=int,
        default=0,
        metavar="N",
        help="Number of granddaughters (daughter of son)",
    )
    descendants_group.add_argument(
        "--iiibn",
        "--great-grandson",
        type=int,
        default=0,
        metavar="N",
        help="Number of great-grandsons",
    )
    descendants_group.add_argument(
        "--biibn",
        "--great-granddaughter",
        type=int,
        default=0,
        metavar="N",
        help="Number of great-granddaughters",
    )

    parents_group = parser.add_argument_group("Parents (Usool)")
    parents_group.add_argument(
        "--umm",
        "--mother",
        "-m",
        type=int,
        default=0,
        metavar="N",
        help="Mother (0 or 1)",
    )
    parents_group.add_argument(
        "--jadda",
        "--grandmother",
        "-g",
        type=int,
        default=0,
        metavar="N",
        help="Grandmother(s) (0 or 1)",
    )
    parents_group.add_argument(
        "--ab",
        "--father",
        "-f",
        type=int,
        default=0,
        metavar="N",
        help="Father (0 or 1)",
    )
    parents_group.add_argument(
        "--jadd",
        "--grandfather",
        type=int,
        default=0,
        metavar="N",
        help="Grandfather (nearest in relation)",
    )

    siblings_group = parser.add_argument_group("Siblings and Relatives (Hawashi)")
    siblings_group.add_argument(
        "--lium",
        "--maternal-half-sibling",
        type=int,
        default=0,
        metavar="N",
        help="Maternal half-sibling(s) count",
    )
    siblings_group.add_argument(
        "--shaqiqa",
        "--full-sister",
        type=int,
        default=0,
        metavar="N",
        help="Full sister(s) count",
    )
    siblings_group.add_argument(
        "--shaqiq",
        "--full-brother",
        type=int,
        default=0,
        metavar="N",
        help="Full brother(s) count",
    )
    siblings_group.add_argument(
        "--uliab",
        "--paternal-half-sister",
        type=int,
        default=0,
        metavar="N",
        help="Paternal half-sister(s) count",
    )
    siblings_group.add_argument(
        "--aliab",
        "--paternal-half-brother",
        type=int,
        default=0,
        metavar="N",
        help="Paternal half-brother(s) count",
    )
    siblings_group.add_argument(
        "--ibnamm-sh",
        "--full-nephew",
        type=int,
        default=0,
        metavar="N",
        help="Full nephew (brother's son) count",
    )
    siblings_group.add_argument(
        "--ibnamm-liab",
        "--half-nephew",
        type=int,
        default=0,
        metavar="N",
        help="Half nephew (half-brother's son) count",
    )
    siblings_group.add_argument(
        "--amm",
        "--uncle",
        type=int,
        default=0,
        metavar="N",
        help="Uncle (brother of father) count",
    )

    spouses_group = parser.add_argument_group("Spouses")
    spouses_group.add_argument(
        "--zawj", "--husband", action="store_true", help="Husband present"
    )
    spouses_group.add_argument(
        "--zawja", "--wife", action="store_true", help="Wife present"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show verbose output with calculation details",
    )

    return parser


def get_provided_members(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract family members that were provided (non-zero or True)."""
    provided = {}

    mappings = {
        "ibn": "ibn",
        "bint": "bint",
        "iibn": "iibn",
        "bibn": "bibn",
        "iiibn": "iiibn",
        "biibn": "biibn",
        "umm": "umm",
        "jadda": "jadda",
        "ab": "ab",
        "jadd": "jadd",
        "lium": "lium",
        "shaqiqa": "shaqiqa",
        "shaqiq": "shaqiq",
        "uliab": "uliab",
        "aliab": "aliab",
        "ibnamm_sh": "ibnamm_sh",
        "ibnamm_liab": "ibnamm_liab",
        "amm": "amm",
    }

    for arg_name, member_name in mappings.items():
        value = getattr(args, arg_name, 0)
        if value > 0:
            provided[member_name] = value

    if getattr(args, "zawj", False):
        provided["zawj"] = True

    if getattr(args, "zawja", False):
        provided["zawja"] = True

    return provided


def print_results(result, provided_members: Dict[str, Any], verbose: bool = False):
    """Print the inheritance distribution results as a table."""

    print("\n" + "=" * 60)
    print("         ISLAMIC INHERITANCE DISTRIBUTION")
    print("=" * 60)

    if provided_members:
        print("\nFamily Members Provided:")
        print("-" * 40)
        for member, value in sorted(provided_members.items()):
            pretty_name = PRETTY_NAMES.get(member, member)
            if isinstance(value, bool):
                print(f"  {pretty_name}: {'Yes' if value else 'No'}")
            else:
                print(f"  {pretty_name}: {value}")

    print("\n" + "-" * 60)
    print(f"{'Beneficiary':<35} {'Share':>10} {'Percentage':>12}")
    print("-" * 60)

    sorted_dist = sorted(
        result.distribution.items(), key=lambda x: float(x[1]), reverse=True
    )

    for member, share in sorted_dist:
        pretty_name = PRETTY_NAMES.get(member, member)
        frac_str = format_fraction(share)
        pct_str = format_percentage(share)
        print(f"{pretty_name:<35} {frac_str:>10} {pct_str:>12}")

    print("-" * 60)
    print(
        f"{'Total':<35} {format_fraction(result.total):>10} {format_percentage(result.total):>12}"
    )
    print("=" * 60)

    if verbose or result.ending:
        print(f"\nDistribution Method: {result.ending or 'Standard'}")
        if result.asib:
            print(f"Residual Heir (Asib): {PRETTY_NAMES.get(result.asib, result.asib)}")
        print(f"Status: {result.status}")

    print()


def main(argv=None):
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    provided_members = get_provided_members(args)

    if not provided_members:
        parser.print_help()
        print("\nError: At least one family member must be specified.")
        return 1

    case = InheritanceCase(**provided_members)
    calculator = InheritanceCalculator()
    result = calculator.calculate(case)

    print_results(result, provided_members, args.verbose)

    if result.status != "Complete":
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
