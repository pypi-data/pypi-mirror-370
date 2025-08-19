"""Setup script for PyPackHelper."""

from setuptools import setup, find_packages
import pathlib

# Read README
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_path = here / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="pypackhelper",
    version="0.1.0",
    author="PyPackHelper Team",
    author_email="contact@pypackhelper.dev",
    description="A comprehensive tool for Python package management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Okymi-X/PyPackHelper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Software Distribution",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typer>=0.9.0",
        "python-dotenv>=1.0.0",
        "toml>=0.10.2",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "flake8>=3.8",
            "black>=21.0",
            "isort>=5.0",
            "mypy>=0.800",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
        "full": [
            "build>=0.10.0",
            "twine>=4.0.0",
            "flake8>=3.8",
            "black>=21.0",
            "isort>=5.0",
            "mypy>=0.800",
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyph=pyph.cli:main",
        ],
    },
    keywords=["python", "packaging", "pypi", "cli", "development"],
    project_urls={
        "Bug Reports": "https://github.com/Okymi-X/PyPackHelper/issues",
        "Source": "https://github.com/Okymi-X/PyPackHelper",
        "Documentation": "https://github.com/Okymi-X/PyPackHelper#readme",
    },
)
