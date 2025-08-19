"""
CLI interface for PyPackHelper using Typer.
"""

import sys
from pathlib import Path
from typing import Optional

import typer

from .init_package import PackageInitializer
from .uploader import PackageUploader
from .validator import PackageValidator
from .version_manager import VersionManager

app = typer.Typer(
    name="pyph",
    help="PyPackHelper - A comprehensive tool for Python package management",
    add_completion=False,
)


@app.command()
def init(
    name: str = typer.Argument(..., help="Package name"),
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Target directory (default: current)"
    ),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Package author"),
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Author email"),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="Package description"
    ),
    license_type: Optional[str] = typer.Option(
        "MIT", "--license", "-l", help="License type"
    ),
    github_actions: bool = typer.Option(
        True,
        "--github-actions/--no-github-actions",
        help="Generate GitHub Actions workflow",
    ),
):
    """Initialize a new Python package."""
    target_path = Path(path) if path else Path.cwd()

    try:
        initializer = PackageInitializer(
            name=name,
            author=author,
            email=email,
            description=description,
            license_type=license_type,
            github_actions=github_actions,
        )

        package_path = initializer.create_package(target_path)
        typer.echo(f"✅ Package '{name}' created successfully at {package_path}")

    except Exception as e:
        typer.echo(f"❌ Error creating package: {e}", err=True)
        sys.exit(1)


@app.command()
def validate(
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Package directory (default: current)"
    ),
    lint_only: bool = typer.Option(
        False, "--lint-only", help="Run only linting checks"
    ),
    test_only: bool = typer.Option(False, "--test-only", help="Run only tests"),
    strict: bool = typer.Option(False, "--strict", help="Strict validation mode"),
):
    """Validate package code with linting and tests."""
    target_path = Path(path) if path else Path.cwd()

    try:
        validator = PackageValidator(target_path, strict=strict)

        if test_only:
            success = validator.run_tests()
        elif lint_only:
            success = validator.run_linting()
        else:
            success = validator.validate_all()

        if success:
            typer.echo("✅ Validation passed!")
        else:
            typer.echo("❌ Validation failed!")
            sys.exit(1)

    except Exception as e:
        typer.echo(f"❌ Error during validation: {e}", err=True)
        sys.exit(1)


@app.command()
def bump(
    version_type: str = typer.Argument(
        ..., help="Version type: major, minor, or patch"
    ),
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Package directory (default: current)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be changed without making changes"
    ),
):
    """Bump package version."""
    if version_type not in ["major", "minor", "patch"]:
        typer.echo("❌ Version type must be 'major', 'minor', or 'patch'", err=True)
        sys.exit(1)

    target_path = Path(path) if path else Path.cwd()

    try:
        version_manager = VersionManager(target_path)

        if dry_run:
            current_version = version_manager.get_current_version()
            new_version = version_manager.calculate_new_version(
                current_version, version_type
            )
            typer.echo(f"Current version: {current_version}")
            typer.echo(f"New version would be: {new_version}")
        else:
            new_version = version_manager.bump_version(version_type)
            typer.echo(f"✅ Version bumped to {new_version}")

    except Exception as e:
        typer.echo(f"❌ Error bumping version: {e}", err=True)
        sys.exit(1)


@app.command()
def upload(
    test: bool = typer.Option(
        False, "--test", help="Upload to TestPyPI instead of PyPI"
    ),
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Package directory (default: current)"
    ),
    skip_validation: bool = typer.Option(
        False, "--skip-validation", help="Skip validation before upload"
    ),
    skip_build: bool = typer.Option(
        False, "--skip-build", help="Skip building package"
    ),
    clean: bool = typer.Option(
        True, "--clean/--no-clean", help="Clean build directories after upload"
    ),
):
    """Upload package to PyPI or TestPyPI."""
    target_path = Path(path) if path else Path.cwd()

    try:
        uploader = PackageUploader(target_path)

        # Validate before upload unless skipped
        if not skip_validation:
            typer.echo("🔍 Validating package...")
            validator = PackageValidator(target_path)
            if not validator.validate_all():
                typer.echo(
                    "❌ Validation failed. Use --skip-validation to force upload.",
                    err=True,
                )
                sys.exit(1)

        # Build package unless skipped
        if not skip_build:
            typer.echo("🔨 Building package...")
            uploader.build_package()

        # Upload
        repository = "testpypi" if test else "pypi"
        typer.echo(f"📦 Uploading to {repository.upper()}...")

        success = uploader.upload_package(test=test)

        if success:
            repo_name = "TestPyPI" if test else "PyPI"
            typer.echo(f"✅ Package uploaded successfully to {repo_name}!")
        else:
            typer.echo("❌ Upload failed!")
            sys.exit(1)

        # Clean build directories
        if clean:
            uploader.clean_build_dirs()

    except Exception as e:
        typer.echo(f"❌ Error during upload: {e}", err=True)
        sys.exit(1)


@app.command()
def build(
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Package directory (default: current)"
    ),
    clean: bool = typer.Option(
        True, "--clean/--no-clean", help="Clean build directories before building"
    ),
):
    """Build package distributions."""
    target_path = Path(path) if path else Path.cwd()

    try:
        uploader = PackageUploader(target_path)

        if clean:
            uploader.clean_build_dirs()

        typer.echo("🔨 Building package...")
        uploader.build_package()
        typer.echo("✅ Package built successfully!")

    except Exception as e:
        typer.echo(f"❌ Error building package: {e}", err=True)
        sys.exit(1)


@app.command()
def clean(
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Package directory (default: current)"
    ),
):
    """Clean build directories and cache files."""
    target_path = Path(path) if path else Path.cwd()

    try:
        uploader = PackageUploader(target_path)
        uploader.clean_build_dirs()
        typer.echo("✅ Build directories cleaned!")

    except Exception as e:
        typer.echo(f"❌ Error cleaning: {e}", err=True)
        sys.exit(1)


@app.command()
def version(
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Package directory (default: current)"
    ),
):
    """Show current package version."""
    target_path = Path(path) if path else Path.cwd()

    try:
        version_manager = VersionManager(target_path)
        current_version = version_manager.get_current_version()
        typer.echo(f"Current version: {current_version}")

    except Exception as e:
        typer.echo(f"❌ Error getting version: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
