# LFX Release Guide

This guide describes how to release a new version of LFX.

## Prerequisites

1. Ensure you have push access to the repository
2. Ensure you have PyPI publishing permissions (or use GitHub's trusted publishing)
3. Ensure GitHub Actions secrets are configured:
   - `DOCKER_USERNAME` and `DOCKER_PASSWORD` for Docker Hub
   - PyPI publishing is handled via OIDC (no tokens needed)

## Release Process

### 1. Prepare the Release

Run the release preparation script from the repository root:

```bash
./scripts/release-lfx.sh 0.1.0
```

This script will:
- Validate the version format
- Update version in `src/lfx/pyproject.toml`
- Run tests to ensure everything works
- Build the package to verify
- Create a git commit and tag

### 2. Push Changes

Push the commit and tag to GitHub:

```bash
git push origin HEAD
git push origin lfx-v0.1.0
```

### 3. Run the Release Workflow

1. Go to [GitHub Actions - LFX Release](https://github.com/langflow-ai/langflow/actions/workflows/release-lfx.yml)
2. Click "Run workflow"
3. Enter the version (e.g., `0.1.0`)
4. Select options:
   - **Publish to PyPI**: Yes (for production releases)
   - **Build Docker images**: Yes (for production releases)
   - **Docker platforms**: `linux/amd64,linux/arm64` (default)
   - **Pre-release**: No (unless it's a beta/RC)
   - **Create GitHub release**: Yes

### 4. Monitor the Release

The workflow will:
1. Validate the version matches pyproject.toml
2. Run tests on Python 3.10, 3.11, 3.12, and 3.13
3. Build the distribution package
4. Publish to PyPI
5. Build and push Docker images (standard and alpine variants)
6. Create a GitHub release with artifacts
7. Test the released packages

### 5. Verify the Release

After the workflow completes:

1. **Check PyPI**: https://pypi.org/project/lfx/
2. **Check Docker Hub**: https://hub.docker.com/r/langflowai/lfx/tags
3. **Check GitHub Release**: https://github.com/langflow-ai/langflow/releases/tag/lfx-v0.1.0

Test the release:

```bash
# Test PyPI installation
pip install lfx==0.1.0
lfx --help

# Test Docker
docker run --rm langflowai/lfx:0.1.0 lfx --help
docker run --rm langflowai/lfx:0.1.0-alpine lfx --help
```

## Version Numbering

LFX follows semantic versioning:
- **Major**: Breaking changes (1.0.0)
- **Minor**: New features, backward compatible (0.1.0)
- **Patch**: Bug fixes (0.1.1)
- **Pre-release**: Beta/RC versions (0.1.0-beta.1)

## Rollback Procedure

If something goes wrong:

1. **PyPI**: Cannot delete, but can yank the release
   ```bash
   pip install twine
   twine yank lfx==0.1.0
   ```

2. **Docker Hub**: Delete the tag from Docker Hub UI

3. **GitHub**: Delete the release and tag
   ```bash
   git push --delete origin lfx-v0.1.0
   git tag -d lfx-v0.1.0
   ```

## Manual Release (Emergency)

If GitHub Actions is down:

```bash
# Build
cd src/lfx
uv build

# Upload to PyPI
pip install twine
twine upload dist/*

# Build Docker
docker build -f docker/Dockerfile -t langflowai/lfx:0.1.0 ../..
docker push langflowai/lfx:0.1.0
```

## Integration with Main Langflow Release

LFX can be released independently of Langflow. However, if you want to coordinate releases:

1. Update Langflow's dependencies to use the new LFX version
2. Test the integration
3. Release both together using their respective workflows

## Troubleshooting

### Version already exists on PyPI
- The workflow will fail early with a clear message
- Bump the version and try again

### Docker build fails
- Check the Dockerfile for syntax errors
- Ensure all dependencies are available
- Check Docker Hub rate limits

### Tests fail in CI but pass locally
- Check for environment-specific issues
- Review the test logs in GitHub Actions
- Ensure all test dependencies are in pyproject.toml

## Release Checklist

- [ ] Version updated in pyproject.toml
- [ ] Tests pass locally
- [ ] CHANGELOG updated (if maintaining one)
- [ ] README is accurate for the new version
- [ ] Docker images build successfully
- [ ] No hardcoded version strings in code
- [ ] All new features are documented
- [ ] Breaking changes are clearly noted