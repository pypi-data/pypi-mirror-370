"""
Package upload module for PyPI distribution.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class PackageUploader:
    """Handles package building and uploading to PyPI/TestPyPI."""

    def __init__(self, package_path: Path):
        self.package_path = Path(package_path).resolve()
        self.dist_dir = self.package_path / "dist"
        self.build_dir = self.package_path / "build"
        self.egg_info_dirs = list(self.package_path.glob("*.egg-info"))

        # Load environment variables
        load_dotenv(self.package_path / ".env")

    def build_package(self) -> bool:
        """Build package distributions (sdist and wheel)."""
        print("🔨 Building package distributions...")

        try:
            # Clean previous builds
            self.clean_build_dirs()

            # Use python -m build if available
            if self._check_command_available("python"):
                try:
                    result = subprocess.run(
                        ["python", "-m", "build"],
                        cwd=self.package_path,
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        print("✅ Package built successfully with python -m build")
                        return True
                    else:
                        print("⚠️  python -m build failed, trying setuptools...")

                except subprocess.CalledProcessError:
                    pass

            # Fallback to setuptools
            if (self.package_path / "setup.py").exists():
                try:
                    # Build source distribution
                    result = subprocess.run(
                        ["python", "setup.py", "sdist"],
                        cwd=self.package_path,
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode != 0:
                        print(
                            f"❌ Failed to build source distribution: {result.stderr}"
                        )
                        return False

                    # Build wheel distribution
                    result = subprocess.run(
                        ["python", "setup.py", "bdist_wheel"],
                        cwd=self.package_path,
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode != 0:
                        print(f"❌ Failed to build wheel distribution: {result.stderr}")
                        return False

                    print("✅ Package built successfully with setuptools")
                    return True

                except Exception as e:
                    print(f"❌ Error building package: {e}")
                    return False

            else:
                print("❌ No setup.py found and python -m build failed")
                return False

        except Exception as e:
            print(f"❌ Error building package: {e}")
            return False

    def upload_package(self, test: bool = False) -> bool:
        """Upload package to PyPI or TestPyPI."""
        repository = "testpypi" if test else "pypi"
        print(f"📦 Uploading package to {repository.upper()}...")

        # Check if dist directory exists and has files
        if not self.dist_dir.exists() or not list(self.dist_dir.glob("*")):
            print("❌ No distribution files found. Run build first.")
            return False

        # Check if twine is available
        if not self._check_command_available("twine"):
            print("❌ twine not available. Install with: pip install twine")
            return False

        try:
            # Get credentials
            username, password = self._get_credentials(test)

            if not username or not password:
                print(f"❌ Missing credentials for {repository.upper()}")
                print("Set credentials in .env file or environment variables")
                return False

            # Build twine command
            cmd = ["twine", "upload"]

            if test:
                cmd.extend(["--repository", "testpypi"])

            cmd.extend(
                [
                    "--username",
                    username,
                    "--password",
                    password,
                    str(self.dist_dir / "*"),
                ]
            )

            # Upload
            result = subprocess.run(
                cmd, cwd=self.package_path, capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"✅ Package uploaded successfully to {repository.upper()}")

                # Print installation instructions
                package_name = self._get_package_name()
                if package_name:
                    if test:
                        print(
                            f"🔧 Test installation: pip install -i https://test.pypi.org/simple/ {package_name}"
                        )
                    else:
                        print(f"🔧 Installation: pip install {package_name}")

                return True
            else:
                print(f"❌ Upload failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error uploading package: {e}")
            return False

    def clean_build_dirs(self):
        """Clean build directories and cache files."""
        print("🧹 Cleaning build directories...")

        directories_to_clean = [
            self.dist_dir,
            self.build_dir,
            *self.egg_info_dirs,
            *self.package_path.glob("**/__pycache__"),
            *self.package_path.glob("**/*.pyc"),
        ]

        for directory in directories_to_clean:
            if directory.exists():
                try:
                    if directory.is_dir():
                        shutil.rmtree(directory)
                    else:
                        directory.unlink()
                    print(f"✅ Removed {directory.name}")
                except Exception as e:
                    print(f"⚠️  Could not remove {directory}: {e}")

    def verify_package(self) -> bool:
        """Verify package can be installed and imported."""
        print("🔍 Verifying package...")

        # Check if dist files exist
        if not self.dist_dir.exists():
            print("❌ No dist directory found")
            return False

        dist_files = list(self.dist_dir.glob("*"))
        if not dist_files:
            print("❌ No distribution files found")
            return False

        print(f"✅ Found {len(dist_files)} distribution files:")
        for file in dist_files:
            print(f"   • {file.name}")

        # Try to get package name and test import
        package_name = self._get_package_name()
        if package_name:
            try:
                # Create temporary environment and test installation
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)

                    # Find wheel file for testing
                    wheel_files = list(self.dist_dir.glob("*.whl"))
                    if wheel_files:
                        wheel_file = wheel_files[0]

                        # Test pip install in isolated environment
                        result = subprocess.run(
                            [
                                "pip",
                                "install",
                                "--target",
                                str(temp_path),
                                str(wheel_file),
                            ],
                            capture_output=True,
                            text=True,
                        )

                        if result.returncode == 0:
                            print("✅ Package can be installed successfully")
                            return True
                        else:
                            print(
                                f"⚠️  Package installation test failed: {result.stderr}"
                            )
                            return False

            except Exception as e:
                print(f"⚠️  Package verification failed: {e}")
                return False

        return True

    def _get_credentials(self, test: bool = False) -> tuple:
        """Get PyPI/TestPyPI credentials from environment."""
        if test:
            username = os.getenv("TESTPYPI_USERNAME", os.getenv("TWINE_USERNAME"))
            password = os.getenv(
                "TESTPYPI_TOKEN",
                os.getenv("TESTPYPI_PASSWORD", os.getenv("TWINE_PASSWORD")),
            )
        else:
            username = os.getenv("PYPI_USERNAME", os.getenv("TWINE_USERNAME"))
            password = os.getenv(
                "PYPI_TOKEN", os.getenv("PYPI_PASSWORD", os.getenv("TWINE_PASSWORD"))
            )

        return username or "__token__", password

    def _get_package_name(self) -> Optional[str]:
        """Get package name from configuration files."""
        # Try pyproject.toml first
        pyproject_path = self.package_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text(encoding="utf-8")
                lines = content.split("\n")
                for line in lines:
                    if line.strip().startswith("name ="):
                        # Extract name from line like: name = "package-name"
                        name = line.split("=")[1].strip().strip('"').strip("'")
                        return name
            except Exception:
                pass

        # Try setup.py
        setup_path = self.package_path / "setup.py"
        if setup_path.exists():
            try:
                content = setup_path.read_text(encoding="utf-8")
                import re

                match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
            except Exception:
                pass

        return None

    def _check_command_available(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            result = subprocess.run(
                [command, "--version"], capture_output=True, text=True
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_upload_status(self) -> Dict[str, Any]:
        """Get current upload status and information."""
        status = {
            "dist_exists": self.dist_dir.exists(),
            "dist_files": [],
            "build_exists": self.build_dir.exists(),
            "package_name": self._get_package_name(),
            "twine_available": self._check_command_available("twine"),
            "build_available": self._check_command_available("python")
            and self._check_build_available(),
        }

        if status["dist_exists"]:
            status["dist_files"] = [f.name for f in self.dist_dir.glob("*")]

        return status

    def _check_build_available(self) -> bool:
        """Check if build package is available."""
        try:
            result = subprocess.run(
                ["python", "-c", "import build"], capture_output=True, text=True
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def install_dependencies(self) -> bool:
        """Install required dependencies for building and uploading."""
        print("📦 Installing upload dependencies...")

        dependencies = ["build", "twine", "python-dotenv"]

        try:
            result = subprocess.run(
                ["pip", "install"] + dependencies,
                cwd=self.package_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                return True
            else:
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
