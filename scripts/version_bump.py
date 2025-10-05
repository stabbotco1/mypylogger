#!/usr/bin/env python3
"""Semantic version automation script for mypylogger.

Automatically increments version based on conventional commit messages:
- feat: minor version increment (0.1.0 -> 0.2.0)
- fix: patch version increment (0.1.0 -> 0.1.1)
- BREAKING CHANGE: major version increment (0.1.0 -> 1.0.0)

Updates version in pyproject.toml and mypylogger/__init__.py
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return match.group(1)


def parse_version(version: str) -> Tuple[int, int, int, str]:
    """Parse semantic version string into components."""
    # Handle pre-release versions like 0.1.0a2
    match = re.match(r"(\d+)\.(\d+)\.(\d+)(.*)$", version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")

    major, minor, patch, suffix = match.groups()
    return int(major), int(minor), int(patch), suffix


def format_version(major: int, minor: int, patch: int, suffix: str = "") -> str:
    """Format version components into string."""
    return f"{major}.{minor}.{patch}{suffix}"


def get_commit_messages_since_last_tag() -> List[str]:
    """Get commit messages since last tag."""
    try:
        # Get last tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        last_tag = result.stdout.strip()

        # Get commits since last tag
        result = subprocess.run(
            ["git", "log", f"{last_tag}..HEAD", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []

    except subprocess.CalledProcessError:
        # No tags exist, get all commits
        result = subprocess.run(
            ["git", "log", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []


def determine_version_increment(commit_messages: List[str]) -> str:
    """Determine version increment type from commit messages."""
    has_breaking = False
    has_feat = False
    has_fix = False

    for message in commit_messages:
        if (
            "BREAKING CHANGE" in message
            or message.startswith("feat!:")
            or message.startswith("fix!:")
        ):
            has_breaking = True
        elif message.startswith("feat:"):
            has_feat = True
        elif message.startswith("fix:"):
            has_fix = True

    if has_breaking:
        return "major"
    elif has_feat:
        return "minor"
    elif has_fix:
        return "patch"
    else:
        return "patch"  # Default to patch for any changes


def increment_version(version: str, increment_type: str) -> str:
    """Increment version based on type."""
    major, minor, patch, suffix = parse_version(version)

    # Remove pre-release suffix for releases
    suffix = ""

    if increment_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif increment_type == "minor":
        minor += 1
        patch = 0
    elif increment_type == "patch":
        patch += 1

    return format_version(major, minor, patch, suffix)


def update_pyproject_toml(new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    updated_content = re.sub(
        r'version = "[^"]+"', f'version = "{new_version}"', content
    )

    pyproject_path.write_text(updated_content)


def update_init_py(new_version: str) -> None:
    """Update version in mypylogger/__init__.py."""
    init_path = Path("mypylogger/__init__.py")
    content = init_path.read_text()

    updated_content = re.sub(
        r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content
    )

    init_path.write_text(updated_content)


def main() -> None:
    """Main version bump logic."""
    if len(sys.argv) > 1:
        # Manual increment type specified
        increment_type = sys.argv[1]
        if increment_type not in ["major", "minor", "patch"]:
            print(
                f"Error: Invalid increment type '{increment_type}'. Use major, minor, or patch."
            )
            sys.exit(1)
    else:
        # Automatic detection from commits
        commit_messages = get_commit_messages_since_last_tag()
        increment_type = determine_version_increment(commit_messages)

    current_version = get_current_version()
    new_version = increment_version(current_version, increment_type)

    print(f"Current version: {current_version}")
    print(f"Increment type: {increment_type}")
    print(f"New version: {new_version}")

    # Update files
    update_pyproject_toml(new_version)
    update_init_py(new_version)

    print(f"Version updated to {new_version}")
    print("Updated files: pyproject.toml, mypylogger/__init__.py")


if __name__ == "__main__":
    main()
