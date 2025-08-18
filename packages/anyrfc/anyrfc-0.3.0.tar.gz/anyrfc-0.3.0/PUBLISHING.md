# Publishing AnyRFC to PyPI

This document contains instructions for publishing `anyrfc` to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
2. **API Tokens**: Generate API tokens for both PyPI and TestPyPI
3. **Package Built**: Ensure the package builds successfully (already done)

## Setup Authentication

### Option 1: Using API Tokens (Recommended)

Create a `.pypirc` file in your home directory:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your-pypi-api-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-api-token>
```

### Option 2: Using Environment Variables

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your-pypi-api-token>
```

## Publishing Steps

### Step 1: Test on TestPyPI (Recommended)

```bash
# Build the package
uv build

# Upload to TestPyPI
uv run twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ anyrfc
```

### Step 2: Publish to PyPI

```bash
# Upload to PyPI
uv run twine upload dist/*
```

### Step 3: Verify Publication

```bash
# Install from PyPI
pip install anyrfc

# Test functionality
python -c "import anyrfc; print(f'✅ anyrfc {anyrfc.__version__} published successfully!')"
```

## Post-Publication Checklist

- [ ] Verify package appears on [PyPI](https://pypi.org/project/anyrfc/)
- [ ] Test installation with `pip install anyrfc`
- [ ] Update documentation links if needed
- [ ] Create GitHub release with tag `v0.1.1`
- [ ] Announce release on relevant platforms

## Package Information

- **Package Name**: `anyrfc`
- **Version**: `0.1.1`
- **Author**: Andrew M. Elgert
- **License**: MIT
- **Python Support**: 3.11+
- **Dependencies**: anyio, httpx, typing-extensions

## Built Files

The following files have been created and validated:

- `dist/anyrfc-0.1.1-py3-none-any.whl` (wheel distribution)
- `dist/anyrfc-0.1.1.tar.gz` (source distribution)

Both packages have passed `twine check` validation.

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure API token is correct and has upload permissions
2. **Package Exists**: If version already exists, increment version in `pyproject.toml`
3. **Metadata Issues**: Run `twine check dist/*` to validate package metadata

### Getting Help

- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Packaging Guide](https://packaging.python.org/)

## Security Notes

- **Never commit API tokens** to version control
- Use environment variables or `.pypirc` for authentication
- Regularly rotate API tokens
- Use trusted publishers when possible

## Future Releases

For future releases:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run tests: `uv run pytest`
4. Build: `uv build`
5. Test on TestPyPI first
6. Publish to PyPI
7. Create GitHub release
