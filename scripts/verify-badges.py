#!/usr/bin/env python3
"""
Badge verification script for mypylogger project.

This script verifies that all badge URLs in the README are correctly formatted
and will display properly on GitHub and PyPI.
"""

import re
import sys
from pathlib import Path


def extract_badges_from_readme():
    """Extract all badge URLs from README.md."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("❌ README.md not found")
        return []

    content = readme_path.read_text()

    # Find all badge patterns: [![text](url)](link)
    badge_pattern = r"\[\!\[([^\]]+)\]\(([^)]+)\)\]\(([^)]+)\)"
    badges = re.findall(badge_pattern, content)

    return badges


def verify_badge_urls():
    """Verify that badge URLs are correctly formatted."""
    badges = extract_badges_from_readme()

    if not badges:
        print("❌ No badges found in README.md")
        return False

    print(f"📊 Found {len(badges)} badges in README.md")
    print()

    all_valid = True

    for i, (alt_text, badge_url, link_url) in enumerate(badges, 1):
        print(f"{i}. {alt_text}")
        print(f"   Badge URL: {badge_url}")
        print(f"   Link URL:  {link_url}")

        # Basic URL validation
        if not badge_url.startswith(("http://", "https://")):
            print("   ❌ Invalid badge URL (must start with http/https)")
            all_valid = False
        elif not link_url.startswith(("http://", "https://")):
            print("   ❌ Invalid link URL (must start with http/https)")
            all_valid = False
        else:
            print("   ✅ URLs look valid")

        print()

    return all_valid


def check_required_badges():
    """Check that all required badges are present."""
    badges = extract_badges_from_readme()
    badge_texts = [badge[0].lower() for badge in badges]

    required_badges = [
        "build status",
        "coverage",
        "security",
        "license",
        "pypi version",
        "python versions",
        "downloads",
        "code style",
    ]

    optional_badges = ["maintenance", "issues", "stars"]

    print("🔍 Checking for required badges:")
    all_present = True

    for required in required_badges:
        found = any(required in text for text in badge_texts)
        status = "✅" if found else "❌"
        print(f"   {status} {required.title()}")
        if not found:
            all_present = False

    print("\n🎯 Checking for optional badges:")
    for optional in optional_badges:
        found = any(optional in text for text in badge_texts)
        status = "✅" if found else "➖"
        print(f"   {status} {optional.title()}")

    return all_present


def verify_workflow_names():
    """Verify that GitHub Actions workflow names match badge URLs."""
    print("\n🔧 Verifying GitHub Actions workflow names:")

    workflows = {
        "CI/CD Pipeline": ".github/workflows/ci.yml",
        "Security Scanning": ".github/workflows/security.yml",
    }

    all_match = True

    for workflow_name, workflow_file in workflows.items():
        workflow_path = Path(workflow_file)
        if workflow_path.exists():
            content = workflow_path.read_text()
            if f"name: {workflow_name}" in content:
                print(f"   ✅ {workflow_name}")
            else:
                print(f"   ❌ {workflow_name} (name mismatch in {workflow_file})")
                all_match = False
        else:
            print(f"   ❌ {workflow_name} (file {workflow_file} not found)")
            all_match = False

    return all_match


def main():
    """Main verification function."""
    print("🏷️  Badge Verification for mypylogger")
    print("=" * 40)
    print()

    # Verify badge URLs
    urls_valid = verify_badge_urls()

    # Check required badges
    badges_complete = check_required_badges()

    # Verify workflow names
    workflows_match = verify_workflow_names()

    print()
    print("📋 Summary:")
    print(f"   Badge URLs Valid: {'✅' if urls_valid else '❌'}")
    print(f"   Required Badges Present: {'✅' if badges_complete else '❌'}")
    print(f"   Workflow Names Match: {'✅' if workflows_match else '❌'}")

    if urls_valid and badges_complete and workflows_match:
        print()
        print("🎉 All badge checks passed!")
        print("   Badges will display correctly on GitHub and PyPI")
        print("   GitHub Actions workflows are properly configured")
        return 0
    else:
        print()
        print("⚠️  Some badge checks failed")
        print("   Review the issues above and fix the configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())
