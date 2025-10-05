#!/usr/bin/env python3
"""Generate changelog entries from conventional commits."""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def get_commits_since_last_tag() -> List[Tuple[str, str]]:
    """Get commits since last tag with hash and message."""
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
            ["git", "log", f"{last_tag}..HEAD", "--pretty=format:%h|%s"],
            capture_output=True,
            text=True,
            check=True,
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                hash_part, message = line.split("|", 1)
                commits.append((hash_part, message))
        return commits

    except subprocess.CalledProcessError:
        # No tags exist, get recent commits
        result = subprocess.run(
            ["git", "log", "--pretty=format:%h|%s", "-10"],
            capture_output=True,
            text=True,
            check=True,
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                hash_part, message = line.split("|", 1)
                commits.append((hash_part, message))
        return commits


def categorize_commits(
    commits: List[Tuple[str, str]],
) -> Dict[str, List[Tuple[str, str]]]:
    """Categorize commits by type."""
    categories: Dict[str, List[Tuple[str, str]]] = {
        "Breaking Changes": [],
        "Features": [],
        "Bug Fixes": [],
        "Documentation": [],
        "Other": [],
    }

    for commit_hash, message in commits:
        if "BREAKING CHANGE" in message or message.startswith(("feat!:", "fix!:")):
            categories["Breaking Changes"].append((commit_hash, message))
        elif message.startswith("feat:"):
            categories["Features"].append((commit_hash, message))
        elif message.startswith("fix:"):
            categories["Bug Fixes"].append((commit_hash, message))
        elif message.startswith("docs:"):
            categories["Documentation"].append((commit_hash, message))
        else:
            categories["Other"].append((commit_hash, message))

    return categories


def format_changelog_entry(
    version: str, categories: Dict[str, List[Tuple[str, str]]]
) -> str:
    """Format changelog entry for version."""
    date = datetime.now().strftime("%Y-%m-%d")
    entry = f"## [{version}] - {date}\n\n"

    for category, commits in categories.items():
        if commits:
            entry += f"### {category}\n\n"
            for commit_hash, message in commits:
                # Clean up commit message
                clean_message = re.sub(
                    r"^(feat|fix|docs|test|refactor|style|perf|chore)(!?):\s*",
                    "",
                    message,
                )
                entry += f"- {clean_message} ({commit_hash})\n"
            entry += "\n"

    return entry


def update_changelog(new_entry: str) -> None:
    """Update CHANGELOG.md with new entry."""
    changelog_path = Path("CHANGELOG.md")

    if changelog_path.exists():
        existing_content = changelog_path.read_text()
        # Insert new entry after header
        lines = existing_content.split("\n")
        header_end = 0
        for i, line in enumerate(lines):
            if line.startswith("## "):
                header_end = i
                break

        if header_end > 0:
            new_content = (
                "\n".join(lines[:header_end])
                + "\n\n"
                + new_entry
                + "\n".join(lines[header_end:])
            )
        else:
            new_content = new_entry + "\n" + existing_content
    else:
        # Create new changelog
        header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        new_content = header + new_entry

    changelog_path.write_text(new_content)


def main() -> None:
    """Generate changelog entry."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_changelog.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    commits = get_commits_since_last_tag()
    categories = categorize_commits(commits)

    # Only generate if there are commits
    if any(categories.values()):
        entry = format_changelog_entry(version, categories)
        update_changelog(entry)
        print(f"Changelog updated for version {version}")
    else:
        print("No commits found for changelog")


if __name__ == "__main__":
    main()
