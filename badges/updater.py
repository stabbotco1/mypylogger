"""README update module with atomic write operations.

This module provides functionality to atomically update README.md with
generated badges, including race condition prevention and retry logic.
"""

from __future__ import annotations

from pathlib import Path
import tempfile
import time


def find_badge_section(content: str) -> tuple[int, int]:
    """Locate badge insertion point in README content.

    Args:
        content: README.md file content as string.

    Returns:
        Tuple of (start_index, end_index) for badge section location.
    """
    if not content:
        return (0, 0)

    # Look for existing badge section markers
    start_marker = "<!-- BADGES START -->"
    end_marker = "<!-- BADGES END -->"
    single_marker = "<!-- BADGES -->"

    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)

    if start_pos != -1 and end_pos != -1:
        # Found both markers, return the section between them
        return (start_pos, end_pos + len(end_marker))

    # Look for single marker
    single_pos = content.find(single_marker)
    if single_pos != -1:
        return (single_pos, single_pos + len(single_marker))

    # No markers found, find position after first heading
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("# "):
            # Found first heading, position after it
            if i + 1 < len(lines):
                # Position at start of next line
                pos = len("\n".join(lines[: i + 1])) + 1
                return (pos, pos)
            # Heading is last line, position at end
            return (len(content), len(content))

    # No heading found, position at start
    return (0, 0)


def atomic_write_readme(content: str, max_retries: int = 10) -> bool:
    """Perform atomic write with retry logic for race condition prevention.

    Args:
        content: Complete README content to write.
        max_retries: Maximum number of retry attempts for file contention.

    Returns:
        True if write was successful, False otherwise.
    """
    readme_path = Path("README.md")

    for attempt in range(max_retries):
        try:
            # Create backup if original file exists
            if readme_path.exists():
                backup_path = Path("README.md.backup")
                backup_path.write_text(readme_path.read_text(), encoding="utf-8")

            # Write to temporary file first
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".tmp", dir=readme_path.parent, delete=False, encoding="utf-8"
            ) as temp_file:
                temp_file.write(content)
                temp_path = Path(temp_file.name)

            # Verify content was written correctly
            if temp_path.read_text(encoding="utf-8") != content:
                temp_path.unlink(missing_ok=True)
                return False

            # Atomic rename operation
            temp_path.replace(readme_path)
            return True

        except (OSError, PermissionError):
            # Handle file contention or permission errors
            # Clean up temp file if it exists
            if "temp_path" in locals():
                temp_path.unlink(missing_ok=True)

            if attempt < max_retries - 1:
                time.sleep(5)  # Wait 5 seconds before retry
                continue
            # Final attempt failed
            return False
        except Exception:
            # Unexpected error, clean up temp file if it exists
            if "temp_path" in locals():
                temp_path.unlink(missing_ok=True)
            return False

    return False


def update_readme_with_badges(badges: list[str]) -> bool:
    """Update README.md with badge markdown using atomic writes.

    Args:
        badges: List of badge markdown strings to insert into README.

    Returns:
        True if update was successful, False otherwise.
    """
    readme_path = Path("README.md")

    # Check if README exists
    if not readme_path.exists():
        return False

    try:
        # Read current README content
        current_content = readme_path.read_text(encoding="utf-8")

        # Find badge section location
        start_pos, end_pos = find_badge_section(current_content)

        # Generate badge section content
        if badges:
            badge_lines = []
            badge_lines.append("<!-- BADGES START -->")
            badge_lines.extend(badges)
            badge_lines.append("<!-- BADGES END -->")
            badge_section = "\n".join(badge_lines)
        else:
            # Empty badge list, create empty section
            badge_section = "<!-- BADGES START -->\n<!-- BADGES END -->"

        # Construct new content
        if start_pos == end_pos:
            # No existing section, insert new one
            if start_pos == 0:
                # Insert at beginning
                new_content = badge_section + "\n\n" + current_content
            else:
                # Insert after first heading
                new_content = (
                    current_content[:start_pos]
                    + "\n"
                    + badge_section
                    + "\n"
                    + current_content[start_pos:]
                )
        else:
            # Replace existing section
            new_content = current_content[:start_pos] + badge_section + current_content[end_pos:]

        # Write updated content atomically
        return atomic_write_readme(new_content)

    except Exception:
        return False
