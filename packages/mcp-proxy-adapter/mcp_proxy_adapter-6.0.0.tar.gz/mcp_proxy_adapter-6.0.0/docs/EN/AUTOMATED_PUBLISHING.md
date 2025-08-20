# Automated Package Publishing

## Introduction

This document describes the automated process for publishing the `mcp_proxy_adapter` package to PyPI using the developed scripts.

## Publishing Scripts

The project includes the following scripts to automate the publishing process:

1. `scripts/publish_and_test.py` - main script for publishing and testing
2. `scripts/test_install.py` - script for verifying the correctness of package installation

## Publishing Process

### 1. Preparation for Publishing

Before publishing, make sure to check:
- All necessary code changes have been made
- Tests pass successfully
- Documentation is updated

### 2. Automated Publishing

To publish the package, use the `publish_and_test.py` script:

```bash
# Update version and publish to main PyPI
python scripts/publish_and_test.py --version 3.0.1

# Publish to TestPyPI
python scripts/publish_and_test.py --test

# Build package only without publishing
python scripts/publish_and_test.py --build-only
```

### 3. What the Publishing Script Does

The `publish_and_test.py` script performs the following actions:

1. **Version Update** (when the `--version` parameter is specified):
   - Updates the version in `mcp_proxy_adapter/version.py`
   - Adds a new entry to the `CHANGELOG.md` and `CHANGELOG_ru.md` files

2. **Package Building**:
   - Cleans previous builds
   - Creates `.tar.gz` and `.whl` archives

3. **Package Publishing**:
   - Uploads the package to PyPI or TestPyPI

4. **Installation Testing**:
   - Creates an isolated environment
   - Installs the package
   - Verifies the correctness of the installation
   - Tests project creation

### 4. Manual Testing

For manual testing of package installation, you can use the `test_install.py` script:

```bash
python scripts/test_install.py
```

## Requirements

The following tools are required to use the publishing scripts:

1. Python 3.6 or higher
2. `build` and `twine` modules:
   ```bash
   pip install build twine
   ```
3. Configured access to PyPI (`.pypirc` file or environment variables)

## Configuring Access to PyPI

### 1. Using a Configuration File

Create a `~/.pypirc` file with the following content:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-API-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = testpypi-API-token
```

### 2. Using Environment Variables

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-API-token
```

## Troubleshooting

### Publishing Error

If an error occurs when publishing the package, check:
1. Correctness of PyPI credentials
2. Uniqueness of the package version (you cannot re-upload an already published version)
3. Compliance of the package name with PyPI requirements

### Installation Error

If the package is installed but errors occur during import:
1. Check if all necessary files are included in the package (MANIFEST.in)
2. Make sure dependencies are correctly specified in setup.py or pyproject.toml
3. Try installing the package in debug mode: `pip install -v mcp_proxy_adapter` 