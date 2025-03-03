"""Tests for the cookiecutter template."""

import shutil
import subprocess

import pytest

from tests.utils import file_contains_text, is_valid_yaml, run_within_dir


def test_bake_project(cookies):
    """Test that the cookiecutter template bakes successfully."""
    result = cookies.bake(extra_context={"project_name": "my-project"})

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.name == "my-project"
    assert result.project_path.is_dir()


def test_using_pytest(cookies, tmp_path):
    """Test that the generated project passes its own tests."""
    with run_within_dir(tmp_path):
        result = cookies.bake()

        # Assert that project was created.
        assert result.exit_code == 0
        assert result.exception is None
        assert result.project_path.name == "example-project"
        assert result.project_path.is_dir()
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        # Install the uv environment and run the tests.
        with run_within_dir(str(result.project_path)):
            uv_path = shutil.which("uv")
            assert subprocess.run([uv_path, "sync"], check=True).returncode == 0
            assert subprocess.run([uv_path, "run", "make", "test"], check=True).returncode == 0
            assert subprocess.run([uv_path, "run", "make", "test"], check=True).returncode == 0


def test_src_layout_using_pytest(cookies, tmp_path):
    """Test that the src layout project passes its own tests."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"layout": "src"})

        # Assert that project was created.
        assert result.exit_code == 0
        assert result.exception is None
        assert result.project_path.name == "example-project"
        assert result.project_path.is_dir()
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")

        # Install the uv environment and run the tests.
        with run_within_dir(str(result.project_path)):
            uv_path = shutil.which("uv")
            assert subprocess.run([uv_path, "sync"], check=True).returncode == 0
            assert subprocess.run([uv_path, "run", "make", "test"], check=True).returncode == 0


def test_devcontainer(cookies, tmp_path):
    """Test that the devcontainer files are created when devcontainer=y."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"devcontainer": "y"})
        assert result.exit_code == 0
        assert (result.project_path / ".devcontainer" / "devcontainer.json").is_file()
        assert (result.project_path / ".devcontainer" / "postCreateCommand.sh").is_file()


def test_not_devcontainer(cookies, tmp_path):
    """Test that the devcontainer files are not created when devcontainer=n."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"devcontainer": "n"})
        assert result.exit_code == 0
        assert not (result.project_path / ".devcontainer" / "devcontainer.json").is_file()
        assert not (result.project_path / ".devcontainer" / "postCreateCommand.sh").is_file()


def test_cicd_contains_pypi_secrets(cookies, tmp_path):
    """Test that PyPI publishing is set up correctly when publish_to_pypi=y."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"publish_to_pypi": "y"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert file_contains_text(result.project_path / ".github" / "workflows" / "on-release-main.yml", "PYPI_TOKEN")
        assert file_contains_text(result.project_path / "Makefile", "build-and-publish")


def test_dont_publish(cookies, tmp_path):
    """Test that PyPI publishing is not set up when publish_to_pypi=n."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"publish_to_pypi": "n"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert not file_contains_text(
            result.project_path / ".github" / "workflows" / "on-release-main.yml", "make build-and-publish"
        )


def test_mkdocs(cookies, tmp_path):
    """Test that MkDocs is set up correctly when mkdocs=y."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"mkdocs": "y"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert file_contains_text(
            result.project_path / ".github" / "workflows" / "on-release-main.yml", "mkdocs gh-deploy"
        )
        assert file_contains_text(result.project_path / "Makefile", "docs:")
        assert (result.project_path / "docs").is_dir()


def test_not_mkdocs(cookies, tmp_path):
    """Test that MkDocs is not set up when mkdocs=n."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"mkdocs": "n"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert not file_contains_text(
            result.project_path / ".github" / "workflows" / "on-release-main.yml", "mkdocs gh-deploy"
        )
        assert not file_contains_text(result.project_path / "Makefile", "docs:")
        assert not (result.project_path / "docs").is_dir()


def test_tox(cookies, tmp_path):
    """Test that tox is configured."""
    with run_within_dir(tmp_path):
        result = cookies.bake()
        assert result.exit_code == 0
        assert (result.project_path / "tox.ini").is_file()
        assert file_contains_text(result.project_path / "tox.ini", "[tox]")


def test_dockerfile(cookies, tmp_path):
    """Test that Dockerfile is created when dockerfile=y."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"dockerfile": "y"})
        assert result.exit_code == 0
        assert (result.project_path / "Dockerfile").is_file()


def test_not_dockerfile(cookies, tmp_path):
    """Test that Dockerfile is not created when dockerfile=n."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"dockerfile": "n"})
        assert result.exit_code == 0
        assert not (result.project_path / "Dockerfile").is_file()


def test_codecov(cookies, tmp_path):
    """Test that codecov is set up."""
    with run_within_dir(tmp_path):
        result = cookies.bake()
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert (result.project_path / "codecov.yaml").is_file()
        assert (result.project_path / ".github" / "workflows" / "validate-codecov-config.yml").is_file()


def test_not_codecov(cookies, tmp_path):
    """Test that codecov is not set up when codecov=n."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"codecov": "n"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert not (result.project_path / "codecov.yaml").is_file()
        assert not (result.project_path / ".github" / "workflows" / "validate-codecov-config.yml").is_file()


def test_remove_release_workflow(cookies, tmp_path):
    """Test that release workflow is handled appropriately."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"publish_to_pypi": "n", "mkdocs": "y"})
        assert result.exit_code == 0
        assert (result.project_path / ".github" / "workflows" / "on-release-main.yml").is_file()

        result = cookies.bake(extra_context={"publish_to_pypi": "n", "mkdocs": "n"})
        assert result.exit_code == 0
        assert not (result.project_path / ".github" / "workflows" / "on-release-main.yml").is_file()


@pytest.mark.parametrize(
    "license_type,expected_line_count",
    [
        ("MIT license", 21),
        ("BSD license", 28),
        ("ISC license", 7),
        ("Apache Software License 2.0", 202),
        ("GNU General Public License v3", 674),
    ],
)
def test_license_types(cookies, tmp_path, license_type, expected_line_count):
    """Test that the different license types work correctly."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"open_source_license": license_type})
        assert result.exit_code == 0

        license_path = result.project_path / "LICENSE"
        assert license_path.is_file()

        # Check that no other license files exist
        for unwanted_license in ["LICENSE_MIT", "LICENSE_BSD", "LICENSE_ISC", "LICENSE_APACHE", "LICENSE_GPL"]:
            assert not (result.project_path / unwanted_license).exists()

        # Check the content length of the license file
        with open(license_path, encoding="utf8") as licfile:
            content = licfile.readlines()
            assert len(content) == expected_line_count


def test_license_no_license(cookies, tmp_path):
    """Test that no license files are created when not open source."""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"open_source_license": "Not open source"})
        assert result.exit_code == 0

        # Check that no license files exist
        for unwanted_license in [
            "LICENSE",
            "LICENSE_MIT",
            "LICENSE_BSD",
            "LICENSE_ISC",
            "LICENSE_APACHE",
            "LICENSE_GPL",
        ]:
            assert not (result.project_path / unwanted_license).exists()
