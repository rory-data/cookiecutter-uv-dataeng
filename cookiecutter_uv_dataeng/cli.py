"""Command-line interface for cookiecutter-uv-dataeng.

This module provides a command-line interface to generate a new data engineering
project using the cookiecutter-uv-dataeng template. It handles direct execution
of the cookiecutter template without requiring users to remember the full path.
"""

import logging
import sys
from pathlib import Path
from typing import Never

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("cookiecutter_cli.log", mode="w", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def exit_with_error(message: str, exit_code: int = 1) -> Never:
    """Exit the program with an error message.

    Args:
        message: The error message to display.
        exit_code: The exit code to use (defaults to 1).

    Returns:
        This function does not return (NoReturn).
    """
    logger.error(f"Error: {message}")
    sys.exit(exit_code)


def get_template_path() -> Path:
    """Get the path to the cookiecutter template.

    Returns:
        Path object pointing to the template directory.

    Raises:
        FileNotFoundError: If the template directory cannot be found.
    """
    try:
        current_dir = Path(__file__).parent
        package_dir = current_dir.parent.resolve()

        if not package_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {package_dir}")

        logger.debug(f"Template directory: {package_dir}")
        return package_dir
    except Exception as e:
        logger.error(f"Failed to locate template directory: {e}", exc_info=True)
        raise


def run_cookiecutter(template_path: Path, extra_context: dict | None = None) -> bool:
    """Run cookiecutter with the specified template.

    Args:
        template_path: Path to the cookiecutter template directory.
        extra_context: Optional dictionary of context variables to override defaults.

    Returns:
        True if the template was successfully generated, False otherwise.

    Raises:
        ImportError: If cookiecutter is not installed.
        Exception: For any other errors during template generation.
    """
    try:
        from cookiecutter.main import cookiecutter

        logger.info(f"Generating project from template: {template_path}")
        cookiecutter(
            str(template_path),
            extra_context=extra_context or {},
        )
        logger.info("Project generated successfully")
        return True
    except ImportError as err:
        logger.error("Cookiecutter package is not installed")
        raise ImportError("Cookiecutter is not installed.") from err
    except Exception as e:
        logger.error(f"Error generating project: {e}", exc_info=True)
        raise


def main() -> None:
    """Run the cookiecutter template from the command line.

    This function handles locating the template directory and executing cookiecutter
    to generate a new project. It includes error handling for common issues.

    Returns:
        None
    """
    logger.info("Starting cookiecutter-uv-dataeng CLI")

    try:
        # Get the template directory
        template_path = get_template_path()

        # Run cookiecutter with the template
        run_cookiecutter(template_path)

        logger.info("CLI completed successfully")
    except ImportError as e:
        exit_with_error(str(e))
    except FileNotFoundError as e:
        exit_with_error(f"Template not found: {e}")
    except Exception as e:
        exit_with_error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
