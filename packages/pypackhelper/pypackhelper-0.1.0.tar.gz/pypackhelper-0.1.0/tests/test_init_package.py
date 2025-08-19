"""
Tests for package initialization module.
"""

import pytest

from pyph.init_package import PackageInitializer


def test_package_initializer_creation():
    """Test PackageInitializer creation."""
    initializer = PackageInitializer(
        name="testpackage", author="Test Author", email="test@example.com"
    )

    assert initializer.name == "testpackage"
    assert initializer.author == "Test Author"
    assert initializer.email == "test@example.com"


def test_package_initializer_defaults():
    """Test PackageInitializer with defaults."""
    initializer = PackageInitializer(name="testpackage")

    assert initializer.name == "testpackage"
    assert initializer.author == "Your Name"
    assert initializer.email == "your.email@example.com"
    assert initializer.license_type == "MIT"
    assert initializer.github_actions is True


def test_create_package_structure(temp_dir):
    """Test package structure creation."""
    initializer = PackageInitializer(
        name="mypackage", author="Test Author", email="test@example.com"
    )

    package_path = initializer.create_package(temp_dir)

    # Check main directory
    assert package_path.exists()
    assert package_path.name == "mypackage"

    # Check package structure
    assert (package_path / "mypackage").exists()
    assert (package_path / "tests").exists()
    assert (package_path / "docs").exists()

    # Check files
    assert (package_path / "setup.py").exists()
    assert (package_path / "pyproject.toml").exists()
    assert (package_path / "README.md").exists()
    assert (package_path / "LICENSE").exists()
    assert (package_path / ".gitignore").exists()

    # Check package files
    assert (package_path / "mypackage" / "__init__.py").exists()
    assert (package_path / "mypackage" / "main.py").exists()
    assert (package_path / "mypackage" / "cli.py").exists()

    # Check test files
    assert (package_path / "tests" / "__init__.py").exists()
    assert (package_path / "tests" / "conftest.py").exists()
    assert (package_path / "tests" / "test_main.py").exists()


def test_create_package_existing_directory(temp_dir):
    """Test creation fails when directory exists."""
    # Create directory first
    (temp_dir / "existing").mkdir()

    initializer = PackageInitializer(name="existing")

    with pytest.raises(ValueError, match="already exists"):
        initializer.create_package(temp_dir)


def test_github_actions_workflow(temp_dir):
    """Test GitHub Actions workflow creation."""
    initializer = PackageInitializer(name="mypackage", github_actions=True)

    package_path = initializer.create_package(temp_dir)

    # Check GitHub Actions files
    assert (package_path / ".github").exists()
    assert (package_path / ".github" / "workflows").exists()
    assert (package_path / ".github" / "workflows" / "ci.yml").exists()

    # Check workflow content
    workflow_content = (package_path / ".github" / "workflows" / "ci.yml").read_text()
    assert "Test and Deploy" in workflow_content
    assert "python-version:" in workflow_content


def test_no_github_actions(temp_dir):
    """Test package creation without GitHub Actions."""
    initializer = PackageInitializer(name="mypackage", github_actions=False)

    package_path = initializer.create_package(temp_dir)

    # Should not create GitHub Actions
    assert not (package_path / ".github").exists()


def test_license_content(temp_dir):
    """Test LICENSE file content."""
    initializer = PackageInitializer(
        name="mypackage", author="Test Author", license_type="MIT"
    )

    package_path = initializer.create_package(temp_dir)

    license_content = (package_path / "LICENSE").read_text()
    assert "MIT License" in license_content
    assert "Test Author" in license_content
    assert str(initializer.current_year) in license_content


def test_custom_license(temp_dir):
    """Test custom license type."""
    initializer = PackageInitializer(name="mypackage", license_type="Apache-2.0")

    package_path = initializer.create_package(temp_dir)

    license_content = (package_path / "LICENSE").read_text()
    assert "Apache-2.0" in license_content


def test_setup_py_content(temp_dir):
    """Test setup.py content."""
    initializer = PackageInitializer(
        name="mypackage",
        author="Test Author",
        email="test@example.com",
        description="Test package description",
    )

    package_path = initializer.create_package(temp_dir)

    setup_content = (package_path / "setup.py").read_text()
    assert 'name="mypackage"' in setup_content
    assert 'author="Test Author"' in setup_content
    assert 'author_email="test@example.com"' in setup_content
    assert 'description="Test package description"' in setup_content


def test_pyproject_toml_content(temp_dir):
    """Test pyproject.toml content."""
    initializer = PackageInitializer(
        name="mypackage", author="Test Author", email="test@example.com"
    )

    package_path = initializer.create_package(temp_dir)

    pyproject_content = (package_path / "pyproject.toml").read_text()
    assert 'name = "mypackage"' in pyproject_content
    assert 'name = "Test Author"' in pyproject_content
    assert 'email = "test@example.com"' in pyproject_content
