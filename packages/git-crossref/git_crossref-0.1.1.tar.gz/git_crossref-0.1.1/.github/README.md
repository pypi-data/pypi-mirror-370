# GitHub Actions CI/CD Pipeline

This directory contains the GitHub Actions workflows for the `git-crossref` project.

## Workflows Overview

### 🔄 CI Pipeline (`ci.yml`)
**Triggers**: Push to `main`/`develop`, Pull Requests

**Jobs**:
- **Code Quality**: Black formatting, Pylint, MyPy, Bandit security scan, Safety vulnerability check
- **Tests**: Multi-platform testing (Ubuntu, Windows, macOS) across Python 3.11 & 3.12
- **Integration Tests**: Real CLI testing with sample configurations
- **Package Test**: Build validation and installation testing
- **Security Scan**: Trivy vulnerability scanning
- **Schema Validation**: JSON schema syntax and sample config validation

### 🚀 Release Pipeline (`release.yml`)
**Triggers**: GitHub Releases, Manual dispatch

**Jobs**:
- **Validate Release**: Full test suite and package build validation
- **Publish to PyPI**: Automated PyPI publishing with version management
- **Create GitHub Release**: Automated release notes and tagging
- **Notify Release**: Success/failure notifications

### 🧹 Maintenance (`maintenance.yml`)
**Triggers**: Weekly schedule (Mondays 9 AM UTC), Manual dispatch

**Jobs**:
- **Dependency Security**: Safety and pip-audit vulnerability scanning
- **Code Quality**: Complexity analysis with radon, dead code detection
- **Test Coverage**: Coverage analysis and reporting
- **Performance Test**: Baseline performance benchmarking
- **Documentation Check**: Link validation and YAML sample verification
- **Cleanup**: Automatic artifact cleanup (30-day retention)

### 🤖 Dependabot Auto-merge (`dependabot-auto-merge.yml`)
**Triggers**: Dependabot Pull Requests

**Features**:
- Auto-approves and merges patch/minor dependency updates
- Requires manual review for major version updates
- Runs tests before auto-merging
- Adds informative comments for manual review cases

## Configuration Files

### 📋 Dependabot (`dependabot.yml`)
- **Python dependencies**: Weekly updates, grouped by type
- **GitHub Actions**: Weekly updates for workflow dependencies
- **Auto-assignment**: PRs assigned to maintainers
- **Smart grouping**: Development vs production dependencies

## Required Secrets

To use these workflows, configure the following secrets in your GitHub repository:

### For Release Pipeline
- `PYPI_API_TOKEN`: PyPI API token for publishing packages

### Optional Secrets
- `CODECOV_TOKEN`: For enhanced Codecov integration (optional)

## Workflow Status Badges

Add these badges to your README.md:

```markdown
[![CI](https://github.com/aesteve-rh/git-crossref/workflows/CI/badge.svg)](https://github.com/aesteve-rh/git-crossref/actions/workflows/ci.yml)
[![Release](https://github.com/aesteve-rh/git-crossref/workflows/Release/badge.svg)](https://github.com/aesteve-rh/git-crossref/actions/workflows/release.yml)
[![Maintenance](https://github.com/aesteve-rh/git-crossref/workflows/Maintenance/badge.svg)](https://github.com/aesteve-rh/git-crossref/actions/workflows/maintenance.yml)
```

## Usage Instructions

### Running CI Locally
To run similar checks locally:

```bash
# Code quality
black --check src/ tests/
pylint src/git_crossref/
mypy src/git_crossref/

# Security
bandit -r src/git_crossref/
safety check

# Tests
pytest tests/ --cov=src/git_crossref

# Package build
python -m build
twine check dist/*
```

### Manual Release
To trigger a manual release:

1. Go to Actions → Release workflow
2. Click "Run workflow"
3. Enter the version number (e.g., `0.2.0`)
4. The workflow will handle the rest

### Monitoring
- **Security alerts**: Check Issues for auto-created vulnerability reports
- **Coverage reports**: Available in workflow artifacts
- **Performance**: Baseline reports generated weekly

## Customization

### Adding New Checks
To add new quality checks:

1. Add the tool installation to the CI workflow
2. Add the check command
3. Consider adding it to the local development setup

### Modifying Auto-merge Rules
Edit `dependabot-auto-merge.yml` to change which updates are auto-merged:

- Modify the grep pattern in the PR title check
- Add more sophisticated version comparison logic
- Adjust test requirements

### Changing Schedules
Modify the `cron` expressions in workflow files:
- Current: Weekly on Mondays at 9 AM UTC
- Format: `'minute hour day month weekday'`

## Troubleshooting

### Common Issues

1. **PyPI Upload Fails**: Check that `PYPI_API_TOKEN` is correctly set
2. **Tests Fail on Windows**: Path separator issues, check test fixtures
3. **Security Scans Fail**: Review and update vulnerable dependencies
4. **Auto-merge Not Working**: Verify Dependabot is enabled and branch protection allows it

### Debug Workflows
- Check workflow logs in the Actions tab
- Download artifacts for detailed reports
- Use `workflow_dispatch` triggers for manual testing
