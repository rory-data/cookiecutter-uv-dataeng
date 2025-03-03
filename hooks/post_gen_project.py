#!/usr/bin/env python
"""Post-generation script for cookiecutter template."""

import platform
import shutil
import subprocess
from pathlib import Path
from typing import Final

# Use Path object for better path handling
PROJECT_DIRECTORY: Final[Path] = Path.cwd()

operating_system = platform.system()


def remove_file(filepath: str) -> None:
    """Remove a file from the project directory."""
    (PROJECT_DIRECTORY / filepath).unlink(missing_ok=True)


def remove_dir(filepath: str) -> None:
    """Remove a directory from the project directory."""
    shutil.rmtree(PROJECT_DIRECTORY / filepath, ignore_errors=True)


def move_file(filepath: str, target: str) -> None:
    """Move a file within the project directory."""
    source_path = PROJECT_DIRECTORY / filepath
    target_path = PROJECT_DIRECTORY / target

    # Make sure the target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if source_path.exists():
        source_path.rename(target_path)


def move_dir(src: str, target: str) -> None:
    """Move a directory within the project directory."""
    # Create parent directories if they don't exist
    (PROJECT_DIRECTORY / target).parent.mkdir(parents=True, exist_ok=True)

    # Use shutil.move which handles cross-device moves better than Path.rename
    source_path = PROJECT_DIRECTORY / src
    target_path = PROJECT_DIRECTORY / target

    if source_path.exists():
        shutil.move(str(source_path), str(target_path))


if __name__ == "__main__":
    # Handle MkDocs
    match "{{cookiecutter.mkdocs}}":
        case "y":
            pass  # Keep docs directory and mkdocs.yml
        case _:
            remove_dir("docs")
            remove_file("mkdocs.yml")
            # Also remove MkDocs GitHub workflow if GitHub Actions is enabled
            if "{{cookiecutter.include_github_actions}}" == "y":
                remove_file(".github/workflows/docs.yml")

    # Handle Codecov
    match "{{cookiecutter.codecov}}":
        case "y":
            pass  # Keep codecov files
        case _:
            remove_file("codecov.yaml")
            # Only try to remove the workflow file if GitHub Actions is enabled
            if "{{cookiecutter.include_github_actions}}" == "y":
                remove_file(".github/workflows/validate-codecov-config.yml")

    # Handle Astro CLI initialization
    match ("{{cookiecutter.include_astro_cli}}", operating_system):
        case ("y", "Darwin"):
            try:
                # Check if Astro CLI is installed
                result = subprocess.run(["which", "astro"], capture_output=True, text=True, check=False)

                match result.returncode:
                    case 0:
                        # Initialize Astro project
                        try:
                            subprocess.run(["astro", "dev", "init"], check=True)
                        except subprocess.SubprocessError as e:
                            print(f"Error initialising Astro project: {e}")
                    case _:
                        print("Astro CLI not found. Please install it first with:")
                        print("  curl -sSL https://install.astronomer.io | sudo bash")
            except subprocess.SubprocessError as e:
                print(f"Error checking for Astro CLI: {e}")
                # Don't exit with error as this is optional
        case _:
            # For non-macOS or if user opted out
            print("Skipping Astro CLI initialisation...")

    # License handling
    license_type = "{{cookiecutter.open_source_license}}"
    all_licenses = ["LICENSE_MIT", "LICENSE_BSD", "LICENSE_ISC", "LICENSE_APACHE", "LICENSE_GPL"]

    match license_type:
        case "MIT license":
            move_file("LICENSE_MIT", "LICENSE")
            license_to_keep = "LICENSE_MIT"
        case "BSD license":
            move_file("LICENSE_BSD", "LICENSE")
            license_to_keep = "LICENSE_BSD"
        case "ISC license":
            move_file("LICENSE_ISC", "LICENSE")
            license_to_keep = "LICENSE_ISC"
        case "Apache Software License 2.0":
            move_file("LICENSE_APACHE", "LICENSE")
            license_to_keep = "LICENSE_APACHE"
        case "GNU General Public License v3":
            move_file("LICENSE_GPL", "LICENSE")
            license_to_keep = "LICENSE_GPL"
        case _:  # "Not open source" or any other case
            license_to_keep = None

    # Remove unused licenses
    if license_to_keep:
        for license_file in all_licenses:
            if license_file != license_to_keep:
                remove_file(license_file)
    else:
        for license_file in all_licenses:
            remove_file(license_file)
