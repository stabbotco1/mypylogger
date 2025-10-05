#!/usr/bin/env python3
"""
Generate enhanced CHANGELOG entry from conventional commits.
Categorizes changes by type and filters noise.
"""

import subprocess
import sys
from collections import defaultdict
from datetime import date


def get_commits_since_last_tag():
    """Get all commits since the last git tag."""
    try:
        last_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        commit_range = f"{last_tag}..HEAD"
    except subprocess.CalledProcessError:
        # No tags exist yet
        commit_range = "HEAD"

    commits = (
        subprocess.check_output(
            ["git", "log", commit_range, "--oneline", "--no-merges"], text=True
        )
        .strip()
        .split("\n")
    )

    return [c for c in commits if c]


def parse_conventional_commit(commit_line):
    """
    Parse conventional commit format.
    Returns: (type, scope, breaking, message, hash)

    Format: <hash> <type>(<scope>)!: <message>
    """
    parts = commit_line.split(" ", 1)
    if len(parts) != 2:
        return None, None, False, commit_line, parts[0] if parts else ""

    commit_hash, rest = parts

    # Check for breaking change indicator
    breaking = "!" in rest.split(":")[0] if ":" in rest else False

    # Parse type and scope
    if ":" not in rest:
        return None, None, breaking, rest, commit_hash

    prefix, message = rest.split(":", 1)
    message = message.strip()

    # Remove breaking change indicator
    prefix = prefix.replace("!", "")

    if "(" in prefix:
        commit_type, scope = prefix.split("(", 1)
        scope = scope.rstrip(")")
    else:
        commit_type = prefix
        scope = None

    return commit_type.strip(), scope, breaking, message, commit_hash


def categorize_commits(commits):
    """Categorize commits by type."""
    categories = defaultdict(list)

    # Skip noise patterns
    noise_patterns = [
        "chore: bump version",
        "chore(release)",
        "Merge pull request",
        "Merge branch",
    ]

    for commit in commits:
        # Skip noise
        if any(pattern in commit for pattern in noise_patterns):
            continue

        commit_type, scope, breaking, message, commit_hash = parse_conventional_commit(
            commit
        )

        # Categorize
        if breaking or "BREAKING CHANGE" in message:
            category = "Breaking Changes"
        elif commit_type == "feat":
            category = "Features"
        elif commit_type == "fix":
            category = "Bug Fixes"
        elif commit_type == "docs":
            category = "Documentation"
        elif commit_type == "perf":
            category = "Performance"
        elif commit_type == "refactor":
            category = "Refactoring"
        elif commit_type == "test":
            category = "Tests"
        elif commit_type == "chore":
            category = "Maintenance"
        else:
            category = "Other Changes"

        # Format entry
        scope_str = f"**{scope}**: " if scope else ""
        entry = f"- {scope_str}{message} ([`{commit_hash[:7]}`](https://github.com/stabbotco1/mypylogger/commit/{commit_hash}))"

        categories[category].append(entry)

    return categories


def generate_changelog_entry(version, categories):
    """Generate formatted CHANGELOG entry."""
    today = date.today().strftime("%Y-%m-%d")

    lines = [f"## [{version}] - {today}", ""]

    # Order categories by importance
    category_order = [
        "Breaking Changes",
        "Features",
        "Bug Fixes",
        "Performance",
        "Documentation",
        "Refactoring",
        "Tests",
        "Maintenance",
        "Other Changes",
    ]

    for category in category_order:
        if category in categories:
            lines.append(f"### {category}")
            lines.append("")
            lines.extend(categories[category])
            lines.append("")

    return "\n".join(lines)


def prepend_to_changelog(new_entry):
    """Prepend new entry to CHANGELOG.md."""
    try:
        with open("CHANGELOG.md", "r") as f:
            existing = f.read()
    except FileNotFoundError:
        existing = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"

    with open("CHANGELOG.md", "w") as f:
        f.write(new_entry)
        f.write("\n")
        f.write(existing)


def main():
    if len(sys.argv) != 2:
        print("Usage: generate-changelog.py <version>")
        sys.exit(1)

    version = sys.argv[1]

    print(f"Generating CHANGELOG entry for version {version}...")

    commits = get_commits_since_last_tag()
    if not commits or (len(commits) == 1 and not commits[0]):
        print("No commits found since last tag")
        sys.exit(0)

    print(f"Found {len(commits)} commits")

    categories = categorize_commits(commits)

    if not categories:
        print("No significant changes to document")
        sys.exit(0)

    entry = generate_changelog_entry(version, categories)
    prepend_to_changelog(entry)

    print("✓ CHANGELOG.md updated")
    print("\nGenerated entry:")
    print(entry)


if __name__ == "__main__":
    main()
