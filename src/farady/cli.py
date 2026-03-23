# Copyright (C) 2018-2026  Adam Ahmed
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from farady.classes import Case
from farady.pipelines import calculate_from_dict
from farady.pipelines import _build_distribution
from farady.processing import PRETTY_NAMES


def format_fraction(value: float) -> str:
    """Format a fractional value for display."""
    return f"{float(value):.4f}"


def format_percentage(value: float) -> str:
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

    debug_group = parser.add_argument_group("Debugging")
    debug_group.add_argument(
        "--debug",
        action="store_true",
        help="Show full debug output with complete Case object details",
    )

    return parser


def get_provided_members(args: argparse.Namespace) -> dict[str, int | bool]:
    """Extract family members that were provided (non-zero or True)."""
    provided: dict[str, int | bool] = {}

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


def print_results(
    result_case,
    provided_members: dict[str, int | bool],
    verbose: bool = False,
    debug: bool = False,
) -> None:
    """Print the inheritance distribution results."""

    # Debug mode: Show full Case object
    if debug:
        print("\n" + "=" * 60)
        print("         FULL DEBUG OUTPUT")
        print("=" * 60)
        print(f"Case object: {result_case}")
        print(f"Distribution card: {_build_distribution(result_case)}")
        print(f"Total shares: {result_case.total_shares}")
        print(f"Raas: {result_case.raas}")
        print(f"Total fraction: {result_case.total}")
        print(f"Ending: {result_case.ending}")
        print(f"Asib: {result_case.asib}")
        print(f"Status: {result_case.status}")
        print()
        return

    # Standard output
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

    # Build distribution
    distribution = _build_distribution(result_case)

    print("\n" + "-" * 60)
    print(f"{'Beneficiary':<35} {'Share':>10} {'Percentage':>12}")
    print("-" * 60)

    sorted_dist = sorted(distribution.items(), key=lambda x: float(x[1]), reverse=True)

    raas = result_case.raas
    for member, share in sorted_dist:
        pretty_name = PRETTY_NAMES.get(member, member)
        frac_str = str(share)
        pct_str = format_percentage(float(share) / float(raas) if raas > 0 else 0.0)
        print(f"{pretty_name:<35} {frac_str:>10} {pct_str:>12}")

    print("-" * 60)
    total_shares = result_case.total_shares
    total_fraction = result_case.total
    print(f"{'Total':<35} {total_shares:>10} {format_percentage(total_fraction):>12}")
    print("=" * 60)

    # Verbose mode: Show additional calculation details
    if verbose:
        print(f"\nDistribution Method: {result_case.ending or 'Standard'}")
        if result_case.asib:
            print(
                f"Residual Heir (Asib): {PRETTY_NAMES.get(result_case.asib, result_case.asib)}"
            )
        print(f"Status: {result_case.status}")

    print()


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    provided_members = get_provided_members(args)

    if not provided_members:
        parser.print_help()
        print("\nError: At least one family member must be specified.")
        return 1

    # Create case and calculate
    result_case = calculate_from_dict(provided_members)

    print_results(result_case, provided_members, args.verbose, args.debug)

    if result_case.status != "Complete":
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
