"""
Tests for package validation module.
"""

from pathlib import Path

from pyph.validator import PackageValidator


def test_validator_creation(sample_package_dir):
    """Test PackageValidator creation."""
    validator = PackageValidator(sample_package_dir)
    assert validator.package_path == sample_package_dir.resolve()
    assert validator.strict is False
    assert validator.errors == []
    assert validator.warnings == []


def test_validator_strict_mode(sample_package_dir):
    """Test PackageValidator in strict mode."""
    validator = PackageValidator(sample_package_dir, strict=True)
    assert validator.strict is True


def test_validate_package_structure_success(sample_package_dir):
    """Test successful package structure validation."""
    # Add required files
    (sample_package_dir / "README.md").write_text("# Test Package")
    (sample_package_dir / "LICENSE").write_text("MIT License")

    validator = PackageValidator(sample_package_dir)
    result = validator._validate_package_structure()

    assert result is True


def test_validate_package_structure_missing_files(temp_dir):
    """Test package structure validation with missing files."""
    # Create minimal package
    package_dir = temp_dir / "testpkg"
    package_dir.mkdir()
    (package_dir / "testpkg").mkdir()
    (package_dir / "testpkg" / "__init__.py").write_text("")

    validator = PackageValidator(package_dir)
    validator._validate_package_structure()

    # Should have warnings for missing files
    assert len(validator.warnings) > 0


def test_validate_package_structure_no_package_dir(temp_dir):
    """Test validation with no package directory."""
    validator = PackageValidator(temp_dir)
    result = validator._validate_package_structure()

    assert result is False
    assert any("No package directory found" in error for error in validator.errors)


def test_find_python_files(sample_package_dir):
    """Test finding Python files."""
    validator = PackageValidator(sample_package_dir)
    python_files = validator._find_python_files()

    assert len(python_files) > 0
    # Should find at least the __init__.py file
    init_files = [f for f in python_files if f.name == "__init__.py"]
    assert len(init_files) > 0


def test_find_python_files_empty_dir(temp_dir):
    """Test finding Python files in empty directory."""
    validator = PackageValidator(temp_dir)
    python_files = validator._find_python_files()

    assert len(python_files) == 0


def test_check_command_available():
    """Test command availability checking."""
    validator = PackageValidator(Path("."))

    # Python should be available
    assert validator._check_command_available("python") is True

    # Non-existent command should not be available
    assert validator._check_command_available("nonexistentcommand12345") is False


def test_validate_package_metadata_pyproject(sample_package_dir):
    """Test validating package metadata from pyproject.toml."""
    validator = PackageValidator(sample_package_dir)
    result = validator._validate_package_metadata()

    # Should succeed with basic metadata
    assert result is True


def test_validate_package_metadata_missing_fields(temp_dir):
    """Test validating package metadata with missing fields."""
    # Create package with incomplete metadata
    package_dir = temp_dir / "testpkg"
    package_dir.mkdir()

    # Create pyproject.toml with missing fields
    pyproject_content = """
[project]
name = "testpackage"
# missing version and description
"""
    (package_dir / "pyproject.toml").write_text(pyproject_content)

    validator = PackageValidator(package_dir, strict=True)
    validator._validate_package_metadata()

    # Should have warnings for missing fields
    assert len(validator.warnings) > 0


def test_get_validation_report(sample_package_dir):
    """Test getting validation report."""
    validator = PackageValidator(sample_package_dir)

    # Add some errors and warnings
    validator.errors.append("Test error")
    validator.warnings.append("Test warning")

    report = validator.get_validation_report()

    assert report["success"] is False  # Has errors
    assert report["error_count"] == 1
    assert report["warning_count"] == 1
    assert "Test error" in report["errors"]
    assert "Test warning" in report["warnings"]


def test_get_validation_report_success(sample_package_dir):
    """Test getting validation report with no errors."""
    validator = PackageValidator(sample_package_dir)

    report = validator.get_validation_report()

    assert report["success"] is True
    assert report["error_count"] == 0
    assert report["warning_count"] == 0
