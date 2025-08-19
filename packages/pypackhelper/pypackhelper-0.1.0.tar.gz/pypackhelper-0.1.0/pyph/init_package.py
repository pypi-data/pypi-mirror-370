"""
Package initialization module for creating new Python packages.
"""

import datetime
from pathlib import Path
from typing import Optional


class PackageInitializer:
    """Handles creation of new Python packages with standard structure."""

    def __init__(
        self,
        name: str,
        author: Optional[str] = None,
        email: Optional[str] = None,
        description: Optional[str] = None,
        license_type: str = "MIT",
        github_actions: bool = True,
    ):
        self.name = name
        self.author = author or "Your Name"
        self.email = email or "your.email@example.com"
        self.description = description or f"A Python package: {name}"
        self.license_type = license_type
        self.github_actions = github_actions
        self.current_year = datetime.datetime.now().year

    def create_package(self, target_path: Path) -> Path:
        """Create a complete package structure."""
        package_path = target_path / self.name

        if package_path.exists():
            raise ValueError(f"Directory '{self.name}' already exists")

        # Create main package directory
        package_path.mkdir(parents=True)

        # Create package structure
        self._create_package_structure(package_path)

        # Create configuration files
        self._create_setup_py(package_path)
        self._create_pyproject_toml(package_path)
        self._create_requirements_files(package_path)

        # Create documentation
        self._create_readme(package_path)
        self._create_license(package_path)

        # Create source code structure
        self._create_source_structure(package_path)

        # Create test structure
        self._create_test_structure(package_path)

        # Create configuration files
        self._create_config_files(package_path)

        # Create GitHub Actions if requested
        if self.github_actions:
            self._create_github_actions(package_path)

        return package_path

    def _create_package_structure(self, package_path: Path):
        """Create basic package directory structure."""
        directories = [
            self.name,
            "tests",
            "docs",
            ".github/workflows" if self.github_actions else None,
        ]

        for directory in directories:
            if directory:
                (package_path / directory).mkdir(parents=True, exist_ok=True)

    def _create_setup_py(self, package_path: Path):
        """Create setup.py file."""
        setup_content = f'''"""Setup script for {self.name}."""

from setuptools import setup, find_packages
import pathlib

# Read README
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_path = here / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="{self.name}",
    version="0.1.0",
    author="{self.author}",
    author_email="{self.email}",
    description="{self.description}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{{USERNAME}}/{self.name}",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: {self.license_type} License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={{
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "flake8>=3.8",
            "black>=21.0",
            "isort>=5.0",
            "mypy>=0.800",
        ],
    }},
    entry_points={{
        "console_scripts": [
            "{self.name}={self.name}.cli:main",
        ],
    }},
)
'''
        (package_path / "setup.py").write_text(setup_content, encoding="utf-8")

    def _create_pyproject_toml(self, package_path: Path):
        """Create pyproject.toml file."""
        toml_content = f"""[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "{self.name}"
version = "0.1.0"
description = "{self.description}"
readme = "README.md"
requires-python = ">=3.8"
license = {{text = "{self.license_type}"}}
authors = [
    {{name = "{self.author}", email = "{self.email}"}},
]
keywords = ["python", "package", "utility"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: {self.license_type} License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "pytest-cov>=2.0",
    "flake8>=3.8",
    "black>=21.0",
    "isort>=5.0",
    "mypy>=0.800",
]

[project.scripts]
{self.name} = "{self.name}.cli:main"

[project.urls]
Homepage = "https://github.com/{{USERNAME}}/{self.name}"
Documentation = "https://github.com/{{USERNAME}}/{self.name}#readme"
Repository = "https://github.com/{{USERNAME}}/{self.name}.git"
"Bug Tracker" = "https://github.com/{{USERNAME}}/{self.name}/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["{self.name}*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.black]
line-length = 88
target-version = ["py38"]
include = '\\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
exclude = [
    ".git",
    "__pycache__",
    "build",
    "dist",
    ".eggs",
    "*.egg-info",
    ".venv",
    "venv",
]
"""
        (package_path / "pyproject.toml").write_text(toml_content, encoding="utf-8")

    def _create_requirements_files(self, package_path: Path):
        """Create requirements files."""
        # Main requirements
        (package_path / "requirements.txt").write_text(
            "# Add your package dependencies here\n", encoding="utf-8"
        )

        # Development requirements
        dev_requirements = """# Development dependencies
pytest>=6.0
pytest-cov>=2.0
flake8>=3.8
black>=21.0
isort>=5.0
mypy>=0.800
pre-commit>=2.0
"""
        (package_path / "requirements-dev.txt").write_text(
            dev_requirements, encoding="utf-8"
        )

    def _create_readme(self, package_path: Path):
        """Create README.md file."""
        readme_content = f"""# {self.name}

{self.description}

## Installation

```bash
pip install {self.name}
```

## Usage

```python
import {self.name}

# Your code here
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/{{USERNAME}}/{self.name}.git
cd {self.name}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black {self.name}/
isort {self.name}/
flake8 {self.name}/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the {self.license_type} License - see the [LICENSE](LICENSE) file for details.

## Author

{self.author} - {self.email}
"""
        (package_path / "README.md").write_text(readme_content, encoding="utf-8")

    def _create_license(self, package_path: Path):
        """Create LICENSE file."""
        if self.license_type == "MIT":
            license_content = f"""MIT License

Copyright (c) {self.current_year} {self.author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        else:
            license_content = f"# License\n\nThis project is licensed under the {self.license_type} License.\n"

        (package_path / "LICENSE").write_text(license_content, encoding="utf-8")

    def _create_source_structure(self, package_path: Path):
        """Create source code structure."""
        source_dir = package_path / self.name

        # __init__.py
        init_content = f'''"""
{self.name} - {self.description}
"""

__version__ = "0.1.0"
__author__ = "{self.author}"
__email__ = "{self.email}"

# Import main classes/functions here
# from .core import MainClass
'''
        (source_dir / "__init__.py").write_text(init_content, encoding="utf-8")

        # main.py
        main_content = f'''"""
