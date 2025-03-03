"""Utility functions for testing."""

import os
from contextlib import contextmanager
from pathlib import Path

import yaml


def is_valid_yaml(path: str | Path) -> bool:
    """
    Check if a file is a valid YAML file.

    Args:
        path: Path to the YAML file

    Returns:
        True if the file is valid YAML, False otherwise
    """
    path = Path(path)

    if not path.is_file():
        print(f"File does not exist: {path}")
        return False

    try:
        with path.open("r", encoding="utf-8") as file:
            yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Invalid YAML file: {path} - Error: {e}")
        return False
    except OSError as e:
        print(f"Error reading file: {path} - Error: {e}")
        return False

    return True


@contextmanager
def run_within_dir(path: str | Path):
    """
    Context manager to temporarily change the working directory.

    Args:
        path: Directory to change to
    """
    path = Path(path)
    oldpwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def file_contains_text(file: str | Path, text: str) -> bool:
    """
    Check if a file contains specific text.

    Args:
        file: Path to the file
        text: Text to search for

    Returns:
        True if the text is found, False otherwise
    """
    file_path = Path(file)
    with file_path.open("r", encoding="utf-8") as f:
        return text in f.read()
