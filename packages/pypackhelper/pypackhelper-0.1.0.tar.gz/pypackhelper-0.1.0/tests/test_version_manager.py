"""
Tests for version management module.
"""

from pathlib import Path

import pytest

from pyph.version_manager import VersionManager


def test_version_manager_creation(sample_package_dir):
    """Test VersionManager creation."""
    vm = VersionManager(sample_package_dir)
    assert vm.package_path == sample_package_dir.resolve()


def test_get_current_version_from_init(sample_package_dir):
    """Test getting version from __init__.py."""
    vm = VersionManager(sample_package_dir)
    version = vm.get_current_version()
    assert version == "0.1.0"


def test_get_current_version_from_pyproject(sample_package_dir):
    """Test getting version from pyproject.toml."""
    # Remove __init__.py version
    init_file = sample_package_dir / "testpackage" / "__init__.py"
    init_file.write_text("# No version here")

    vm = VersionManager(sample_package_dir)
    version = vm.get_current_version()
    assert version == "0.1.0"


def test_calculate_new_version():
    """Test version calculation."""
    vm = VersionManager(Path("."))

    # Test patch bump
    new_version = vm.calculate_new_version("1.0.0", "patch")
    assert new_version == "1.0.1"

    # Test minor bump
    new_version = vm.calculate_new_version("1.0.5", "minor")
    assert new_version == "1.1.0"

    # Test major bump
    new_version = vm.calculate_new_version("1.5.3", "major")
    assert new_version == "2.0.0"


def test_calculate_new_version_invalid_type():
    """Test version calculation with invalid type."""
    vm = VersionManager(Path("."))

    with pytest.raises(ValueError, match="Invalid version type"):
        vm.calculate_new_version("1.0.0", "invalid")


def test_calculate_new_version_invalid_format():
    """Test version calculation with invalid format."""
    vm = VersionManager(Path("."))

    with pytest.raises(ValueError, match="Invalid version format"):
        vm.calculate_new_version("invalid", "patch")


def test_bump_version(sample_package_dir):
    """Test version bumping."""
    vm = VersionManager(sample_package_dir)

    # Bump patch version
    new_version = vm.bump_version("patch")
    assert new_version == "0.1.1"

    # Verify version was updated
    updated_version = vm.get_current_version()
    assert updated_version == "0.1.1"


def test_validate_version_consistency_consistent(sample_package_dir):
    """Test version consistency validation when versions match."""
    vm = VersionManager(sample_package_dir)
    assert vm.validate_version_consistency() is True


def test_validate_version_consistency_inconsistent(sample_package_dir):
    """Test version consistency validation when versions don't match."""
    # Change version in one file
    pyproject_content = """
[project]
name = "testpackage"
version = "0.2.0"
description = "Test package"
"""
    (sample_package_dir / "pyproject.toml").write_text(pyproject_content)

    vm = VersionManager(sample_package_dir)
    assert vm.validate_version_consistency() is False


def test_list_versions(sample_package_dir):
    """Test listing all versions."""
    vm = VersionManager(sample_package_dir)
    versions = vm.list_versions()

    assert len(versions) >= 2  # Should find versions in multiple files

    # Check that we found versions
    version_values = [v["version"] for v in versions]
    assert "0.1.0" in version_values


def test_update_pyproject_version(sample_package_dir):
    """Test updating pyproject.toml version."""
    vm = VersionManager(sample_package_dir)
    vm._update_pyproject_version("1.2.3")

    # Check that version was updated
    pyproject_content = (sample_package_dir / "pyproject.toml").read_text()
    assert 'version = "1.2.3"' in pyproject_content


def test_update_setup_py_version(sample_package_dir):
    """Test updating setup.py version."""
    vm = VersionManager(sample_package_dir)
    vm._update_setup_py_version("0.1.0", "1.2.3")

    # Check that version was updated
    setup_content = (sample_package_dir / "setup.py").read_text()
    assert 'version="1.2.3"' in setup_content


def test_update_init_version(sample_package_dir):
    """Test updating __init__.py version."""
    init_file = sample_package_dir / "testpackage" / "__init__.py"
    vm = VersionManager(sample_package_dir)
    vm._update_init_version(init_file, "0.1.0", "1.2.3")

    # Check that version was updated
    init_content = init_file.read_text()
    assert '__version__ = "1.2.3"' in init_content
