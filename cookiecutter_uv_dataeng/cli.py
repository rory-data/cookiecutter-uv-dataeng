"""Command-line interface for cookiecutter-uv-dataeng."""

import sys
from pathlib import Path


def main() -> None:
    """Run the cookiecutter template from the command line."""
    # Use pathlib for more modern path handling
    current_dir = Path(__file__).parent
    package_dir = current_dir.parent.resolve()

    # Use Python's importlib to run cookiecutter directly instead of subprocess
    try:
        from cookiecutter.main import cookiecutter

        cookiecutter(str(package_dir))
    except ImportError:
        print("Cookiecutter is not installed. Please install it with: pip install cookiecutter")
        sys.exit(1)


if __name__ == "__main__":
    main()
