#!/usr/bin/env python
"""Post-generation script for cookiecutter template.

This script runs after the cookiecutter template is generated to:
1. Remove unwanted files and directories based on user choices
2. Set up the license file according to the chosen license
3. Initialize optional components like Astro CLI
4. Handle project layout (standard or src)
"""

import logging
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Final

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("cookiecutter_post_gen.log", mode="w", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# Use Path object for better path handling
PROJECT_DIRECTORY: Final[Path] = Path.cwd()

operating_system: str = platform.system()


def remove_file(filepath: str) -> None:
    """Remove a file from the project directory.

    Args:
        filepath: Relative path to the file to be removed.

    Note:
        Uses missing_ok=True to avoid errors if the file doesn't exist.
    """
    try:
        file_path = PROJECT_DIRECTORY / filepath
        if file_path.exists():
            file_path.unlink(missing_ok=True)
            logger.info(f"Removed file: {filepath}")
        else:
            logger.debug(f"File does not exist, skipping: {filepath}")
    except Exception as e:
        logger.warning(f"Could not remove file {filepath}: {e}")


def remove_dir(filepath: str) -> None:
    """Remove a directory from the project directory.

    Args:
        filepath: Relative path to the directory to be removed.

    Note:
        Uses ignore_errors=True to avoid errors if the directory doesn't exist
        or contains read-only files.
    """
    try:
        dir_path = PROJECT_DIRECTORY / filepath
        if dir_path.exists():
            shutil.rmtree(dir_path, ignore_errors=True)
            logger.info(f"Removed directory: {filepath}")
        else:
            logger.debug(f"Directory does not exist, skipping: {filepath}")
    except Exception as e:
        logger.warning(f"Could not remove directory {filepath}: {e}")


def move_file(filepath: str, target: str) -> None:
    """Move a file within the project directory.

    Args:
        filepath: Relative path to the file to be moved.
        target: Relative path to the target location.

    Note:
        Creates parent directories if they don't exist.
        Only attempts to move if the source file exists.
    """
    source_path = PROJECT_DIRECTORY / filepath
    target_path = PROJECT_DIRECTORY / target

    try:
        # Make sure the target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if source_path.exists():
            source_path.rename(target_path)
            logger.info(f"Moved file: {filepath} → {target}")
        else:
            logger.warning(f"Source file {filepath} does not exist, skipping move operation.")
    except PermissionError:
        logger.error(f"Permission denied when moving {filepath} to {target}")
    except FileExistsError:
        logger.error(f"Target file {target} already exists")
    except Exception as e:
        logger.error(f"Error moving file {filepath} to {target}: {e}")


def move_dir(src: str, target: str) -> None:
    """Move a directory within the project directory.

    Args:
        src: Relative path to the directory to be moved.
        target: Relative path to the target location.

    Note:
        Creates parent directories if they don't exist.
        Uses shutil.move which handles cross-device moves better than Path.rename.
        Only attempts to move if the source directory exists.
    """
    source_path = PROJECT_DIRECTORY / src
    target_path = PROJECT_DIRECTORY / target

    try:
        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if source_path.exists():
            shutil.move(str(source_path), str(target_path))
            logger.info(f"Moved directory: {src} → {target}")
        else:
            logger.warning(f"Source directory {src} does not exist, skipping move operation.")
    except PermissionError:
        logger.error(f"Permission denied when moving {src} to {target}")
    except FileExistsError:
        logger.error(f"Target directory {target} already exists")
    except Exception as e:
        logger.error(f"Error moving directory {src} to {target}: {e}")


def run_command(command: list[str], check: bool = True) -> subprocess.CompletedProcess | None:
    """Run a shell command and handle exceptions.

    Args:
        command: List of command and arguments to run.
        check: If True, raises a CalledProcessError if the command fails.

    Returns:
        CompletedProcess instance if successful, None if an error occurred.

    Raises:
        subprocess.CalledProcessError: If check is True and the command returns
                                      a non-zero exit code.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command '{' '.join(command)}' failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        if check:
            raise
        return None
    except FileNotFoundError:
        print(f"Command '{command[0]}' not found")
        return None
    except Exception as e:
        print(f"Error running command '{' '.join(command)}': {e}")
        return None


if __name__ == "__main__":
    # Handle MkDocs
    match "{{cookiecutter.mkdocs}}":
        case "y":
            pass  # Keep docs directory and mkdocs.yml
        case _:
            remove_dir("docs")
            remove_file("mkdocs.yml")

    # Handle Codecov
    match "{{cookiecutter.codecov}}":
        case "y":
            pass  # Keep codecov files
        case _:
            remove_file("codecov.yaml")

    # Handle Astro CLI initialization
    match ("{{cookiecutter.include_astro_cli}}", operating_system):
        case ("y", "Darwin"):
            try:
                # Check if Astro CLI is installed
                result = run_command(["which", "astro"], check=False)

                if result is not None:
                    match result.returncode:
                        case 0:
                            # Initialize Astro project
                            try:
                                run_command(["astro", "dev", "init"])
                                print("Successfully initialized Astro project.")
                            except subprocess.SubprocessError as e:
                                print(f"Error initializing Astro project: {e}")
                        case _:
                            print("Astro CLI not found. Please install it first with:")
                            print("  curl -sSL https://install.astronomer.io | sudo bash")
            except Exception as e:
                print(f"Error checking for Astro CLI: {e}")
                # Don't exit with error as this is optional
        case _:
            # For non-macOS or if user opted out
            print("Skipping Astro CLI initialization...")

    # License handling
    license_type: str = "{{cookiecutter.open_source_license}}"
    all_licenses: list[str] = ["LICENSE_MIT", "LICENSE_BSD", "LICENSE_ISC", "LICENSE_APACHE", "LICENSE_GPL"]
    license_to_keep: str | None = None

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
