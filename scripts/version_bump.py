#!/usr/bin/env python3
"""Interactive version bump script for mypylogger.

This script provides centralized version management with automatic document updates.
It uses pyproject.toml as the single source of truth for version information.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomli
except ImportError:
    import tomllib as tomli  # Python 3.11+


class VersionError(Exception):
    """Raised when version operations fail."""


class VersionInfo:
    """Represents semantic version information."""

    def __init__(self, version_string: str) -> None:
        """Initialize version info from string.
        
        Args:
            version_string: Version in format "major.minor.patch"
            
        Raises:
            VersionError: If version format is invalid
        """
        self.version_string = version_string
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_string)
        if not match:
            raise VersionError(f"Invalid version format: {version_string}")
        
        self.major = int(match.group(1))
        self.minor = int(match.group(2))
        self.patch = int(match.group(3))

    def bump_major(self) -> VersionInfo:
        """Create new version with major bump."""
        return VersionInfo(f"{self.major + 1}.0.0")

    def bump_minor(self) -> VersionInfo:
        """Create new version with minor bump."""
        return VersionInfo(f"{self.major}.{self.minor + 1}.0")

    def bump_patch(self) -> VersionInfo:
        """Create new version with patch bump."""
        return VersionInfo(f"{self.major}.{self.minor}.{self.patch + 1}")

    def __str__(self) -> str:
        """Return version string."""
        return self.version_string

    def __repr__(self) -> str:
        """Return version representation."""
        return f"VersionInfo('{self.version_string}')"


class VersionManager:
    """Manages version information and updates across the project."""

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize version manager.
        
        Args:
            project_root: Project root directory. If None, uses current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.pyproject_path = self.project_root / "pyproject.toml"
        
        if not self.pyproject_path.exists():
            raise VersionError(f"pyproject.toml not found at {self.pyproject_path}")

    def get_current_version(self) -> VersionInfo:
        """Get current version from pyproject.toml.
        
        Returns:
            Current version information
            
        Raises:
            VersionError: If version cannot be read or parsed
        """
        try:
            with open(self.pyproject_path, "rb") as f:
                data = tomli.load(f)
            
            version_string = data.get("project", {}).get("version")
            if not version_string:
                raise VersionError("Version not found in pyproject.toml")
            
            return VersionInfo(version_string)
        except (OSError, tomli.TOMLDecodeError) as e:
            raise VersionError(f"Failed to read pyproject.toml: {e}") from e

    def update_pyproject_version(self, new_version: VersionInfo) -> None:
        """Update version in pyproject.toml.
        
        Args:
            new_version: New version to set
            
        Raises:
            VersionError: If update fails
        """
        try:
            # Read current content
            content = self.pyproject_path.read_text(encoding="utf-8")
            
            # Replace version line
            pattern = r'^version = "[^"]*"'
            replacement = f'version = "{new_version}"'
            
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            if new_content == content:
                raise VersionError("Version line not found in pyproject.toml")
            
            # Write updated content
            self.pyproject_path.write_text(new_content, encoding="utf-8")
            
        except OSError as e:
            raise VersionError(f"Failed to update pyproject.toml: {e}") from e

    def get_version_files(self) -> list[tuple[Path, str, str]]:
        """Get list of files containing version references.
        
        Returns:
            List of tuples (file_path, pattern, description)
        """
        return [
            # Source code files
            (
                self.project_root / "src" / "mypylogger" / "__init__.py",
                r'__version__ = "[^"]*"',
                "Package version constant"
            ),
            (
                self.project_root / "src" / "mypylogger" / "__init__.py",
                r'"""mypylogger v[0-9]+\.[0-9]+\.[0-9]+ - [^"]*"""',
                "Module docstring version"
            ),
            # Documentation files
            (
                self.project_root / "README.md",
                r"# mypylogger v[0-9]+\.[0-9]+\.[0-9]+",
                "README title"
            ),
            (
                self.project_root / "README.md",
                r"mypylogger v[0-9]+\.[0-9]+\.[0-9]+ does ONE thing",
                "README description"
            ),
            # Test runner script
            (
                self.project_root / "scripts" / "run_tests.sh",
                r"# Master test script for mypylogger v[0-9]+\.[0-9]+\.[0-9]+",
                "Test script comment"
            ),
            (
                self.project_root / "scripts" / "run_tests.sh",
                r"echo \"🧪 mypylogger v[0-9]+\.[0-9]+\.[0-9]+ - Master Test Runner\"",
                "Test script output"
            ),
        ]

    def update_version_files(self, old_version: VersionInfo, new_version: VersionInfo) -> list[Path]:
        """Update version references in all project files.
        
        Args:
            old_version: Current version
            new_version: New version to set
            
        Returns:
            List of files that were updated
            
        Raises:
            VersionError: If any file update fails
        """
        updated_files = []
        
        for file_path, pattern, description in self.get_version_files():
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text(encoding="utf-8")
                
                # Create replacement pattern
                if "__version__" in pattern:
                    replacement = f'__version__ = "{new_version}"'
                elif "mypylogger v" in pattern and "does ONE thing" in pattern:
                    replacement = re.sub(
                        r"mypylogger v[0-9]+\.[0-9]+\.[0-9]+",
                        f"mypylogger v{new_version}",
                        content
                    )
                    new_content = replacement
                else:
                    # Generic version replacement
                    replacement = re.sub(
                        r"v[0-9]+\.[0-9]+\.[0-9]+",
                        f"v{new_version}",
                        content
                    )
                    new_content = replacement
                
                # Apply specific pattern replacements
                if "__version__" in pattern:
                    new_content = re.sub(pattern, replacement, content)
                elif "# mypylogger v" in pattern:
                    new_content = re.sub(pattern, f"# mypylogger v{new_version}", content)
                elif "Master test script" in pattern:
                    new_content = re.sub(
                        pattern,
                        f"# Master test script for mypylogger v{new_version}",
                        content
                    )
                elif "Master Test Runner" in pattern:
                    new_content = re.sub(
                        pattern,
                        f'echo "🧪 mypylogger v{new_version} - Master Test Runner"',
                        content
                    )
                elif '"""mypylogger v' in pattern:
                    new_content = re.sub(
                        r'"""mypylogger v[0-9]+\.[0-9]+\.[0-9]+',
                        f'"""mypylogger v{new_version}',
                        content
                    )
                
                if new_content != content:
                    file_path.write_text(new_content, encoding="utf-8")
                    updated_files.append(file_path)
                    print(f"  ✓ Updated {description} in {file_path.relative_to(self.project_root)}")
                
            except OSError as e:
                raise VersionError(f"Failed to update {file_path}: {e}") from e
        
        return updated_files

    def validate_semantic_version(self, version_string: str) -> bool:
        """Validate semantic version format.
        
        Args:
            version_string: Version string to validate
            
        Returns:
            True if valid semantic version
        """
        try:
            VersionInfo(version_string)
            return True
        except VersionError:
            return False


