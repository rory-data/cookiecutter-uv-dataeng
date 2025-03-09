"""Pre-generation script for cookiecutter template.

This script runs before the cookiecutter template is generated. It validates project
name and slug, and modifies the cookiecutter.json file based on operating system.
"""

import logging
import platform
import re
import sys
from typing import Final

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Constants defined as Final for better type checking
PROJECT_NAME_REGEX: Final[str] = r"^[-a-zA-Z][-a-zA-Z0-9]+$"
PROJECT_SLUG_REGEX: Final[str] = r"^[_a-zA-Z][_a-zA-Z0-9]+$"


def validate_project_name(name: str) -> bool:
    """Validate that the project name meets requirements.

    Args:
        name: Project name to validate.

    Returns:
        True if the project name is valid, False otherwise.
    """
    logger.debug(f"Validating project name: {name}")
    valid = bool(re.match(PROJECT_NAME_REGEX, name))
    if not valid:
        logger.warning(f"Invalid project name: {name}")
    return valid


def validate_project_slug(slug: str) -> bool:
    """Validate that the project slug meets requirements.

    Args:
        slug: Project slug to validate.

    Returns:
        True if the project slug is valid, False otherwise.
    """
    logger.debug(f"Validating project slug: {slug}")
    valid = bool(re.match(PROJECT_SLUG_REGEX, slug))
    if not valid:
        logger.warning(f"Invalid project slug: {slug}")
    return valid


def main() -> None:
    """Main function to run the pre-generation script."""
    logger.info("Starting pre-generation script")

    # Detect the operating system
    operating_system = platform.system()
    logger.info(f"Detected operating system: {operating_system}")

    # Validate project name
    project_name = "{{cookiecutter.project_name}}"
    logger.info(f"Validating project name: {project_name}")
    if not validate_project_name(project_name):
        error_msg = (
            f"ERROR: The project name {project_name!r} is not a valid Python module name. "
            "Please do not use a _ and use - instead"
        )
        logger.error(f"Error: {error_msg}")
        # Exit to cancel project
        sys.exit(1)

    # Validate project slug
    project_slug = "{{cookiecutter.project_slug}}"
    logger.info(f"Validating project slug: {project_slug}")
    if not validate_project_slug(project_slug):
        error_msg = (
            f"ERROR: The project slug {project_slug!r} is not a valid Python module name. "
            "Please do not use a - and use _ instead"
        )
        logger.error(f"Error: {error_msg}")
        # Exit to cancel project
        sys.exit(1)

    logger.info("Pre-generation script completed successfully")


if __name__ == "__main__":
    main()
