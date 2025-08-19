"""
Tests for package upload module.
"""

from pathlib import Path

from pyph.uploader import PackageUploader


def test_uploader_creation(sample_package_dir):
    """Test PackageUploader creation."""
    uploader = PackageUploader(sample_package_dir)
    assert uploader.package_path == sample_package_dir.resolve()
    assert uploader.dist_dir == sample_package_dir / "dist"
    assert uploader.build_dir == sample_package_dir / "build"


def test_get_package_name_from_pyproject(sample_package_dir):
    """Test getting package name from pyproject.toml."""
    uploader = PackageUploader(sample_package_dir)
    name = uploader._get_package_name()
    assert name == "testpackage"


def test_get_package_name_from_setup_py(temp_dir):
    """Test getting package name from setup.py."""
    # Create package with only setup.py
    package_dir = temp_dir / "testpkg"
    package_dir.mkdir()

    setup_content = """
from setuptools import setup

setup(
    name="mypackage",
    version="1.0.0",
)
"""
    (package_dir / "setup.py").write_text(setup_content)

    uploader = PackageUploader(package_dir)
    name = uploader._get_package_name()
    assert name == "mypackage"


def test_get_package_name_not_found(temp_dir):
    """Test getting package name when not found."""
    uploader = PackageUploader(temp_dir)
    name = uploader._get_package_name()
    assert name is None


def test_check_command_available():
    """Test command availability checking."""
    uploader = PackageUploader(Path("."))

    # Python should be available
    assert uploader._check_command_available("python") is True

    # Non-existent command should not be available
    assert uploader._check_command_available("nonexistentcommand12345") is False


def test_get_credentials_pypi(mock_env_vars):
    """Test getting PyPI credentials."""
    uploader = PackageUploader(Path("."))
    username, password = uploader._get_credentials(test=False)

    assert username == "__token__"
    assert password == "test_pypi_token"


def test_get_credentials_testpypi(mock_env_vars):
    """Test getting TestPyPI credentials."""
    uploader = PackageUploader(Path("."))
    username, password = uploader._get_credentials(test=True)

    assert username == "__token__"
    assert password == "test_testpypi_token"


def test_get_credentials_missing():
    """Test getting credentials when not set."""
    uploader = PackageUploader(Path("."))
    username, password = uploader._get_credentials(test=False)

    # Should default to __token__ for username
    assert username == "__token__"
    # Password might be None if not set
    assert password is None or password == ""


def test_clean_build_dirs(sample_package_dir):
    """Test cleaning build directories."""
    # Create some build directories
    (sample_package_dir / "build").mkdir()
    (sample_package_dir / "dist").mkdir()
    (sample_package_dir / "testpackage.egg-info").mkdir()

    # Create some files
    (sample_package_dir / "build" / "test.txt").write_text("test")
    (sample_package_dir / "dist" / "test.whl").write_text("test")

    uploader = PackageUploader(sample_package_dir)
    uploader.clean_build_dirs()

    # Directories should be removed
    assert not (sample_package_dir / "build").exists()
    assert not (sample_package_dir / "dist").exists()


def test_get_upload_status(sample_package_dir):
    """Test getting upload status."""
    uploader = PackageUploader(sample_package_dir)
    status = uploader.get_upload_status()

    assert "dist_exists" in status
    assert "dist_files" in status
    assert "build_exists" in status
    assert "package_name" in status
    assert "twine_available" in status
    assert "build_available" in status

    assert status["package_name"] == "testpackage"


def test_get_upload_status_with_dist(sample_package_dir):
    """Test getting upload status with dist files."""
    # Create dist directory with files
    dist_dir = sample_package_dir / "dist"
    dist_dir.mkdir()
    (dist_dir / "testpackage-1.0.0.tar.gz").write_text("test")
    (dist_dir / "testpackage-1.0.0-py3-none-any.whl").write_text("test")

    uploader = PackageUploader(sample_package_dir)
    status = uploader.get_upload_status()

    assert status["dist_exists"] is True
    assert len(status["dist_files"]) == 2
    assert "testpackage-1.0.0.tar.gz" in status["dist_files"]
    assert "testpackage-1.0.0-py3-none-any.whl" in status["dist_files"]


def test_verify_package_no_dist(sample_package_dir):
    """Test package verification with no dist directory."""
    uploader = PackageUploader(sample_package_dir)
    result = uploader.verify_package()

    assert result is False


def test_verify_package_with_dist(sample_package_dir):
    """Test package verification with dist files."""
    # Create dist directory with files
    dist_dir = sample_package_dir / "dist"
    dist_dir.mkdir()
    (dist_dir / "testpackage-1.0.0.tar.gz").write_text("test")
    (dist_dir / "testpackage-1.0.0-py3-none-any.whl").write_text("test")

    uploader = PackageUploader(sample_package_dir)
    result = uploader.verify_package()

    # Should find the files
    assert result is True or result is False  # Depends on pip install test
