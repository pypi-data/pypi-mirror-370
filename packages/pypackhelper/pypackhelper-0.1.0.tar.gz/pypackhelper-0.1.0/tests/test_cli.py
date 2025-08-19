"""
Tests for PyPackHelper CLI module.
"""

from typer.testing import CliRunner

from pyph.cli import app

runner = CliRunner()


def test_cli_help():
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "PyPackHelper" in result.stdout


def test_init_command_help():
    """Test init command help."""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "Initialize a new Python package" in result.stdout


def test_validate_command_help():
    """Test validate command help."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Validate package code" in result.stdout


def test_bump_command_help():
    """Test bump command help."""
    result = runner.invoke(app, ["bump", "--help"])
    assert result.exit_code == 0
    assert "Bump package version" in result.stdout


def test_upload_command_help():
    """Test upload command help."""
    result = runner.invoke(app, ["upload", "--help"])
    assert result.exit_code == 0
    assert "Upload package to PyPI" in result.stdout


def test_version_command_help():
    """Test version command help."""
    result = runner.invoke(app, ["version", "--help"])
    assert result.exit_code == 0
    assert "Show current package version" in result.stdout


def test_build_command_help():
    """Test build command help."""
    result = runner.invoke(app, ["build", "--help"])
    assert result.exit_code == 0
    assert "Build package distributions" in result.stdout


def test_clean_command_help():
    """Test clean command help."""
    result = runner.invoke(app, ["clean", "--help"])
    assert result.exit_code == 0
    assert "Clean build directories" in result.stdout


def test_init_package_basic(temp_dir):
    """Test basic package initialization."""
    result = runner.invoke(
        app,
        [
            "init",
            "testpkg",
            "--path",
            str(temp_dir),
            "--author",
            "Test Author",
            "--email",
            "test@example.com",
        ],
    )

    # Should succeed
    assert result.exit_code == 0

    # Check if package directory was created
    package_dir = temp_dir / "testpkg"
    assert package_dir.exists()
    assert (package_dir / "testpkg").exists()
    assert (package_dir / "setup.py").exists()
    assert (package_dir / "README.md").exists()


def test_init_package_already_exists(temp_dir):
    """Test initialization when package already exists."""
    # Create directory first
    (temp_dir / "testpkg").mkdir()

    result = runner.invoke(app, ["init", "testpkg", "--path", str(temp_dir)])

    # Should fail
    assert result.exit_code == 1
    assert "already exists" in result.stdout


def test_bump_invalid_version_type(sample_package_dir):
    """Test bump with invalid version type."""
    result = runner.invoke(app, ["bump", "invalid", "--path", str(sample_package_dir)])

    assert result.exit_code == 1
    assert "must be 'major', 'minor', or 'patch'" in result.stdout


def test_version_command(sample_package_dir):
    """Test version command."""
    result = runner.invoke(app, ["version", "--path", str(sample_package_dir)])

    assert result.exit_code == 0
    assert "Current version:" in result.stdout