Main module for {self.name}.
"""


def main():
    """Main entry point for the application."""
    print("Hello from {self.name}!")


if __name__ == "__main__":
    main()
'''
        (source_dir / "main.py").write_text(main_content, encoding="utf-8")

        # cli.py (if needed)
        cli_content = f'''"""
Command line interface for {self.name}.
"""

import argparse


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(description="{self.description}")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    print(f"Welcome to {self.name}!")


if __name__ == "__main__":
    main()
'''
        (source_dir / "cli.py").write_text(cli_content, encoding="utf-8")

    def _create_test_structure(self, package_path: Path):
        """Create test structure."""
        tests_dir = package_path / "tests"

        # __init__.py
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")

        # conftest.py
        conftest_content = '''"""
Pytest configuration and fixtures.
"""

import pytest


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {"key": "value", "number": 42}
'''
        (tests_dir / "conftest.py").write_text(conftest_content, encoding="utf-8")

        # test_main.py
        test_main_content = f'''"""
Tests for {self.name} main module.
"""

import pytest
from {self.name} import main


def test_main_function():
    """Test main function exists and is callable."""
    assert callable(main.main)


def test_sample_with_fixture(sample_data):
    """Test using sample fixture."""
    assert sample_data["key"] == "value"
    assert sample_data["number"] == 42


# Add more tests here
'''
        (tests_dir / "test_main.py").write_text(test_main_content, encoding="utf-8")

    def _create_config_files(self, package_path: Path):
        """Create configuration files."""
        # .gitignore
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        (package_path / ".gitignore").write_text(gitignore_content, encoding="utf-8")

        # .env.example
        env_example_content = """# Environment variables for development
# Copy this to .env and fill in your values

# PyPI credentials (for upload)
PYPI_USERNAME=__token__
PYPI_TOKEN=your_pypi_token_here

# TestPyPI credentials (for testing)
TESTPYPI_USERNAME=__token__
TESTPYPI_TOKEN=your_testpypi_token_here
"""
        (package_path / ".env.example").write_text(
            env_example_content, encoding="utf-8"
        )

        # setup.cfg
        setup_cfg_content = """[metadata]
license_files = LICENSE

[bdist_wheel]
universal = 1

[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    .eggs,
    *.egg-info,
    .venv,
    venv,

[coverage:run]
source = .
omit = 
    */tests/*
    */test_*
    setup.py
    */venv/*
    */.venv/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
"""
        (package_path / "setup.cfg").write_text(setup_cfg_content, encoding="utf-8")

    def _create_github_actions(self, package_path: Path):
        """Create GitHub Actions workflow."""
        workflow_content = f"""name: Test and Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Lint with flake8
      run: |
        flake8 {self.name}/ tests/
    
    - name: Format check with black
      run: |
        black --check {self.name}/ tests/
    
    - name: Import sort check with isort
      run: |
        isort --check-only {self.name}/ tests/
    
    - name: Type check with mypy
      run: |
        mypy {self.name}/
    
    - name: Test with pytest
      run: |
        pytest --cov={self.name} --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'release' && github.event.action == 'published'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        user: __token__
        password: ${{{{ secrets.PYPI_API_TOKEN }}}}
"""
        github_dir = package_path / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)
        (github_dir / "ci.yml").write_text(workflow_content, encoding="utf-8")
