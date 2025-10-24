"""Main entry point for mypylogger development and testing."""

import sys


def main() -> None:
    """Main development environment entry point."""
    sys.stdout.write("mypylogger v0.2.0 - Development Environment\n")
    sys.stdout.write("Run 'uv run pytest' to execute tests\n")
    sys.stdout.write("Run 'uv run ruff format .' to format code\n")
    sys.stdout.write("Run 'uv run ruff check .' to check linting\n")


if __name__ == "__main__":
    main()