class GitManager:
    """Manages Git operations for version bumps."""

    def __init__(self, project_root: Path) -> None:
        """Initialize Git manager.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root

    def is_clean_working_directory(self) -> bool:
        """Check if working directory is clean.
        
        Returns:
            True if working directory is clean
        """
        try:
            result = subprocess.run(
                ["git", "--no-pager", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return len(result.stdout.strip()) == 0
        except subprocess.CalledProcessError:
            return False

    def stage_files(self, files: list[Path]) -> None:
        """Stage files for commit.
        
        Args:
            files: List of files to stage
            
        Raises:
            VersionError: If staging fails
        """
        try:
            # Stage all modified files
            subprocess.run(
                ["git", "add", "."],
                cwd=self.project_root,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise VersionError(f"Failed to stage files: {e}") from e

    def commit_and_push(self, old_version: VersionInfo, new_version: VersionInfo, comment: str) -> str:
        """Commit changes and push to remote.
        
        Args:
            old_version: Previous version
            new_version: New version
            comment: User comment for the version bump
            
        Returns:
            Commit hash
            
        Raises:
            VersionError: If commit or push fails
        """
        try:
            # Create commit message
            commit_message = f"feat: bump version {old_version} → {new_version}"
            if comment:
                commit_message += f"\n\n{comment}"
            
            # Commit changes
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get commit hash
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = commit_result.stdout.strip()
            
            # Push to remote
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.project_root,
                check=True
            )
            
            return commit_hash
            
        except subprocess.CalledProcessError as e:
            raise VersionError(f"Failed to commit and push: {e}") from e


def get_user_input(prompt: str, default: str | None = None) -> str:
    """Get user input with optional default.
    
    Args:
        prompt: Prompt to display
        default: Default value if user presses enter
        
    Returns:
        User input or default value
    """
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    response = input(full_prompt).strip()
    return response if response else (default or "")


def main() -> None:
    """Main version bump workflow."""
    print("🔄 mypylogger Version Bump Tool")
    print("=" * 40)
    
    try:
        # Initialize managers
        version_manager = VersionManager()
        git_manager = GitManager(version_manager.project_root)
        
        # Check Git status
        if not git_manager.is_clean_working_directory():
            print("❌ Working directory is not clean. Please commit or stash changes first.")
            sys.exit(1)
        
        # Get current version
        current_version = version_manager.get_current_version()
        print(f"📋 Current version: {current_version}")
        print()
        
        # Show version bump options
        print("Version bump options:")
        print(f"  1. Patch: {current_version.bump_patch()} (bug fixes)")
        print(f"  2. Minor: {current_version.bump_minor()} (new features)")
        print(f"  3. Major: {current_version.bump_major()} (breaking changes)")
        print("  4. Custom version")
        print()
        
        # Get user choice
        choice = get_user_input("Select version bump type (1-4)", "1")
        
        if choice == "1":
            new_version = current_version.bump_patch()
        elif choice == "2":
            new_version = current_version.bump_minor()
        elif choice == "3":
            new_version = current_version.bump_major()
        elif choice == "4":
            while True:
                version_input = get_user_input("Enter custom version (e.g., 1.2.3)")
                if version_manager.validate_semantic_version(version_input):
                    new_version = VersionInfo(version_input)
                    break
                else:
                    print("❌ Invalid version format. Please use semantic versioning (e.g., 1.2.3)")
        else:
            print("❌ Invalid choice. Exiting.")
            sys.exit(1)
        
        print(f"📈 New version: {new_version}")
        print()
        
        # Get version bump comment
        comment = get_user_input("Enter version bump comment (optional)")
        
        # Confirm the change
        print()
        print("📝 Version bump summary:")
        print(f"  Current: {current_version}")
        print(f"  New:     {new_version}")
        if comment:
            print(f"  Comment: {comment}")
        print()
        
        confirm = get_user_input("Proceed with version bump? (y/N)", "n").lower()
        if confirm not in ("y", "yes"):
            print("❌ Version bump cancelled.")
            sys.exit(0)
        
        print()
        print("🚀 Starting version bump...")
        
        # Update pyproject.toml
        print("  📝 Updating pyproject.toml...")
        version_manager.update_pyproject_version(new_version)
        
        # Update all version files
        print("  📝 Updating version references...")
        updated_files = version_manager.update_version_files(current_version, new_version)
        
        if not updated_files:
            print("  ⚠️  No files were updated")
        
        # Stage files
        print("  📦 Staging changes...")
        git_manager.stage_files(updated_files)
        
        # Commit and push
        print("  🔄 Committing and pushing...")
        commit_hash = git_manager.commit_and_push(current_version, new_version, comment)
        
        print()
        print("✅ Version bump completed successfully!")
        print(f"  📋 Version: {current_version} → {new_version}")
        print(f"  📦 Commit: {commit_hash[:8]}")
        print(f"  📁 Files updated: {len(updated_files)}")
        
    except VersionError as e:
        print(f"❌ Version bump failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Version bump cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()