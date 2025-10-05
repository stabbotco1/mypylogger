#!/usr/bin/env python3
"""Release validation and rollback script."""

import subprocess
import sys
import time
from typing import Optional

import requests


def check_pypi_availability(
    package_name: str, version: str, max_retries: int = 10
) -> bool:
    """Check if package version is available on PyPI."""
    url = f"https://pypi.org/pypi/{package_name}/{version}/json"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✓ Package {package_name} v{version} is available on PyPI")
                return True
            elif response.status_code == 404:
                print(
                    f"⏳ Package {package_name} v{version} not yet available on PyPI (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(30)  # Wait 30 seconds between attempts
            else:
                print(f"⚠️ Unexpected response from PyPI: {response.status_code}")
                time.sleep(30)
        except requests.RequestException as e:
            print(f"⚠️ Error checking PyPI: {e}")
            time.sleep(30)

    return False


def test_package_installation(package_name: str, version: str) -> bool:
    """Test package installation in clean environment."""
    try:
        # Create temporary virtual environment
        subprocess.run(["python", "-m", "venv", "temp_test_env"], check=True)

        # Install package in temp environment
        result = subprocess.run(
            [
                "temp_test_env/bin/python",
                "-m",
                "pip",
                "install",
                f"{package_name}=={version}",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"✗ Failed to install {package_name} v{version}")
            print(result.stderr)
            return False

        # Test basic import
        result = subprocess.run(
            [
                "temp_test_env/bin/python",
                "-c",
                f'import {package_name}; print(f\'Successfully imported {package_name} v{{getattr({package_name}, "__version__", "unknown")}}\')',
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"✓ Package {package_name} v{version} installs and imports correctly")
            return True
        else:
            print(f"✗ Package {package_name} v{version} failed import test")
            print(result.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"✗ Error during package testing: {e}")
        return False
    finally:
        # Clean up temp environment
        subprocess.run(["rm", "-rf", "temp_test_env"], check=False)


def get_previous_version() -> Optional[str]:
    """Get the previous git tag."""
    try:
        result = subprocess.run(
            ["git", "tag", "--sort=-version:refname"],
            capture_output=True,
            text=True,
            check=True,
        )

        tags = [tag.strip() for tag in result.stdout.split("\n") if tag.strip()]
        if len(tags) >= 2:
            # Return second most recent tag (previous version)
            return tags[1].lstrip("v")
        else:
            print("⚠️ No previous version found for rollback")
            return None
    except subprocess.CalledProcessError:
        print("⚠️ Error getting previous version")
        return None


def rollback_release(version: str) -> bool:
    """Rollback to previous version."""
    previous_version = get_previous_version()
    if not previous_version:
        print("✗ Cannot rollback: no previous version found")
        return False

    print(f"🔄 Rolling back from v{version} to v{previous_version}")

    try:
        # Reset to previous tag
        subprocess.run(["git", "reset", "--hard", f"v{previous_version}"], check=True)

        # Force push to main (dangerous but necessary for rollback)
        subprocess.run(["git", "push", "--force", "origin", "main"], check=True)

        # Delete the failed tag
        subprocess.run(["git", "tag", "-d", f"v{version}"], check=False)

        subprocess.run(
            ["git", "push", "--delete", "origin", f"v{version}"], check=False
        )

        print(f"✓ Successfully rolled back to v{previous_version}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Rollback failed: {e}")
        return False


def send_notification(status: str, version: str, details: str = "") -> None:
    """Send release notification (placeholder for future integration)."""
    message = f"Release v{version}: {status}"
    if details:
        message += f"\nDetails: {details}"

    print(f"📢 Notification: {message}")
    # Future: integrate with Slack, email, etc.


def main() -> None:
    """Main validation logic."""
    if len(sys.argv) < 2:
        print("Usage: python validate_release.py <version> [rollback]")
        sys.exit(1)

    version = sys.argv[1]
    should_rollback = len(sys.argv) > 2 and sys.argv[2] == "rollback"

    if should_rollback:
        success = rollback_release(version)
        if success:
            send_notification(
                "ROLLED BACK", version, "Release rolled back successfully"
            )
        else:
            send_notification(
                "ROLLBACK FAILED", version, "Manual intervention required"
            )
        sys.exit(0 if success else 1)

    print(f"🔍 Validating release v{version}")

    # Check PyPI availability
    pypi_available = check_pypi_availability("mypylogger", version)

    if not pypi_available:
        print("✗ Package not available on PyPI after maximum retries")
        send_notification("FAILED", version, "Package not available on PyPI")
        sys.exit(1)

    # Test installation
    install_success = test_package_installation("mypylogger", version)

    if not install_success:
        print("✗ Package installation test failed")
        send_notification("FAILED", version, "Package installation test failed")
        sys.exit(1)

    print(f"✅ Release v{version} validation successful")
    send_notification("SUCCESS", version, "All validation checks passed")


if __name__ == "__main__":
    main()
