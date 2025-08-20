# Publishing to PyPI

## Introduction

This document describes the process of publishing the `mcp_proxy_adapter` package to PyPI (Python Package Index).

## Prerequisites

1. Account on [PyPI](https://pypi.org/)
2. Installed build and publishing tools:
   ```bash
   pip install build twine
   ```
3. Configured PyPI credentials (API token can be used)

## Publication Methods

There are several ways to publish the package:

### 1. Using publish.py script

The easiest way to publish the package is to use the `publish.py` script in the project root:

```bash
# Publishing to TestPyPI (test server)
python publish.py --test

# Publishing to main PyPI
python publish.py
```

This script performs:
- Cleaning previous builds
- Building a new package
- Running installation tests
- Publishing to PyPI

### 2. Using scripts/publish.py script

An alternative script for publishing with additional options:

```bash
# Only build the package without uploading
python scripts/publish.py --build-only

# Publishing to TestPyPI
python scripts/publish.py --test

# Publishing to main PyPI without cleaning build directories
python scripts/publish.py --no-clean
```

### 3. Manual publication

You can also perform the publication process manually:

```bash
# Cleaning previous builds
rm -rf build/ dist/ *.egg-info/

# Building the package
python -m build

# Publishing to TestPyPI
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Publishing to main PyPI
python -m twine upload dist/*
```

### 4. GitHub Actions

The project is configured for automatic publication via GitHub Actions when a version tag is created:

1. Create and push a version tag:
   ```bash
   git tag v3.0.1
   git push origin v3.0.1
   ```

2. GitHub Actions will automatically run tests and publish the package to PyPI after successful test completion.

## Configuring PyPI Credentials

### Option 1: .pypirc file

Create a `~/.pypirc` file with the following content:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJGYwMjU5YWVlLWEzYTktNGQwMy1iNWM1LTQzYmJmNjQ4NWY5MwACKlszLCJjMzZiMTJkNi00ZDJjLTQwYjAtOWI5ZS1mZjQ4YTUxNWNhOWEiXQAABiDhI_H_1wPtcPqxvbMeA9eCKHLDJj9UwMECE-XiO6vNNg

[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZwIkZGE0MzE0NzAtMmQ5OS00YjIwLTk1NTYtMzI4ZDIwOTVhZGU0AAIqWzMsIjM0MTI5OGY2LWM5YzItNDdlMi05OGU2LThkOTA0MDQzYzIyOCJdAAAGIOQh9aXVQkIqwTfwDDnBPokEZuq1OuWDJYHpS-i7UR4c
```

Replace the tokens with your own.

### Option 2: Environment variables

Instead of a configuration file, you can use environment variables:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJGYwMjU5YWVlLWEzYTktNGQwMy1iNWM1LTQzYmJmNjQ4NWY5MwACKlszLCJjMzZiMTJkNi00ZDJjLTQwYjAtOWI5ZS1mZjQ4YTUxNWNhOWEiXQAABiDhI_H_1wPtcPqxvbMeA9eCKHLDJj9UwMECE-XiO6vNNg
```

## Preparation for publication

### 1. Updating version

Before publishing, update the package version in the `mcp_proxy_adapter/version.py` file:

```python
__version__ = "3.0.1"
```

### 2. Updating CHANGELOG.md

Add information about the new version to the files:
- `CHANGELOG.md`
- `CHANGELOG_ru.md`

### 3. Checking package metadata

Ensure that all metadata in the `pyproject.toml` file is up to date.

## Verifying the package after publication

After publication, it's useful to ensure that the package installs and works correctly:

```bash
# Creating a temporary environment
python -m venv test_env
source test_env/bin/activate

# Installing the package
pip install mcp-proxy-adapter

# Checking import
python -c "import mcp_proxy_adapter; print(mcp_proxy_adapter.__version__)"

# Deactivating the environment
deactivate
rm -rf test_env
```

## Troubleshooting

### Authentication error

If you encounter an authentication error, check:
- Token correctness
- Token expiration date
- Token access rights (should include publication)

### Metadata validation error

If PyPI rejects the package due to metadata problems:
- Check that all required fields are present in `pyproject.toml`
- Ensure that the package description is correctly formatted
- Verify package name uniqueness

## Additional resources

- [Official documentation on publishing to PyPI](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Twine documentation](https://twine.readthedocs.io/en/latest/)
- [Build documentation](https://pypa-build.readthedocs.io/en/latest/) 