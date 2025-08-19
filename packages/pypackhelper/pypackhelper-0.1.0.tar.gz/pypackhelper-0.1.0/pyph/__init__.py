"""
PyPackHelper - A comprehensive tool for Python package management.

This package provides utilities for creating, validating, versioning,
and uploading Python packages to PyPI.
"""

__version__ = "0.1.0"
__author__ = "PyPackHelper Team"
__email__ = "contact@pypackhelper.dev"
__description__ = "A comprehensive tool for Python package management"

from .cli import app
from .init_package import PackageInitializer
from .uploader import PackageUploader
from .validator import PackageValidator
from .version_manager import VersionManager

__all__ = [
    "app",
    "PackageInitializer",
    "VersionManager",
    "PackageValidator",
    "PackageUploader",
]
