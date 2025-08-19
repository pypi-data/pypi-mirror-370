"""
Pytest configuration and fixtures for PyPackHelper tests.
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_package_dir(temp_dir):
    """Create a sample package structure for testing."""
    package_dir = temp_dir / "testpackage"
    package_dir.mkdir()

    # Create basic package structure
    (package_dir / "testpackage").mkdir()
    (package_dir / "testpackage" / "__init__.py").write_text('__version__ = "0.1.0"')
    (package_dir / "tests").mkdir()
    (package_dir / "tests" / "__init__.py").write_text("")

    # Create setup.py
    setup_content = """
from setuptools import setup, find_packages

setup(
    name="testpackage",
    version="0.1.0",
    packages=find_packages(),
)
"""
    (package_dir / "setup.py").write_text(setup_content)

    # Create pyproject.toml
    pyproject_content = """
[project]
name = "testpackage"
version = "0.1.0"
description = "Test package"
"""
    (package_dir / "pyproject.toml").write_text(pyproject_content)

    return package_dir


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    test_vars = {
        "PYPI_USERNAME": "__token__",
        "PYPI_TOKEN": "test_pypi_token",
        "TESTPYPI_USERNAME": "__token__",
        "TESTPYPI_TOKEN": "test_testpypi_token",
    }

    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)

    return test_vars
