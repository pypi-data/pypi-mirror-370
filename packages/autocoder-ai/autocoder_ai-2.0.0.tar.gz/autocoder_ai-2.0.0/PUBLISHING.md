# Publishing AutoCoder AI

This guide explains how to publish AutoCoder AI so users can install it via `pip install autocoder-ai`.

## Option 1: Publishing to PyPI (Recommended)

### Prerequisites
1. Create a PyPI account at https://pypi.org/account/register/
2. Create an API token at https://pypi.org/manage/account/token/
3. Install publishing tools:
   ```bash
   pip install --upgrade pip setuptools wheel twine build
   ```

### Steps to Publish

1. **Update version number** in `__version__.py`:
   ```python
   __version__ = '2.0.1'  # Increment for new releases
   ```

2. **Build the distribution**:
   ```bash
   # Clean previous builds
   rm -rf dist/ build/ *.egg-info/
   
   # Build source distribution and wheel
   python -m build
   ```

3. **Test with TestPyPI** (optional but recommended):
   ```bash
   # Upload to TestPyPI
   python -m twine upload --repository testpypi dist/*
   
   # Test installation
   pip install --index-url https://test.pypi.org/simple/ autocoder-ai
   ```

4. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```
   
   You'll be prompted for:
   - Username: `__token__`
   - Password: Your PyPI API token

5. **Verify installation**:
   ```bash
   pip install autocoder-ai
   autocoder --version
   ```

### Using .pypirc for Authentication

Create `~/.pypirc` to avoid entering credentials:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
```

## Option 2: Installing from GitHub

Users can install directly from GitHub without PyPI:

### Public Repository
```bash
# Install from main branch
pip install git+https://github.com/eladrave/autocoder.git

# Install specific version/tag
pip install git+https://github.com/eladrave/autocoder.git@v2.0.0

# Install specific branch
pip install git+https://github.com/eladrave/autocoder.git@develop

# Install with development dependencies
pip install "autocoder-ai[dev] @ git+https://github.com/eladrave/autocoder.git"
```

### Private Repository
```bash
# Using SSH (requires SSH key setup)
pip install git+ssh://git@github.com/eladrave/autocoder.git

# Using HTTPS with token
pip install git+https://{github_token}@github.com/eladrave/autocoder.git

# Using GitHub CLI
gh repo clone eladrave/autocoder && pip install ./autocoder
```

## Option 3: GitHub Releases

1. **Create a GitHub Release**:
   ```bash
   # Tag the release
   git tag -a v2.0.0 -m "Release version 2.0.0"
   git push origin v2.0.0
   ```

2. **Upload wheel to GitHub Release**:
   - Go to https://github.com/eladrave/autocoder/releases
   - Click "Draft a new release"
   - Choose your tag
   - Upload the `.whl` and `.tar.gz` files from `dist/`

3. **Users can install from release**:
   ```bash
   # Download and install wheel
   wget https://github.com/eladrave/autocoder/releases/download/v2.0.0/autocoder_ai-2.0.0-py3-none-any.whl
   pip install autocoder_ai-2.0.0-py3-none-any.whl
   ```

## Option 4: Private PyPI Server

For enterprise use, you can host your own PyPI server:

### Using devpi
```bash
# Install devpi
pip install devpi-server devpi-client

# Start server
devpi-server --start --init

# Upload package
devpi upload
```

### Using AWS CodeArtifact
```bash
# Configure AWS
aws codeartifact login --tool pip --domain my-domain --repository my-repo

# Upload package
twine upload --repository codeartifact dist/*
```

## Continuous Deployment

### GitHub Actions for PyPI
Create `.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Build and publish
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install build twine
        python -m build
        python -m twine upload dist/*
```

## Version Management

### Semantic Versioning
- MAJOR.MINOR.PATCH (e.g., 2.0.0)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Pre-release Versions
```python
__version__ = '2.1.0a1'  # Alpha
__version__ = '2.1.0b1'  # Beta
__version__ = '2.1.0rc1' # Release candidate
```

## Testing Installation

### Create Virtual Environment
```bash
# Test clean installation
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from PyPI
pip install autocoder-ai

# Test CLI
autocoder --version
autocoder --help

# Test imports
python -c "import autocoder; print(autocoder.__version__)"
```

## Troubleshooting

### Common Issues

1. **Name already taken on PyPI**:
   - Use a different name (e.g., `autocoder-ai` instead of `autocoder`)
   - Add namespace (e.g., `eladrave-autocoder`)

2. **Missing files in package**:
   - Check `MANIFEST.in` file
   - Verify `package_data` in `setup.py`
   - Use `include_package_data=True`

3. **Import errors after installation**:
   - Ensure all packages are listed in `packages=find_packages()`
   - Check `__init__.py` files exist in all packages

4. **Dependencies not installed**:
   - List all in `install_requires`
   - Test with `pip install -e .` locally

## Quick Start Commands

```bash
# For maintainers - publish new version
./scripts/publish.sh

# For users - install package
pip install autocoder-ai

# For developers - install from source
git clone https://github.com/eladrave/autocoder.git
cd autocoder
pip install -e ".[dev]"
```

## License

Remember to include a LICENSE file (MIT recommended) before publishing.
