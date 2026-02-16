# Repository Audit Reusable Workflow

This directory contains a reusable GitHub Actions workflow for auditing repository health and compliance.

## Workflows

### `repository-audit.yml` - Reusable Repository Audit

A reusable workflow that audits a repository against Ed-Fi DevSecOps standards.

**Features:**

- Runs on a single repository (defaults to the calling repository)
- Outputs results to GitHub Actions job summary (not HTML files)
- Excludes the "requires signed commits" check

**Usage:**

```yaml
name: Audit My Repository
on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

permissions: read-all

jobs:
  audit:
    uses: Ed-Fi-Alliance-OSS/DevSecOps/.github/workflows/repository-audit.yml@main
    permissions:
      actions: read
      contents: read
      pull-requests: read
      security-events: read
    secrets: inherit
```

**Inputs:**

- `repository` (optional): Name of the repository to audit. Defaults to the current repository.

**Secrets:**

- Uses the built-in `GITHUB_TOKEN` automatically (no secret configuration needed).

### `test-repository-audit.yml` - Test Workflow

A test workflow that demonstrates how to call the reusable `repository-audit.yml` workflow.

This workflow runs on:

- Manual trigger (`workflow_dispatch`)
- Pull requests that modify audit-related files

## Audit Checks

The repository audit performs the following checks:

- **Has Actions**: Repository uses GitHub Actions
- **Uses only approved GitHub Actions**: Uses approved actions
- **Uses Test Reporter**: Test results are uploaded to GitHub Actions
- **Has Unit Tests**: Repository has unit tests
- **Has NOTICES**: Has NOTICES.md file
- **Has CODE_OF_CONDUCT**: Has CODE_OF_CONDUCT.md file
- **Wiki Disabled**: Repository wiki is disabled
- **Issues Enabled**: Repository issues are enabled
- **Projects Disabled**: Repository projects are disabled
- **Deletes head branch**: Auto-deletes head branches on merge
- **Uses Squash Merge**: Squash merge is enabled
- **License Information**: Repository has license information
- **Dependabot Enabled**: Dependabot is enabled
- **Dependabot Alerts**: No old critical/high severity alerts

## Development

The audit logic is implemented in the `edfi-repo-auditor` Python package. See the [edfi-repo-auditor README](../edfi-repo-auditor/README.md) for more information.
