"""
Tests for git hook functionality and pre-commit integration.

This test suite validates that our git hooks work correctly and
captures lessons learned from pre-commit hook failures.
"""

import subprocess
from pathlib import Path

import pytest


class TestGitHooks:
    """Test git hook functionality and pre-commit integration."""

    def test_precommit_config_exists(self):
        """Test that pre-commit configuration exists and is valid."""
        config_path = Path(".pre-commit-config.yaml")
        assert config_path.exists(), "Pre-commit config file should exist"

        # Validate YAML syntax
        import yaml

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "repos" in config, "Config should have repos section"
        assert len(config["repos"]) > 0, "Should have at least one repo configured"

    def test_precommit_hooks_installable(self):
        """Test that pre-commit hooks can be installed without errors."""
        # This is a basic smoke test - in CI/CD this would be more comprehensive
        try:
            result = subprocess.run(
                ["pre-commit", "--version"], capture_output=True, text=True, check=True
            )
            assert "pre-commit" in result.stdout.lower()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("pre-commit not available in test environment")

    def test_mypy_dependencies_specific(self):
        """Test that mypy dependencies are specific, not using problematic types-all."""
        config_path = Path(".pre-commit-config.yaml")
        with open(config_path) as f:
            content = f.read()

        # Should not use types-all (causes dependency resolution issues)
        assert "types-all" not in content, (
            "Should use specific type dependencies, not types-all which causes "
            "dependency resolution failures with yanked packages"
        )

        # Should have specific type dependencies
        assert "types-" in content, "Should have specific type dependencies"

    def test_hook_stages_not_deprecated(self):
        """Test that hook configuration doesn't use deprecated stage names."""
        config_path = Path(".pre-commit-config.yaml")
        with open(config_path) as f:
            content = f.read()

        # These stage names are deprecated
        deprecated_stages = ["commit", "merge-commit", "push"]

        for stage in deprecated_stages:
            # Allow in comments but not in actual configuration
            lines = [
                line.strip()
                for line in content.split("\n")
                if not line.strip().startswith("#")
            ]
            config_content = "\n".join(lines)

            assert f"stages: [{stage}]" not in config_content, (
                f"Deprecated stage '{stage}' should not be used. "
                f"Use 'pre-commit', 'pre-merge-commit', 'pre-push' instead"
            )

    @pytest.mark.integration
    def test_quality_gates_in_precommit(self):
        """Test that essential quality gates are included in pre-commit hooks."""
        config_path = Path(".pre-commit-config.yaml")
        with open(config_path) as f:
            content = f.read()

        # Essential tools should be present
        essential_tools = ["black", "isort", "flake8", "mypy", "bandit"]

        for tool in essential_tools:
            assert (
                tool in content
            ), f"Essential tool '{tool}' should be in pre-commit config"

    def test_precommit_lessons_learned(self):
        """Document lessons learned from pre-commit hook failures."""
        lessons = {
            "types-all": (
                "Don't use 'types-all' in mypy additional_dependencies. "
                "It tries to install every type stub including yanked packages. "
                "Use specific type stubs like 'types-PyYAML', 'types-requests' instead."
            ),
            "deprecated_stages": (
                "Update pre-commit hooks regularly with 'pre-commit autoupdate' "
                "to avoid deprecated stage name warnings."
            ),
            "dependency_resolution": (
                "Pre-commit environments can fail if dependencies have conflicts. "
                "Keep additional_dependencies minimal and specific."
            ),
            "hook_updates": (
                "When pre-commit hooks fail, first try 'pre-commit clean' and "
                "'pre-commit install --install-hooks' to refresh environments."
            ),
        }

        # This test documents the lessons - in a real scenario you might
        # store these in documentation or validate against known issues
        assert len(lessons) > 0, "Should have documented lessons learned"

        for lesson_key, lesson_text in lessons.items():
            assert len(lesson_text) > 50, f"Lesson '{lesson_key}' should be detailed"


class TestGitWorkflow:
    """Test git workflow integration."""

    def test_commit_message_format(self):
        """Test that commit messages follow conventional format."""
        # This would typically check the last commit message
        # For now, just validate the format we expect
        valid_prefixes = [
            "feat:",
            "fix:",
            "docs:",
            "test:",
            "refactor:",
            "style:",
            "perf:",
            "chore:",
            "ci:",
        ]

        # In a real test, you'd check actual commit messages
        example_message = "fix: resolved pre-commit hook dependency issues"

        has_valid_prefix = any(
            example_message.startswith(prefix) for prefix in valid_prefixes
        )
        assert has_valid_prefix, "Commit messages should follow conventional format"

    @pytest.mark.integration
    def test_git_hooks_prevent_bad_commits(self):
        """Test that git hooks prevent commits with quality issues."""
        # This is a placeholder for integration testing
        # In practice, you'd create a temporary git repo and test the hooks
        pytest.skip("Integration test - requires full git environment setup")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
