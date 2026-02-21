#!/usr/bin/env python3
"""Version management utility for Farady.

Usage:
    python scripts/version.py bump <component>
    python scripts/version.py current
    python scripts/version.py tag

Components: major, minor, patch, sa
"""

import re
import subprocess
import sys
from pathlib import Path


INIT_FILE = Path("src/farady/__init__.py")
PYPROJECT_FILE = Path("pyproject.toml")


def get_current_version() -> str:
    content = INIT_FILE.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find __version__ in __init__.py")
    return match.group(1)


def parse_version(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump_version(component: str) -> str:
    current = get_current_version()
    major, minor, patch = parse_version(current)

    if component == "major":
        major += 1
        minor = 0
        patch = 0
    elif component == "minor":
        minor += 1
        patch = 0
    elif component == "patch":
        patch += 1
    else:
        raise ValueError(f"Unknown component: {component}")

    new_version = f"{major}.{minor}.{patch}"
    return new_version


def update_version_files(new_version: str) -> None:
    init_content = INIT_FILE.read_text()
    new_init = re.sub(
        r'__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        init_content,
    )
    INIT_FILE.write_text(new_init)

    pyproject_content = PYPROJECT_FILE.read_text()
    new_pyproject = re.sub(
        r'version\s*=\s*["\'][^"\']+["\']',
        f'version = "{new_version}"',
        pyproject_content,
    )
    PYPROJECT_FILE.write_text(new_pyproject)

    print(f"Updated version to {new_version} in __init__.py and pyproject.toml")


def get_latest_sa_tag() -> str | None:
    result = subprocess.run(
        ["git", "tag", "-l", "v*-sa.*"],
        capture_output=True,
        text=True,
    )
    tags = result.stdout.strip().split("\n")
    tags = [t for t in tags if t]
    if not tags:
        return None
    return sorted(tags, key=lambda t: [int(x) for x in re.findall(r"\d+", t)])[-1]


def create_sa_tag() -> str:
    current_version = get_current_version()
    latest_tag = get_latest_sa_tag()

    if latest_tag:
        match = re.search(r"-sa\.(\d+)$", latest_tag)
        if match and latest_tag.startswith(f"v{current_version}-sa"):
            last_num = int(match.group(1))
            new_num = last_num + 1
        else:
            new_num = 1
    else:
        new_num = 1

    new_tag = f"v{current_version}-sa.{new_num}"
    return new_tag


def create_tag(tag: str) -> None:
    subprocess.run(["git", "tag", "-a", tag, "-m", f"Release {tag}"], check=True)
    print(f"Created tag: {tag}")


def push_tag(tag: str) -> None:
    subprocess.run(["git", "push", "origin", tag], check=True)
    print(f"Pushed tag: {tag}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "current":
        print(get_current_version())
    elif command == "bump":
        if len(sys.argv) < 3:
            print("Usage: python scripts/version.py bump <component>")
            print("Components: major, minor, patch")
            sys.exit(1)
        component = sys.argv[2]
        if component == "sa":
            print("Use 'tag' command for SA releases")
            sys.exit(1)
        new_version = bump_version(component)
        update_version_files(new_version)
    elif command == "tag":
        new_tag = create_sa_tag()
        create_tag(new_tag)
        if "--push" in sys.argv:
            push_tag(new_tag)
        else:
            print(f"Tag created: {new_tag}")
            print("Run with --push to push to remote")
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
