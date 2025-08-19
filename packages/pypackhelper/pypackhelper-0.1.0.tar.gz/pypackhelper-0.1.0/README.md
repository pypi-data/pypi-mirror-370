# PyPackHelper

A comprehensive command-line tool for Python package management that simplifies creating, validating, versioning, and uploading Python packages to PyPI.

## 🚀 Features

- **Package Initialization**: Create new Python packages with proper structure
- **Code Validation**: Automated linting and testing with flake8, black, isort, mypy, and pytest
- **Version Management**: Semantic version bumping (major.minor.patch)
- **Automated Upload**: Upload to PyPI and TestPyPI with twine
- **GitHub Actions**: Generate CI/CD workflows
- **Environment Management**: Support for .env files and credentials

## 📦 Installation

```bash
pip install pypackhelper
```

For development features:
```bash
pip install pypackhelper[dev]
```

For all features:
```bash
pip install pypackhelper[full]
```

## 🛠️ Usage

### Initialize a New Package

```bash
pyph init mypackage --author "Your Name" --email "your@email.com"
```

Options:
- `--path, -p`: Target directory (default: current)
- `--author, -a`: Package author
- `--email, -e`: Author email  
- `--description, -d`: Package description
- `--license, -l`: License type (default: MIT)
- `--github-actions/--no-github-actions`: Generate GitHub Actions workflow

### Validate Package

```bash
pyph validate
```

Options:
- `--path, -p`: Package directory (default: current)
- `--lint-only`: Run only linting checks
- `--test-only`: Run only tests
- `--strict`: Strict validation mode

### Version Management

```bash
# Show current version
pyph version

# Bump version
pyph bump patch    # 1.0.0 -> 1.0.1
pyph bump minor    # 1.0.0 -> 1.1.0  
pyph bump major    # 1.0.0 -> 2.0.0
```

Options:
- `--path, -p`: Package directory (default: current)
- `--dry-run`: Show what would be changed without making changes

### Build Package

```bash
pyph build
```

Options:
- `--path, -p`: Package directory (default: current)
- `--clean/--no-clean`: Clean build directories before building

### Upload to PyPI

```bash
# Upload to TestPyPI (for testing)
pyph upload --test

# Upload to PyPI
pyph upload
```

Options:
- `--test`: Upload to TestPyPI instead of PyPI
- `--path, -p`: Package directory (default: current)
- `--skip-validation`: Skip validation before upload
- `--skip-build`: Skip building package
- `--clean/--no-clean`: Clean build directories after upload

### Clean Build Files

```bash
pyph clean
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your package root:

```env
# PyPI credentials
PYPI_USERNAME=__token__
PYPI_TOKEN=your_pypi_token_here

# TestPyPI credentials  
TESTPYPI_USERNAME=__token__
TESTPYPI_TOKEN=your_testpypi_token_here
```

### Package Structure Created

```
mypackage/
├── mypackage/
│   ├── __init__.py
│   ├── main.py
│   └── cli.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── setup.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
└── setup.cfg
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Okymi-X/PyPackHelper.git
cd PyPackHelper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black pyph/
isort pyph/

# Lint code
flake8 pyph/

# Type checking
mypy pyph/
```

## 📋 Requirements

- Python 3.8+
- Dependencies automatically managed

### Optional Dependencies

For full functionality, install:
- `build`: For building packages
- `twine`: For uploading to PyPI
- `flake8`: For linting
- `black`: For code formatting
- `isort`: For import sorting
- `mypy`: For type checking
- `pytest`: For testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Typer](https://typer.tiangolo.com/) for the excellent CLI framework
- [setuptools](https://setuptools.pypa.io/) and [build](https://build.pypa.io/) for packaging
- [twine](https://twine.readthedocs.io/) for PyPI uploads
- The Python packaging community

## 📞 Support

- 🐛 [Report Issues](https://github.com/Okymi-X/PyPackHelper/issues)
- 💡 [Request Features](https://github.com/Okymi-X/PyPackHelper/issues)
- 📖 [Documentation](https://github.com/Okymi-X/PyPackHelper#readme)

---

Made with ❤️ for the Python community
