# PyPI Publishing Guide

This guide explains how to publish the `toronto-open-data` package to PyPI using GitHub Actions and Trusted Publishing.

## 🚀 Overview

The package is automatically published to PyPI when you create a new release on GitHub. The workflow:
1. Runs tests to ensure quality
2. Builds the package
3. Publishes to PyPI using Trusted Publishing (no API tokens needed)

## 📋 Prerequisites

- **GitHub Repository**: Must be the official repository
- **PyPI Package**: Package must exist on PyPI
- **Repository Permissions**: Must have admin access to the repository

## 🔧 Setup Steps

### 1. Create the Package on PyPI (First Time Only)

If this is the first time publishing:

```bash
# Build the package locally
make build

# Upload to PyPI (you'll need PyPI credentials)
twine upload dist/*
```

### 2. Enable Trusted Publishing

The GitHub Actions workflow automatically sets up Trusted Publishing. When you create your first release:

1. Go to your GitHub repository
2. Create a new release with a tag (e.g., `v0.1.5`)
3. The workflow will run and create a Trusted Publisher
4. Follow the link in the workflow output to approve the Trusted Publisher

### 3. Verify Trusted Publisher

After the first release:
1. Go to [PyPI Trusted Publishers](https://pypi.org/manage/account/publishing/)
2. You should see a Trusted Publisher for your GitHub repository
3. The publisher will be automatically used for future releases

## 📝 Publishing Process

### Automatic Publishing (Recommended)

1. **Update Version**: Edit `pyproject.toml` and bump the version
   ```toml
   [project]
   version = "0.1.5"  # Increment this
   ```

2. **Commit and Push**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.1.5"
   git push origin main
   ```

3. **Create Release**:
   - Go to GitHub → Releases → "Create a new release"
   - Tag: `v0.1.5` (must match version in pyproject.toml)
   - Title: `Version 0.1.5`
   - Description: Add release notes
   - Click "Publish release"

4. **Monitor Workflow**:
   - The workflow will automatically run
   - Tests must pass before publishing
   - Check the Actions tab for progress

### Manual Publishing (Fallback)

If you need to publish manually:

```bash
# Build the package
make build

# Upload to PyPI (requires PyPI credentials)
twine upload dist/*
```

## 🔍 Troubleshooting

### Common Issues

1. **Tests Fail**: Fix any test failures before publishing
2. **Version Mismatch**: Ensure tag matches version in `pyproject.toml`
3. **Permission Denied**: Check repository permissions and Trusted Publisher status

### Workflow Debugging

1. **Check Actions Tab**: View workflow runs and logs
2. **Verify Trusted Publisher**: Check PyPI Trusted Publishers page
3. **Review Workflow File**: Ensure `.github/workflows/release.yml` is correct

### Trusted Publisher Issues

If Trusted Publishing isn't working:

1. **Check Repository**: Ensure it's the official repository
2. **Verify Permissions**: Must have admin access
3. **Manual Setup**: Follow PyPI's manual Trusted Publisher setup guide

## 📚 Resources

- [PyPI Trusted Publishers Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Packaging Guide](https://packaging.python.org/)

## 🎯 Best Practices

1. **Always Test**: Ensure tests pass before releasing
2. **Version Management**: Use semantic versioning
3. **Release Notes**: Provide clear descriptions of changes
4. **Tag Naming**: Use consistent tag format (`v*.*.*`)
5. **Automation**: Let GitHub Actions handle the publishing process

## 🔒 Security

- **No API Tokens**: Trusted Publishing eliminates the need for stored credentials
- **Repository Scoped**: Publishers only work for the specific repository
- **Audit Trail**: All publishing actions are logged and traceable
- **Automatic Rotation**: No need to manage or rotate API tokens
