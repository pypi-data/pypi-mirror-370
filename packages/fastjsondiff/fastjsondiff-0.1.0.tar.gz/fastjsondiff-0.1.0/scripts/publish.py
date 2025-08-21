#!/usr/bin/env python3
"""
Script to help with version management and publishing to PyPI.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def update_version(version: str) -> None:
    """Update version in pyproject.toml and Cargo.toml."""
    # Update pyproject.toml
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    content = re.sub(r'version = "([^"]+)"', f'version = "{version}"', content)
    pyproject_path.write_text(content)

    # Update Cargo.toml
    cargo_path = Path("Cargo.toml")
    content = cargo_path.read_text()
    content = re.sub(r'version = "([^"]+)"', f'version = "{version}"', content)
    cargo_path.write_text(content)

    print(f"Updated version to {version} in pyproject.toml and Cargo.toml")


def build_package() -> None:
    """Build the package using maturin."""
    print("Building package...")
    subprocess.run(["maturin", "build", "--release"], check=True)
    print("Package built successfully!")


def publish_to_pypi() -> None:
    """Publish the package to PyPI."""
    print("Publishing to PyPI...")
    subprocess.run(["maturin", "publish"], check=True)
    print("Package published successfully!")


def main():
    parser = argparse.ArgumentParser(description="FastJSONDiff publishing script")
    parser.add_argument(
        "command", choices=["version", "build", "publish"], help="Command to run"
    )
    parser.add_argument("--version", help="New version number (for version command)")

    args = parser.parse_args()

    if args.command == "version":
        if not args.version:
            print("Error: --version is required for the version command")
            sys.exit(1)
        update_version(args.version)
    elif args.command == "build":
        build_package()
    elif args.command == "publish":
        publish_to_pypi()


if __name__ == "__main__":
    main()
