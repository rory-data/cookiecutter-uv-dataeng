"""Tests for the cookiecutter template.

This module contains tests to verify that the cookiecutter template generates
projects correctly with all the configured options.
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tests.utils import file_contains_text, is_valid_yaml, run_within_dir

# Configure logging
logger = logging.getLogger(__name__)


def assert_project_creation(result: Any, project_name: str) -> None:
    """Assert that the project was created successfully."""
    assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
    assert result.exception is None, f"Expected no exception, got {result.exception}"
    assert result.project_path.name == project_name, (
        f"Expected project name '{project_name}', got {result.project_path.name}"
    )
    assert result.project_path.is_dir(), f"Expected {result.project_path} to be a directory"


def run_uv_command(project_path: Path, command: list[str]) -> subprocess.CompletedProcess:
    """Run a uv command within the generated project."""
    uv_path = shutil.which("uv")
    if uv_path is None:
        raise OSError("UV executable not found in PATH")

    logger.info(f"Using UV from {uv_path}")
    logger.info(f"Running uv command: {' '.join(command)}")

    result = subprocess.run(
        [uv_path, *command],
        cwd=str(project_path),
        check=True,
        capture_output=True,
        text=True,
    )
    logger.debug(f"Command output: {result.stdout}")
    logger.debug(f"Command error: {result.stderr}")
    return result


def test_bake_project(cookies: Any) -> None:
    """Test that the cookiecutter template bakes successfully."""
    logger.info("Testing basic project generation")

    try:
        result = cookies.bake(extra_context={"project_name": "my-project"})
        assert_project_creation(result, "my-project")
        logger.info("Basic project generation successful")
    except Exception as e:
        logger.error(f"Project generation failed: {e}", exc_info=True)
        raise


def test_using_pytest(cookies: Any, tmp_path: Path) -> None:
    """Test that the generated project passes its own tests."""
    logger.info("Testing that generated project passes its own tests")

    with run_within_dir(tmp_path):
        try:
            result = cookies.bake()
            assert_project_creation(result, "example-project")

            workflow_path = result.project_path / ".github" / "workflows" / "main.yml"
            assert is_valid_yaml(workflow_path), f"Expected valid YAML at {workflow_path}"

            logger.info("Project structure verified, running tests")

            # Install the uv environment and run the tests.
            with run_within_dir(str(result.project_path)):
                # Sync dependencies
                logger.info("Syncing UV dependencies")
                run_uv_command(result.project_path, ["sync"])

                # Run tests
                logger.info("Running tests in generated project")
                run_uv_command(result.project_path, ["run", "make", "test"])

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.cmd} (exit code {e.returncode})")
            logger.error(f"Command output: {e.stdout}")
            logger.error(f"Command error: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise


def test_mkdocs(cookies: Any, tmp_path: Path) -> None:
    """Test that MkDocs is set up correctly when mkdocs=y."""
    logger.info("Testing MkDocs setup")

    with run_within_dir(tmp_path):
        try:
            result = cookies.bake(extra_context={"mkdocs": "y"})
            assert_project_creation(result, "example-project")

            main_workflow = result.project_path / ".github" / "workflows" / "main.yml"
            release_workflow = result.project_path / ".github" / "workflows" / "on-release-main.yml"

            assert is_valid_yaml(main_workflow), f"Expected valid YAML at {main_workflow}"
            assert is_valid_yaml(release_workflow), f"Expected valid YAML at {release_workflow}"

            assert file_contains_text(release_workflow, "mkdocs gh-deploy"), (
                "Expected mkdocs gh-deploy in release workflow"
            )
            assert file_contains_text(result.project_path / "Makefile", "docs:"), "Expected docs target in Makefile"
            assert (result.project_path / "docs").is_dir(), "Expected docs directory to be created"

            logger.info("MkDocs setup verified")
        except Exception as e:
            logger.error(f"MkDocs test failed: {e}", exc_info=True)
            raise


def test_not_mkdocs(cookies: Any, tmp_path: Path) -> None:
    """Test that MkDocs is not set up when mkdocs=n."""
    logger.info("Testing MkDocs disabled")

    with run_within_dir(tmp_path):
        try:
            result = cookies.bake(extra_context={"mkdocs": "n"})
            assert_project_creation(result, "example-project")

            main_workflow = result.project_path / ".github" / "workflows" / "main.yml"
            release_workflow = result.project_path / ".github" / "workflows" / "on-release-main.yml"

            assert is_valid_yaml(main_workflow), f"Expected valid YAML at {main_workflow}"
            assert is_valid_yaml(release_workflow), f"Expected valid YAML at {release_workflow}"

            assert not file_contains_text(release_workflow, "mkdocs gh-deploy"), (
                "Unexpected mkdocs gh-deploy in release workflow"
            )
            assert not file_contains_text(result.project_path / "Makefile", "docs:"), (
                "Unexpected docs target in Makefile"
            )
            assert not (result.project_path / "docs").is_dir(), "Unexpected docs directory found"

            logger.info("Verified MkDocs is disabled")
        except Exception as e:
            logger.error(f"No MkDocs test failed: {e}", exc_info=True)
            raise


def test_codecov(cookies: Any, tmp_path: Path) -> None:
    """Test that codecov is set up."""
    logger.info("Testing Codecov setup")

    with run_within_dir(tmp_path):
        try:
            result = cookies.bake()
            assert_project_creation(result, "example-project")

            workflow_path = result.project_path / ".github" / "workflows" / "main.yml"
            codecov_config = result.project_path / "codecov.yaml"
            codecov_workflow = result.project_path / ".github" / "workflows" / "validate-codecov-config.yml"

            assert is_valid_yaml(workflow_path), f"Expected valid YAML at {workflow_path}"
            assert codecov_config.is_file(), f"Expected codecov.yaml at {codecov_config}"
            assert codecov_workflow.is_file(), f"Expected codecov validation workflow at {codecov_workflow}"

            logger.info("Codecov configuration verified")
        except Exception as e:
            logger.error(f"Codecov test failed: {e}", exc_info=True)
            raise


def test_not_codecov(cookies: Any, tmp_path: Path) -> None:
    """Test that codecov is not set up when codecov=n."""
    logger.info("Testing Codecov disabled")

    with run_within_dir(tmp_path):
        try:
            result = cookies.bake(extra_context={"codecov": "n"})
            assert_project_creation(result, "example-project")

            workflow_path = result.project_path / ".github" / "workflows" / "main.yml"
            codecov_config = result.project_path / "codecov.yaml"
            codecov_workflow = result.project_path / ".github" / "workflows" / "validate-codecov-config.yml"

            assert is_valid_yaml(workflow_path), f"Expected valid YAML at {workflow_path}"
            assert not codecov_config.is_file(), f"Unexpected codecov.yaml at {codecov_config}"
            assert not codecov_workflow.is_file(), f"Unexpected codecov validation workflow at {codecov_workflow}"

            logger.info("Verified Codecov is disabled")
        except Exception as e:
            logger.error(f"No Codecov test failed: {e}", exc_info=True)
            raise


@pytest.mark.parametrize(
    ("license_type", "expected_line_count"),
    [
        ("MIT license", 21),
        ("BSD license", 28),
        ("ISC license", 7),
        ("Apache Software License 2.0", 202),
        ("GNU General Public License v3", 674),
    ],
)
def test_license_types(cookies: Any, tmp_path: Path, license_type: str, expected_line_count: int) -> None:
    """Test that the different license types work correctly."""
    logger.info(f"Testing license type: {license_type}")

    with run_within_dir(tmp_path):
        try:
            result = cookies.bake(extra_context={"open_source_license": license_type})
            assert_project_creation(result, "example-project")

            license_path = result.project_path / "LICENSE"
            assert license_path.is_file(), f"Expected LICENSE file at {license_path}"

            # Check that no other license files exist
            for unwanted_license in ["LICENSE_MIT", "LICENSE_BSD", "LICENSE_ISC", "LICENSE_APACHE", "LICENSE_GPL"]:
                unwanted_path = result.project_path / unwanted_license
                assert not unwanted_path.exists(), f"Unexpected license file: {unwanted_path}"

            # Check the content length of the license file
            with open(license_path, encoding="utf8") as licfile:
                content = licfile.readlines()
                assert len(content) == expected_line_count, (
                    f"Expected {expected_line_count} lines in {license_type} file, got {len(content)}"
                )

            logger.info(f"License {license_type} verified")
        except Exception as e:
            logger.error(f"License test failed for {license_type}: {e}", exc_info=True)
            raise


def test_license_no_license(cookies: Any, tmp_path: Path) -> None:
    """Test that no license files are created when not open source."""
    logger.info("Testing no license option")

    with run_within_dir(tmp_path):
        try:
            result = cookies.bake(extra_context={"open_source_license": "Not open source"})
            assert_project_creation(result, "example-project")

            # Check that no license files exist
            for unwanted_license in [
                "LICENSE",
                "LICENSE_MIT",
                "LICENSE_BSD",
                "LICENSE_ISC",
                "LICENSE_APACHE",
                "LICENSE_GPL",
            ]:
                unwanted_path = result.project_path / unwanted_license
                assert not unwanted_path.exists(), f"Unexpected license file: {unwanted_path}"

            logger.info("Verified no license files were created")
        except Exception as e:
            logger.error(f"No license test failed: {e}", exc_info=True)
            raise
