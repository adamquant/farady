# Copyright (C) 2024  Adam Ahmed / SunnaAssets
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
"""Shared fixtures and utilities for monte carlo tests.

This module provides:
- Test case loading from disk
- Result computation and caching (via lru_cache)
- Failure collection helpers
- Pytest session logging
"""

import functools
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from farady import calculate_from_dict
from farady.run_pipeline import _build_distribution

CATEGORIES = ("ordinary", "no_fare", "hawashi")

MONTE_TESTS = [
    ("test_total_always_one", lambda r: round(r["total"], 2) != 1.0),
    ("test_status_is_complete", lambda r: r["status"] != "Complete"),
]


def _get_version() -> str:
    try:
        from farady import __version__

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )
            commit = result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            commit = "unknown"
        return f"{__version__}+g{commit}"
    except Exception:
        return "0.0.0+unknown"


def pytest_sessionstart(session):
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"pytest_{datetime.now().strftime('%Y%m%d')}.log"
    version = _get_version()
    header = f"{'=' * 60}\nPYTEST SESSION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nVERSION: {version}\n{'=' * 60}\n"
    with open(log_file, "a") as f:
        f.write(header)


def pytest_sessionfinish(session, exitstatus):
    log_dir = Path(__file__).parent.parent / "logs"
    log_file = log_dir / f"pytest_{datetime.now().strftime('%Y%m%d')}.log"
    if log_file.exists():
        summary = f"{'=' * 60}\nSUMMARY: {exitstatus}\n{'=' * 60}\n"
        with open(log_file, "a") as f:
            f.write(summary)


def _resolve_test_cases_path() -> "Path | None":
    candidates = [
        Path(__file__).parent / "data" / "test_cases.npz",
        Path(__file__).parent / "data" / "monte" / "test_cases.npz",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    matches = list(Path(__file__).parent.rglob("test_cases.npz"))
    return matches[0] if matches else None


def load_test_cases() -> dict[str, list]:
    data_path = _resolve_test_cases_path()
    if data_path is None:
        pytest.skip("test_cases.npz not found")
    data = np.load(data_path, allow_pickle=True)
    return {cat: list(data[cat]) for cat in CATEGORIES}


def case_to_result(case) -> dict:
    result = _build_distribution(case)
    numerators = {
        name: int(heir.get("shares", 0))
        for name, heir in zip(case._all_heir_names, case._all_heirs)
        if heir.get("shares")
    }
    total = sum(item["fraction"] for item in result.values()) if result else 0
    return {
        "distribution": result,
        "ending": case.ending,
        "asib": case.asib,
        "total": total,
        "status": case.status,
        "denominator": case.raas,
        "numerators": numerators,
    }


@functools.lru_cache(maxsize=1)
def get_results() -> dict:
    cases = load_test_cases()
    # Default to 1000 cases for faster iteration, but allow customization
    limit = int(os.environ.get("FARADY_MONTE_LIMIT", "1000"))
    if limit <= 0:
        return {cat: [] for cat in CATEGORIES}
    return {
        cat: [(c, case_to_result(calculate_from_dict(c))) for c in cases[cat][:limit]]
        for cat in CATEGORIES
    }


def collect_failures(results: dict, predicate) -> dict[str, list[dict]]:
    return {
        cat: [
            {"index": i, "case": c, "result": r}
            for i, (c, r) in enumerate(results[cat])
            if predicate(r)
        ]
        for cat in CATEGORIES
    }


def save_failures(
    failures: dict, test_name: str, timestamp: "str | None" = None
) -> "Path | None":
    if not failures:
        return None
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"failures_{test_name}_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(failures, f, indent=2)
    return output_file


def run_test(test_name: str, results: dict, predicate, description: str) -> dict:
    failures = collect_failures(results, predicate)
    if failures:
        save_failures(failures, test_name, datetime.now().strftime("%Y%m%d_%H%M%S"))
    if any(failures[cat] for cat in CATEGORIES):
        parts = [
            f"{cat}: {len(failures[cat])} failures"
            for cat in CATEGORIES
            if failures[cat]
        ]
        raise AssertionError(f"{test_name}: {', '.join(parts)}")
    return failures
