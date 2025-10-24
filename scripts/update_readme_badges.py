#!/usr/bin/env python3
"""README badge update script for mypylogger v0.2.0.

This script updates the README.md file with current badge URLs,
including the new performance badge.

Requirements addressed:
- 15.3: Update README with performance badge display
- 15.5: README badges updated to include performance metrics from enhanced CI/CD workflows
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys


class ReadmeBadgeUpdater:
    """Updates README.md with current badge URLs."""

    def __init__(self, readme_path: Path = Path("README.md")) -> None:
        """Initialize badge updater.

        Args:
            readme_path: Path to README.md file
        """
        self.readme_path = readme_path
        self.badge_base_url = (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com"
        )

    def get_badge_definitions(self, repo_name: str) -> dict[str, str]:
        """Get badge definitions for the repository.

        Args:
            repo_name: GitHub repository name (owner/repo)

        Returns:
            Dictionary mapping badge names to their URLs
        """
        base_url = f"{self.badge_base_url}/{repo_name}/main/.github/badges"

        return {
            "build": f"{base_url}/build-status.json",
            "coverage": f"{base_url}/coverage.json",
            "code-style": f"{base_url}/code-style.json",
            "security": f"{base_url}/security.json",
            "performance": f"{base_url}/performance.json",
        }

    def generate_badge_markdown(self, repo_name: str) -> list[str]:
        """Generate badge markdown lines.

        Args:
            repo_name: GitHub repository name (owner/repo)

        Returns:
            List of markdown badge lines
        """
        badges = self.get_badge_definitions(repo_name)

        return [
            f"![Build Status]({badges['build']})",
            f"![Coverage]({badges['coverage']})",
            f"![Code Style]({badges['code-style']})",
            f"![Security]({badges['security']})",
            f"![Performance]({badges['performance']})",
        ]

    def update_readme_badges(self, repo_name: str) -> bool:
        """Update README.md with current badge URLs.

        Args:
            repo_name: GitHub repository name (owner/repo)

        Returns:
            True if README was updated, False otherwise
        """
        if not self.readme_path.exists():
            print(f"❌ README file not found: {self.readme_path}")
            return False

        # Read current README content
        try:
            with self.readme_path.open(encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading README: {e}")
            return False

        # Generate new badge markdown
        badge_lines = self.generate_badge_markdown(repo_name)
        badge_section = "\n".join(badge_lines)

        # Look for existing badge section
        badge_patterns = [
            # Pattern 1: Badges in a dedicated section
            r"<!-- BADGES START -->.*?<!-- BADGES END -->",
            # Pattern 2: Multiple badge lines at the top
            r"(!\[.*?\]\(https://img\.shields\.io/.*?\)\s*\n?){2,}",
            # Pattern 3: Single line with multiple badges
            r"!\[.*?\]\(https://img\.shields\.io/.*?\)(\s*!\[.*?\]\(https://img\.shields\.io/.*?\))*",
        ]

        updated = False

        # Try to replace existing badge section
        for pattern in badge_patterns:
            if re.search(pattern, content, re.DOTALL):
                # Replace with new badges wrapped in comments
                new_badge_section = f"<!-- BADGES START -->\n{badge_section}\n<!-- BADGES END -->"
                content = re.sub(pattern, new_badge_section, content, flags=re.DOTALL)
                updated = True
                print("✅ Updated existing badge section")
                break

        # If no existing badges found, add them after the title
        if not updated:
            # Look for the main title (# Title)
            title_pattern = r"^(#\s+.*?)(\n|$)"
            title_match = re.search(title_pattern, content, re.MULTILINE)

            if title_match:
                # Insert badges after the title
                title_end = title_match.end()
                new_badge_section = (
                    f"\n<!-- BADGES START -->\n{badge_section}\n<!-- BADGES END -->\n"
                )
                content = content[:title_end] + new_badge_section + content[title_end:]
                updated = True
                print("✅ Added new badge section after title")
            else:
                # Insert badges at the beginning
                new_badge_section = (
                    f"<!-- BADGES START -->\n{badge_section}\n<!-- BADGES END -->\n\n"
                )
                content = new_badge_section + content
                updated = True
                print("✅ Added new badge section at beginning")

        # Write updated content back to README
        if updated:
            try:
                with self.readme_path.open("w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ README updated successfully: {self.readme_path}")
                return True
            except Exception as e:
                print(f"❌ Error writing README: {e}")
                return False
        else:
            print("⚠️ No badge updates needed")
            return True

    def validate_badge_urls(self, repo_name: str) -> None:
        """Validate that badge URLs are correctly formatted.

        Args:
            repo_name: GitHub repository name (owner/repo)
        """
        print("🔍 Validating Badge URLs")
        print("=" * 25)

        badges = self.get_badge_definitions(repo_name)

        for badge_name, badge_url in badges.items():
            print(f"📋 {badge_name.title()} Badge:")
            print(f"   URL: {badge_url}")

            # Basic URL validation
            if badge_url.startswith("https://img.shields.io/endpoint?url="):
                print("   ✅ Valid shields.io endpoint URL")
            else:
                print("   ❌ Invalid URL format")

            print()

    def generate_badge_preview(self, repo_name: str) -> str:
        """Generate a preview of how badges will look in README.

        Args:
            repo_name: GitHub repository name (owner/repo)

        Returns:
            Markdown preview string
        """
        badge_lines = self.generate_badge_markdown(repo_name)

        preview = "Badge Preview:\n"
        preview += "=" * 14 + "\n\n"
        preview += "<!-- BADGES START -->\n"
        preview += "\n".join(badge_lines)
        preview += "\n<!-- BADGES END -->\n"

        return preview


def detect_repository_name() -> str:
    """Detect repository name from git configuration or environment.

    Returns:
        Repository name in format "owner/repo"
    """
    # Try to get from environment variables (GitHub Actions)
    github_repo = os.environ.get("GITHUB_REPOSITORY")
    if github_repo:
        return github_repo

    # Try to get from git remote
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        )

        remote_url = result.stdout.strip()

        # Parse GitHub URL
        if "github.com" in remote_url:
            # Handle both SSH and HTTPS URLs
            if remote_url.startswith("git@github.com:"):
                repo_part = remote_url.replace("git@github.com:", "").replace(".git", "")
            elif "github.com/" in remote_url:
                repo_part = remote_url.split("github.com/")[-1].replace(".git", "")
            else:
                repo_part = None

            if repo_part and "/" in repo_part:
                return repo_part

    except subprocess.CalledProcessError:
        pass

    # Fallback - ask user or use default
    return "username/mypylogger"


def main() -> None:
    """Main entry point for README badge updates."""
    print("🏷️ README Badge Updater for mypylogger v0.2.0")
    print("=" * 48)

    # Detect or get repository name
    repo_name = sys.argv[1] if len(sys.argv) > 1 else detect_repository_name()

    print(f"Repository: {repo_name}")
    print()

    updater = ReadmeBadgeUpdater()

    # Validate badge URLs
    updater.validate_badge_urls(repo_name)

    # Show badge preview
    preview = updater.generate_badge_preview(repo_name)
    print(preview)
    print()

    # Update README
    print("📝 Updating README.md...")
    success = updater.update_readme_badges(repo_name)

    if success:
        print("\n✅ README badge update completed successfully")
        print("\n📋 Badge URLs added to README:")
        badges = updater.get_badge_definitions(repo_name)
        for badge_name, badge_url in badges.items():
            print(f"  • {badge_name.title()}: {badge_url}")

        print(
            "\n💡 Badges will be visible once the badge JSON files are committed to the repository"
        )
    else:
        print("\n❌ README badge update failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
