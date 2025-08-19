"""
Package validation module for code quality checks.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


class PackageValidator:
    """Handles package validation including linting and testing."""

    def __init__(self, package_path: Path, strict: bool = False):
        self.package_path = Path(package_path).resolve()
        self.strict = strict
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        success = True

        print("🔍 Starting package validation...")

        # Check package structure
        if not self._validate_package_structure():
            success = False

        # Run linting
        if not self.run_linting():
            success = False

        # Run tests
        if not self.run_tests():
            success = False

        # Check package metadata
        if not self._validate_package_metadata():
            success = False

        # Print summary
        self._print_summary()

        return success

    def run_linting(self) -> bool:
        """Run code linting checks."""
        success = True
        print("🔧 Running linting checks...")

        # Find Python files to lint
        python_files = self._find_python_files()
        if not python_files:
            print("⚠️  No Python files found to lint")
            return True

        # Run flake8
        if not self._run_flake8(python_files):
            success = False

        # Run black check (if available)
        if not self._run_black_check(python_files):
            if self.strict:
                success = False

        # Run isort check (if available)
        if not self._run_isort_check(python_files):
            if self.strict:
                success = False

        # Run mypy (if available)
        if not self._run_mypy_check(python_files):
            if self.strict:
                success = False

        return success

    def run_tests(self) -> bool:
        """Run test suite."""
        print("🧪 Running tests...")

        # Check if tests directory exists
        tests_dir = self.package_path / "tests"
        if not tests_dir.exists():
            print("⚠️  No tests directory found")
            return not self.strict

        # Check if pytest is available
        if not self._check_command_available("pytest"):
            print("⚠️  pytest not available, skipping tests")
            return not self.strict

        # Run pytest
        try:
            result = subprocess.run(
                ["pytest", str(tests_dir), "-v", "--tb=short"],
                cwd=self.package_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ Tests passed")
                return True
            else:
                print("❌ Tests failed")
                print(result.stdout)
                print(result.stderr)
                self.errors.append("Test suite failed")
                return False

        except Exception as e:
            print(f"❌ Error running tests: {e}")
            self.errors.append(f"Error running tests: {e}")
            return False

    def _validate_package_structure(self) -> bool:
        """Validate basic package structure."""
        print("📁 Validating package structure...")
        success = True

        required_files = ["setup.py", "pyproject.toml", "README.md", "LICENSE"]

        for file_name in required_files:
            file_path = self.package_path / file_name
            if not file_path.exists():
                if file_name in ["setup.py", "pyproject.toml"]:
                    # At least one of these should exist
                    setup_exists = (self.package_path / "setup.py").exists()
                    pyproject_exists = (self.package_path / "pyproject.toml").exists()
                    if not (setup_exists or pyproject_exists):
                        print(
                            f"❌ Missing build configuration (setup.py or pyproject.toml)"
                        )
                        self.errors.append("Missing build configuration")
                        success = False
                else:
                    print(f"⚠️  Missing recommended file: {file_name}")
                    self.warnings.append(f"Missing {file_name}")
                    if self.strict:
                        success = False
            else:
                print(f"✅ Found {file_name}")

        # Check for package directory
        package_dirs = [
            d
            for d in self.package_path.iterdir()
            if d.is_dir()
            and not d.name.startswith(".")
            and d.name not in ["tests", "docs", "__pycache__", "build", "dist"]
        ]

        if not package_dirs:
            print("❌ No package directory found")
            self.errors.append("No package directory found")
            success = False
        else:
            for pkg_dir in package_dirs:
                init_file = pkg_dir / "__init__.py"
                if init_file.exists():
                    print(f"✅ Found package: {pkg_dir.name}")
                else:
                    print(f"⚠️  Package directory missing __init__.py: {pkg_dir.name}")
                    self.warnings.append(f"Missing __init__.py in {pkg_dir.name}")

        return success

    def _validate_package_metadata(self) -> bool:
        """Validate package metadata."""
        print("📋 Validating package metadata...")
        success = True

        # Check pyproject.toml metadata
        pyproject_path = self.package_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                if sys.version_info >= (3, 11):
                    import tomllib

                    with open(pyproject_path, "rb") as f:
                        data = tomllib.load(f)
                else:
                    try:
                        import tomli

                        with open(pyproject_path, "rb") as f:
                            data = tomli.load(f)
                    except ImportError:
                        # Fallback to basic parsing
                        content = pyproject_path.read_text(encoding="utf-8")
                        # Simple check for basic fields
                        if "[project]" in content:
                            print("✅ Found [project] section in pyproject.toml")
                        return True

                if "project" in data:
                    project = data["project"]
                    required_fields = ["name", "version", "description"]

                    for field in required_fields:
                        if field not in project:
                            print(f"⚠️  Missing project.{field} in pyproject.toml")
                            self.warnings.append(f"Missing project.{field}")
                            if self.strict:
                                success = False
                        else:
                            print(f"✅ Found project.{field}")

            except ImportError:
                print("⚠️  Cannot validate pyproject.toml (tomli/tomllib not available)")
            except Exception as e:
                print(f"⚠️  Error reading pyproject.toml: {e}")
                self.warnings.append(f"Error reading pyproject.toml: {e}")

        # Check setup.py metadata
        setup_path = self.package_path / "setup.py"
        if setup_path.exists():
            try:
                content = setup_path.read_text(encoding="utf-8")
                if "name=" in content and "version=" in content:
                    print("✅ Found basic setup.py metadata")
                else:
                    print("⚠️  setup.py missing basic metadata")
                    self.warnings.append("setup.py missing basic metadata")
            except Exception as e:
                print(f"⚠️  Error reading setup.py: {e}")
                self.warnings.append(f"Error reading setup.py: {e}")

        return success

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the package."""
        python_files = []

        # Find package directories
        for item in self.package_path.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and item.name not in ["__pycache__", "build", "dist"]
            ):

                python_files.extend(item.rglob("*.py"))

        # Add root level Python files
        python_files.extend(self.package_path.glob("*.py"))

        return [f for f in python_files if f.is_file()]

    def _run_flake8(self, python_files: List[Path]) -> bool:
        """Run flake8 linting."""
        if not self._check_command_available("flake8"):
            print("⚠️  flake8 not available, skipping")
            return not self.strict

        try:
            # Run flake8 on the package directory
            result = subprocess.run(
                ["flake8"] + [str(f) for f in python_files],
                cwd=self.package_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ flake8 passed")
                return True
            else:
                print("❌ flake8 found issues:")
                print(result.stdout)
                self.errors.append("flake8 linting failed")
                return False

        except Exception as e:
            print(f"❌ Error running flake8: {e}")
            self.errors.append(f"Error running flake8: {e}")
            return False

    def _run_black_check(self, python_files: List[Path]) -> bool:
        """Run black format checking."""
        if not self._check_command_available("black"):
            print("⚠️  black not available, skipping")
            return True

        try:
            result = subprocess.run(
                ["black", "--check"] + [str(f) for f in python_files],
                cwd=self.package_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ black format check passed")
                return True
            else:
                print("⚠️  black format check failed (run 'black .' to fix)")
                self.warnings.append("Code not formatted with black")
                return False

        except Exception as e:
            print(f"⚠️  Error running black: {e}")
            return True

    def _run_isort_check(self, python_files: List[Path]) -> bool:
        """Run isort import sorting check."""
        if not self._check_command_available("isort"):
            print("⚠️  isort not available, skipping")
            return True

        try:
            result = subprocess.run(
                ["isort", "--check-only"] + [str(f) for f in python_files],
                cwd=self.package_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ isort check passed")
                return True
            else:
                print("⚠️  isort check failed (run 'isort .' to fix)")
                self.warnings.append("Imports not sorted correctly")
                return False

        except Exception as e:
            print(f"⚠️  Error running isort: {e}")
            return True

    def _run_mypy_check(self, python_files: List[Path]) -> bool:
        """Run mypy type checking."""
        if not self._check_command_available("mypy"):
            print("⚠️  mypy not available, skipping")
            return True

        try:
            # Find package directories for mypy
            package_dirs = [
                d
                for d in self.package_path.iterdir()
                if d.is_dir()
                and not d.name.startswith(".")
                and d.name not in ["tests", "docs", "__pycache__", "build", "dist"]
            ]

            if not package_dirs:
                return True

            result = subprocess.run(
                ["mypy"] + [str(d) for d in package_dirs],
                cwd=self.package_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ mypy check passed")
                return True
            else:
                print("⚠️  mypy found type issues:")
                print(result.stdout)
                self.warnings.append("Type checking issues found")
                return False

        except Exception as e:
            print(f"⚠️  Error running mypy: {e}")
            return True

    def _check_command_available(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            result = subprocess.run(
                [command, "--version"], capture_output=True, text=True
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)

        if self.errors:
            print(f"❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print(f"⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")

        if not self.errors and not self.warnings:
            print("✅ All checks passed!")
        elif not self.errors:
            print("✅ No critical errors found")

        print("=" * 50)

    def get_validation_report(self) -> Dict[str, Any]:
        """Get detailed validation report."""
        return {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }
