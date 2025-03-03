"""Pre-generation script for cookiecutter template."""

import json
import os
import platform
import re
import sys
from typing import Final

# Constants defined as Final for better type checking
PROJECT_NAME_REGEX: Final = r"^[-a-zA-Z][-a-zA-Z0-9]+$"
PROJECT_SLUG_REGEX: Final = r"^[_a-zA-Z][_a-zA-Z0-9]+$"

# Detect the operating system
operating_system = platform.system()

# Path to the cookiecutter.json file (in parent directory of hooks)
json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookiecutter.json")

try:
    # Load the original cookiecutter.json
    with open(json_path) as f:
        config = json.load(f)

    # Initialize _prompts if it doesn't exist
    if "_prompts" not in config:
        config["_prompts"] = {}

    # OS-specific prompt handling
    if operating_system == "Darwin":  # macOS
        # For macOS, include the Astro CLI prompt
        config["_prompts"]["include_astro_cli"] = "Do you want to initialise Astro CLI in this project? (y/n):"
    elif operating_system == "Windows":
        # For Windows, remove the Astro CLI option completely from prompts
        # and set a default value to skip the prompt
        if "include_astro_cli" in config["_prompts"]:
            del config["_prompts"]["include_astro_cli"]
        config["include_astro_cli"] = "n"  # Default to no for Windows

    # Write the modified cookiecutter.json
    with open(json_path, "w") as f:
        json.dump(config, f, indent=2)

except Exception as e:
    print(f"Error modifying cookiecutter.json: {e!s}")
    sys.exit(1)


# Validate project name
project_name = "{{cookiecutter.project_name}}"
if not re.match(PROJECT_NAME_REGEX, project_name):
    print(
        f"ERROR: The project name {project_name!r} is not a valid Python module name. "
        "Please do not use a _ and use - instead"
    )
    # Exit to cancel project
    sys.exit(1)

# Validate project slug
project_slug = "{{cookiecutter.project_slug}}"
if not re.match(PROJECT_SLUG_REGEX, project_slug):
    print(
        f"ERROR: The project slug {project_slug!r} is not a valid Python module name. "
        "Please do not use a - and use _ instead"
    )
    # Exit to cancel project
    sys.exit(1)
