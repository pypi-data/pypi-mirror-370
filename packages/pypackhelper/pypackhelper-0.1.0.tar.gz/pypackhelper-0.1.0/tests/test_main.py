"""
Tests for the main pyph module.
"""

from pyph import __author__, __description__, __email__, __version__


def test_module_metadata():
    """Test module metadata is correctly defined."""
    assert __version__ == "0.1.0"
    assert __author__ == "PyPackHelper Team"
    assert __email__ == "contact@pypackhelper.dev"
    assert __description__ == "A comprehensive tool for Python package management"


def test_module_imports():
    """Test that main components can be imported."""
    from pyph import (
        PackageInitializer,
        PackageUploader,
        PackageValidator,
        VersionManager,
        app,
    )

    # Check that imports work
    assert app is not None
    assert PackageInitializer is not None
    assert VersionManager is not None
    assert PackageValidator is not None
    assert PackageUploader is not None


def test_package_initializer_import():
    """Test PackageInitializer can be instantiated."""
    from pyph import PackageInitializer

    initializer = PackageInitializer(name="test")
    assert initializer.name == "test"


def test_version_manager_import():
    """Test VersionManager can be instantiated."""
    from pathlib import Path

    from pyph import VersionManager

    vm = VersionManager(Path("."))
    assert vm.package_path is not None


def test_package_validator_import():
    """Test PackageValidator can be instantiated."""
    from pathlib import Path

    from pyph import PackageValidator

    validator = PackageValidator(Path("."))
    assert validator.package_path is not None


def test_package_uploader_import():
    """Test PackageUploader can be instantiated."""
    from pathlib import Path

    from pyph import PackageUploader

    uploader = PackageUploader(Path("."))
    assert uploader.package_path is not None
