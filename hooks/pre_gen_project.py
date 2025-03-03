"""Pre-generation script for cookiecutter template.

This script runs before the cookiecutter template is generated. It validates project
name and slug, and modifies the cookiecutter.json file based on operating system.
"""

import json
import logging
import os
import platform
import re
import sys
from typing import Any, Dict, Final

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("cookiecutter_pre_gen.log", mode="w", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# Constants defined as Final for better type checking
PROJECT_NAME_REGEX: Final[str] = r"^[-a-zA-Z][-a-zA-Z0-9]+$"
PROJECT_SLUG_REGEX: Final[str] = r"^[_a-zA-Z][_a-zA-Z0-9]+$"


def load_cookiecutter_config(json_path: str) -> dict[str, Any]:
    """Load the cookiecutter configuration from a JSON file.

    Args:
        json_path: Path to the cookiecutter.json file.

    Returns:
        Dictionary containing the cookiecutter configuration.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If the JSON file is invalid.
    """
    logger.debug(f"Loading cookiecutter configuration from {json_path}")
    try:
        with open(json_path, encoding="utf-8") as f:
            config = json.load(f)
            logger.debug(f"Successfully loaded configuration with {len(config)} keys")
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {json_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        raise


def save_cookiecutter_config(json_path: str, config: dict[str, Any]) -> None:
    """Save the cookiecutter configuration to a JSON file.

    Args:
        json_path: Path to the cookiecutter.json file.
        config: Dictionary containing the cookiecutter configuration.

    Raises:
        PermissionError: If the file cannot be written due to permissions.
        OSError: If there is an OS-level error writing the file.
    """
    logger.debug(f"Saving cookiecutter configuration to {json_path}")
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        logger.debug("Configuration saved successfully")
    except PermissionError:
        logger.error(f"Permission denied when writing to {json_path}")
        raise
    except OSError as e:
        logger.error(f"OS error when writing configuration: {e}")
        raise


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

    # Path to the cookiecutter.json file (in parent directory of hooks)
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookiecutter.json")
    logger.debug(f"Cookiecutter configuration path: {json_path}")

    try:
        # Load the original cookiecutter.json
        logger.info("Loading cookiecutter configuration")
        config = load_cookiecutter_config(json_path)

        # Initialize _prompts if it doesn't exist
        if "_prompts" not in config:
            logger.debug("Initializing _prompts dictionary in configuration")
            config["_prompts"] = {}

        # OS-specific prompt handling
        logger.info("Applying OS-specific configurations")
        if operating_system == "Darwin":  # macOS
            # For macOS, include the Astro CLI prompt
            logger.info("Adding Astro CLI prompt for macOS")
            config["_prompts"]["include_astro_cli"] = "Do you want to initialise Astro CLI in this project? (y/n):"
        elif operating_system == "Windows":
            # For Windows, remove the Astro CLI option completely from prompts
            # and set a default value to skip the prompt
            logger.info("Removing Astro CLI option for Windows")
            if "include_astro_cli" in config["_prompts"]:
                del config["_prompts"]["include_astro_cli"]
            config["include_astro_cli"] = "n"  # Default to no for Windows

        # Write the modified cookiecutter.json
        logger.info("Saving modified cookiecutter configuration")
        save_cookiecutter_config(json_path, config)

    except FileNotFoundError:
        logger.critical(f"Could not find cookiecutter.json at {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.critical(f"Invalid JSON format in cookiecutter.json: {e}")
        sys.exit(1)
    except PermissionError:
        logger.critical(f"Permission denied when writing to {json_path}")
        sys.exit(1)
    except OSError as e:
        logger.critical(f"Error modifying cookiecutter.json: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error modifying cookiecutter.json: {e}", exc_info=True)
        sys.exit(1)

    # Validate project name
    project_name = "{{cookiecutter.project_name}}"
    logger.info(f"Validating project name: {project_name}")
    if not validate_project_name(project_name):
        error_msg = (
            f"ERROR: The project name {project_name!r} is not a valid Python module name. "
            "Please do not use a _ and use - instead"
        )
        logger.error(error_msg)
        print(error_msg)
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
        logger.error(error_msg)
        print(error_msg)
        # Exit to cancel project
        sys.exit(1)

    logger.info("Pre-generation script completed successfully")


if __name__ == "__main__":
    main()
