# Publishing FastJSONDiff to PyPI

This guide explains how to publish the FastJSONDiff package to PyPI using GitHub Actions CI/CD.

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account on [TestPyPI](https://test.pypi.org/account/register/) for testing
3. **GitHub Repository**: Push your code to a GitHub repository

## Setup PyPI API Token

1. Go to your PyPI account settings
2. Navigate to "API tokens"
3. Create a new token with "Entire account" scope
4. Copy the token (it starts with `pypi-`)

## Setup GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token

## Publishing Process

### 1. Update Version

Before publishing, update the version number in both `pyproject.toml` and `Cargo.toml`:

```bash
# Using the provided script
python scripts/publish.py version --version 0.1.0

# Or manually update both files
```

### 2. Create a GitHub Release

1. Go to your GitHub repository
2. Click on "Releases" in the right sidebar
3. Click "Create a new release"
4. Set the tag version (e.g., `v0.1.0`)
5. Set the release title (e.g., `Version 0.1.0`)
6. Add release notes describing the changes
7. Click "Publish release"

### 3. Automatic Publishing

The GitHub Actions workflow will automatically:

1. Run tests on multiple platforms and Python versions
2. Build wheels for all supported platforms
3. Publish to PyPI when a release is published

## Manual Publishing (Alternative)

If you prefer to publish manually:

```bash
# Build the package
maturin build --release

# Publish to PyPI
maturin publish

# Or use the provided script
python scripts/publish.py build
python scripts/publish.py publish
```

## Testing on TestPyPI

Before publishing to PyPI, you can test on TestPyPI:

1. Create a `TEST_PYPI_API_TOKEN` secret in GitHub
2. Update the workflow to use TestPyPI for testing
3. Install from TestPyPI: `pip install -i https://test.pypi.org/simple/ fastjsondiff`

## Version Management

Follow semantic versioning (SemVer):

- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features, backward compatible
- `PATCH`: Bug fixes, backward compatible

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure your PyPI API token is correct and has the right permissions
2. **Version Already Exists**: Make sure you're using a new version number
3. **Build Failures**: Check that all tests pass locally before creating a release

### Local Testing

```bash
# Test the build process
maturin build --release

# Test installation
pip install target/wheels/fastjsondiff-*.whl

# Test functionality
python test_fastjsondiff.py
```

## Release Checklist

Before creating a release:

- [ ] All tests pass
- [ ] Version numbers updated in both `pyproject.toml` and `Cargo.toml`
- [ ] README.md is up to date
- [ ] CHANGELOG.md is updated (if you have one)
- [ ] GitHub Actions workflow is working
- [ ] PyPI API token is configured in GitHub secrets

## Security Notes

- Never commit your PyPI API token to the repository
- Use GitHub secrets to store sensitive information
- Regularly rotate your API tokens
- Use TestPyPI for testing before publishing to PyPI
