# Branch Protection Configuration

This document describes how to configure GitHub branch protection rules for the schedulo-api repository to ensure code quality and prevent deployment of failing code.

## Required Branch Protection Rules

### Main Branch Protection

Navigate to `Settings > Branches > Add rule` and configure the following for the `main` branch:

#### Basic Settings
- **Branch name pattern**: `main`
- **Restrict pushes that create matching branches**: ✓ Enabled

#### Protect matching branches
- **Require a pull request before merging**: ✓ Enabled
  - **Require approvals**: 1 required review
  - **Dismiss stale PR approvals when new commits are pushed**: ✓ Enabled
  - **Require review from code owners**: ✓ Enabled (if CODEOWNERS file exists)

#### Status Checks
- **Require status checks to pass before merging**: ✓ Enabled
- **Require branches to be up to date before merging**: ✓ Enabled
- **Required status checks**:
  - `test (3.10)`
  - `test (3.11)`
  - `test (3.12)`
  - `build-package`
  - `integration-test` (if PR)
  - `pre-commit`

#### Additional Restrictions
- **Restrict pushes that create matching branches**: ✓ Enabled
- **Allow force pushes**: ❌ Disabled
- **Allow deletions**: ❌ Disabled

### Development Branch Protection

Configure similar rules for the `dev` branch:

#### Basic Settings
- **Branch name pattern**: `dev`

#### Protect matching branches
- **Require a pull request before merging**: ✓ Enabled
  - **Require approvals**: 1 required review
  - **Dismiss stale PR approvals when new commits are pushed**: ✓ Enabled

#### Status Checks
- **Require status checks to pass before merging**: ✓ Enabled
- **Required status checks**:
  - `test (3.10)`
  - `pre-commit`

## Setting Up Status Checks

The following GitHub Actions workflows must complete successfully:

### 1. CI/CD Pipeline (`.github/workflows/ci.yml`)
- Runs tests on Python 3.10, 3.11, 3.12
- Performs code quality checks (linting, type checking, formatting)
- Builds the package
- Runs security scans

### 2. Pre-commit Checks (`.github/workflows/pre-commit.yml`)
- Runs pre-commit hooks
- Validates code formatting and basic checks

## Manual Setup Steps

1. **Go to Repository Settings**
   - Navigate to your GitHub repository
   - Click `Settings` tab
   - Select `Branches` from the left sidebar

2. **Add Branch Protection Rule**
   - Click `Add rule`
   - Enter branch name pattern: `main`
   - Configure protection settings as specified above

3. **Set Up Required Status Checks**
   - After running CI workflows at least once, the status check names will be available
   - Select the required checks from the dropdown
   - Ensure `Require branches to be up to date before merging` is checked

4. **Configure Admin Settings**
   - **Include administrators**: ✓ Enabled (admins must follow rules too)
   - **Allow force pushes**: ❌ Disabled
   - **Allow deletions**: ❌ Disabled

## Required Secrets

Add the following secrets in `Settings > Secrets and variables > Actions`:

- `CODECOV_TOKEN`: Token for code coverage reporting (optional)
- `PYPI_TOKEN`: API token for publishing to PyPI (for releases)

## CODEOWNERS File

Create a `.github/CODEOWNERS` file to require specific people to review changes:

```
# Global owners
* @yourusername

# Python source code
src/ @yourusername

# CI/CD and workflows
.github/ @yourusername

# Documentation
*.md @yourusername
```

## Testing Branch Protection

To verify branch protection is working:

1. **Create a test branch**:
   ```bash
   git checkout -b test-protection
   echo "test" > test.txt
   git add test.txt
   git commit -m "test: verify branch protection"
   git push origin test-protection
   ```

2. **Create a Pull Request**:
   - Open PR from `test-protection` to `main`
   - Verify that status checks are required
   - Verify that review is required

3. **Test Failure Handling**:
   - Add a failing test or break the linting
   - Push the change and verify PR cannot be merged

4. **Clean up**:
   ```bash
   git checkout main
   git branch -D test-protection
   git push origin --delete test-protection
   ```

## Enforcement Results

Once properly configured, the following will be enforced:

- ✅ **No direct pushes to main/dev**: All changes must go through pull requests
- ✅ **All tests must pass**: CI pipeline must complete successfully
- ✅ **Code review required**: At least one approval needed
- ✅ **Up-to-date branches**: Branches must be current with target before merge
- ✅ **Quality gates**: Linting, type checking, and formatting must pass
- ✅ **Security checks**: Bandit security scan must pass

## Troubleshooting

### Status Checks Not Appearing
- Ensure workflows have run at least once on the target branch
- Check that workflow names exactly match the status check names
- Verify workflows are triggered on `pull_request` events

### Cannot Merge Despite Green Checks
- Verify branch is up to date with target branch
- Check if all required status checks are listed
- Ensure admin bypass is not preventing enforcement

### Failed Status Checks
- Review the Actions tab to see which checks failed
- Fix the underlying issues (test failures, linting errors, etc.)
- Push new commits to update the PR

This configuration ensures that only high-quality, tested code reaches the main branch while maintaining a smooth development workflow.
