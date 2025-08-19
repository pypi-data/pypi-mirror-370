"""
Version management module for Python packages.
"""

import re
import subprocess
from pathlib import Path
from typing import Optional

import toml


class VersionManager:
    """Handles version bumping and management for Python packages."""

    def __init__(self, package_path: Path):
        self.package_path = Path(package_path).resolve()
        self.pyproject_path = self.package_path / "pyproject.toml"
        self.setup_py_path = self.package_path / "setup.py"
        self.init_files = list(self.package_path.glob("*//__init__.py"))

    def get_current_version(self) -> str:
        """Get the current version from various sources."""
        # Try pyproject.toml first
        if self.pyproject_path.exists():
            try:
                with open(self.pyproject_path, "r", encoding="utf-8") as f:
                    data = toml.load(f)
                    if "project" in data and "version" in data["project"]:
                        return data["project"]["version"]
            except Exception:
                pass

        # Try setup.py
        if self.setup_py_path.exists():
            try:
                content = self.setup_py_path.read_text(encoding="utf-8")
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    return version_match.group(1)
            except Exception:
                pass

        # Try __init__.py files
        for init_file in self.init_files:
            try:
                content = init_file.read_text(encoding="utf-8")
                version_match = re.search(
                    r'__version__\s*=\s*["\']([^"\']+)["\']', content
                )
                if version_match:
                    return version_match.group(1)
            except Exception:
                pass

        raise ValueError("Could not find version information in package files")

    def calculate_new_version(self, current_version: str, version_type: str) -> str:
        """Calculate new version based on current version and bump type."""
        if not re.match(r"^\d+\.\d+\.\d+", current_version):
            raise ValueError(f"Invalid version format: {current_version}")

        # Parse version
        version_parts = current_version.split(".")
        major = int(version_parts[0])
        minor = int(version_parts[1])
        patch_part = version_parts[2]

        # Extract patch number (handle pre-release versions)
        patch_match = re.match(r"^(\d+)", patch_part)
        if not patch_match:
            raise ValueError(f"Invalid patch version: {patch_part}")

        patch = int(patch_match.group(1))

        # Bump version
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        elif version_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid version type: {version_type}")

        return f"{major}.{minor}.{patch}"

    def bump_version(self, version_type: str) -> str:
        """Bump version in all relevant files."""
        current_version = self.get_current_version()
        new_version = self.calculate_new_version(current_version, version_type)

        # Update pyproject.toml
        if self.pyproject_path.exists():
            self._update_pyproject_version(new_version)

        # Update setup.py
        if self.setup_py_path.exists():
            self._update_setup_py_version(current_version, new_version)

        # Update __init__.py files
        for init_file in self.init_files:
            self._update_init_version(init_file, current_version, new_version)

        # Create git tag if in git repository
        try:
            self._create_git_tag(new_version)
        except Exception:
            # Ignore git errors (might not be in a git repo)
            pass

        return new_version

    def _update_pyproject_version(self, new_version: str):
        """Update version in pyproject.toml."""
        with open(self.pyproject_path, "r", encoding="utf-8") as f:
            data = toml.load(f)

        if "project" in data:
            data["project"]["version"] = new_version

        with open(self.pyproject_path, "w", encoding="utf-8") as f:
            toml.dump(data, f)

    def _update_setup_py_version(self, old_version: str, new_version: str):
        """Update version in setup.py."""
        content = self.setup_py_path.read_text(encoding="utf-8")

        # Replace version string
        pattern = rf'version\s*=\s*["\']({re.escape(old_version)})["\']'
        replacement = f'version="{new_version}"'

        updated_content = re.sub(pattern, replacement, content)

        if updated_content != content:
            self.setup_py_path.write_text(updated_content, encoding="utf-8")

    def _update_init_version(self, init_file: Path, old_version: str, new_version: str):
        """Update version in __init__.py file."""
        try:
            content = init_file.read_text(encoding="utf-8")

            # Replace __version__ string
            pattern = rf'__version__\s*=\s*["\']({re.escape(old_version)})["\']'
            replacement = f'__version__ = "{new_version}"'

            updated_content = re.sub(pattern, replacement, content)

            if updated_content != content:
                init_file.write_text(updated_content, encoding="utf-8")
        except Exception:
            # Ignore errors for individual files
            pass

    def _create_git_tag(self, version: str):
        """Create a git tag for the new version."""
        try:
            # Check if we're in a git repository
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.package_path,
                check=True,
                capture_output=True,
            )

            # Create and push tag
            tag_name = f"v{version}"

            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Version {version}"],
                cwd=self.package_path,
                check=True,
            )

            print(f"Created git tag: {tag_name}")

        except subprocess.CalledProcessError:
            # Not in a git repository or git command failed
            pass
        except FileNotFoundError:
            # Git not installed
            pass

    def get_git_info(self) -> Optional[dict]:
        """Get git repository information."""
        try:
            # Get current commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.package_path,
                capture_output=True,
                text=True,
                check=True,
            )
            commit_hash = result.stdout.strip()

            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.package_path,
                capture_output=True,
                text=True,
                check=True,
            )
            branch = result.stdout.strip()

            # Check if working directory is clean
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.package_path,
                capture_output=True,
                text=True,
                check=True,
            )
            is_clean = len(result.stdout.strip()) == 0

            return {"commit": commit_hash, "branch": branch, "is_clean": is_clean}

        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def validate_version_consistency(self) -> bool:
        """Check if version is consistent across all files."""
        versions = []

        # Check pyproject.toml
        if self.pyproject_path.exists():
            try:
                with open(self.pyproject_path, "r", encoding="utf-8") as f:
                    data = toml.load(f)
                    if "project" in data and "version" in data["project"]:
                        versions.append(("pyproject.toml", data["project"]["version"]))
            except Exception:
                pass

        # Check setup.py
        if self.setup_py_path.exists():
            try:
                content = self.setup_py_path.read_text(encoding="utf-8")
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    versions.append(("setup.py", version_match.group(1)))
            except Exception:
                pass

        # Check __init__.py files
        for init_file in self.init_files:
            try:
                content = init_file.read_text(encoding="utf-8")
                version_match = re.search(
                    r'__version__\s*=\s*["\']([^"\']+)["\']', content
                )
                if version_match:
                    rel_path = init_file.relative_to(self.package_path)
                    versions.append((str(rel_path), version_match.group(1)))
            except Exception:
                pass

        if not versions:
            return False

        # Check if all versions are the same
        first_version = versions[0][1]
        return all(version[1] == first_version for version in versions)

    def list_versions(self) -> list:
        """List all versions found in package files."""
        versions = []

        # Check pyproject.toml
        if self.pyproject_path.exists():
            try:
                with open(self.pyproject_path, "r", encoding="utf-8") as f:
                    data = toml.load(f)
                    if "project" in data and "version" in data["project"]:
                        versions.append(
                            {
                                "file": "pyproject.toml",
                                "version": data["project"]["version"],
                            }
                        )
            except Exception:
                pass

        # Check setup.py
        if self.setup_py_path.exists():
            try:
                content = self.setup_py_path.read_text(encoding="utf-8")
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    versions.append(
                        {"file": "setup.py", "version": version_match.group(1)}
                    )
            except Exception:
                pass

        # Check __init__.py files
        for init_file in self.init_files:
            try:
                content = init_file.read_text(encoding="utf-8")
                version_match = re.search(
                    r'__version__\s*=\s*["\']([^"\']+)["\']', content
                )
                if version_match:
                    rel_path = init_file.relative_to(self.package_path)
                    versions.append(
                        {"file": str(rel_path), "version": version_match.group(1)}
                    )
            except Exception:
                pass

        return versions
