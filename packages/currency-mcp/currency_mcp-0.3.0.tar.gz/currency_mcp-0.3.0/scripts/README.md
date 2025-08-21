# Publishing Scripts

Simple shell scripts for publishing the `currency-mcp` package to PyPI.

## 📁 Scripts

- **`publish.sh`** - Master script that calls the appropriate tool script
- **`publish-pip.sh`** - Uses pip + build + twine
- **`publish-poetry.sh`** - Uses Poetry
- **`publish-uv.sh`** - Uses uv

## 🚀 Usage

### Master Script
```bash
./scripts/publish.sh [pip|poetry|uv] [test|prod]
```

### Individual Scripts
```bash
./scripts/publish-pip.sh test      # Test with pip
./scripts/publish-pip.sh prod      # Production with pip

./scripts/publish-poetry.sh test   # Test with Poetry
./scripts/publish-poetry.sh prod   # Production with Poetry

./scripts/publish-uv.sh test       # Test with uv
./scripts/publish-uv.sh prod       # Production with uv
```

## 🔐 Authentication

Set your PyPI credentials:

```bash
export TWINE_USERNAME=your_username
export TWINE_PASSWORD=your_api_token
```

Or create `~/.pypirc`:
```ini
[pypi]
username = your_username
password = your_api_token

[testpypi]
username = your_username
password = your_test_api_token
```

## 📋 What Each Script Does

### TestPyPI (test)
1. Builds the package
2. Checks the package
3. Uploads to TestPyPI
4. Tests installation from TestPyPI

### Production PyPI (prod)
1. Builds the package
2. Checks the package
3. Uploads to PyPI

## 🎯 Examples

```bash
# Test on TestPyPI with uv
./scripts/publish.sh uv test

# Production with pip
./scripts/publish.sh pip prod

# Test with Poetry
./scripts/publish.sh poetry test
```

That's it! Simple and straightforward. 🚀
