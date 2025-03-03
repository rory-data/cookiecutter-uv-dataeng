"""Utility functions for testing.

This module provides utility functions for testing cookiecutter templates,
including YAML validation, directory context management, and text searching.
"""

import logging
import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import yaml

# Configure logging
logger = logging.getLogger(__name__)


def is_valid_yaml(path: str | Path) -> bool:
    """Check if a file is a valid YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        True if the file is valid YAML, False otherwise.

    Raises:
        None: All exceptions are caught and logged.
    """
    path = Path(path)
    logger.debug(f"Checking if {path} is valid YAML")

    if not path.is_file():
        logger.warning(f"File does not exist: {path}")
        return False

    try:
        with path.open("r", encoding="utf-8") as file:
            yaml.safe_load(file)
            logger.debug(f"YAML validation successful: {path}")
            return True
    except yaml.YAMLError as e:
        logger.warning(f"Invalid YAML file: {path} - Error: {e}")
        return False
    except OSError as e:
        logger.warning(f"Error reading file: {path} - Error: {e}")
        return False
    except Exception as e:
        logger.warning(f"Unexpected error validating YAML: {path} - Error: {e}")
        return False


@contextmanager
def run_within_dir(path: str | Path) -> Generator[None, None, None]:
    """Context manager to temporarily change the working directory.

    Args:
        path: Directory to change to.

    Yields:
        None: This function yields control back to the caller.

    Raises:
        OSError: If the directory cannot be changed.
    """
    path = Path(path)
    oldpwd = Path.cwd()
    logger.debug(f"Changing directory from {oldpwd} to {path}")

    try:
        os.chdir(path)
        logger.debug(f"Successfully changed to directory: {path}")
        yield
    except OSError as e:
        logger.error(f"Failed to change to directory {path}: {e}")
        raise
    finally:
        logger.debug(f"Changing back to original directory: {oldpwd}")
        os.chdir(oldpwd)


def file_contains_text(file: str | Path, text: str) -> bool:
    """Check if a file contains specific text.

    Args:
        file: Path to the file.
        text: Text to search for.

    Returns:
        True if the text is found, False otherwise.

    Raises:
        None: All exceptions are caught and logged.
    """
    file_path = Path(file)
    logger.debug(f"Checking if file {file_path} contains text: '{text[:20]}...' (truncated)")

    if not file_path.is_file():
        logger.warning(f"File does not exist: {file_path}")
        return False

    try:
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read()
            found = text in content
            logger.debug(f"Text {'found' if found else 'not found'} in {file_path}")
            return found
    except UnicodeDecodeError as e:
        logger.warning(f"Unicode decode error in {file_path}: {e}")
        return False
    except OSError as e:
        logger.warning(f"Error reading file {file_path}: {e}")
        return False
    except Exception as e:
        logger.warning(f"Unexpected error checking file contents {file_path}: {e}")
        return False


def ensure_directory_exists(directory: str | Path) -> bool:
    """Ensure that a directory exists, creating it if necessary.

    Args:
        directory: Directory path to ensure exists.

    Returns:
        True if the directory exists or was created, False otherwise.

    Raises:
        None: All exceptions are caught and logged.
    """
    dir_path = Path(directory)
    logger.debug(f"Ensuring directory exists: {dir_path}")

    try:
        if dir_path.exists():
            if dir_path.is_dir():
                logger.debug(f"Directory already exists: {dir_path}")
                return True
            else:
                logger.warning(f"Path exists but is not a directory: {dir_path}")
                return False

        dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {dir_path}")
        return True
    except OSError as e:
        logger.error(f"Failed to create directory {dir_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating directory {dir_path}: {e}")
        return False
