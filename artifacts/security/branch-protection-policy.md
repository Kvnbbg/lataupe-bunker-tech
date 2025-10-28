# Branch Protection Policy

To maintain repository integrity and reduce change failure rate, apply the following protection rules on `main` and `develop` branches:

## Required Status Checks
- ✅ `CI / Lint & Test` job must succeed.
- ✅ `CI / Static Application Security Testing` job must succeed.
- ✅ `CI / Build Container Image` job must succeed.
- Enforce status checks before merging and require branches to be up to date with the base branch.

## Review Requirements
- Require at least **2 approving reviews** for pull requests targeting protected branches.
- Require review from the **CODEOWNERS** relevant to modified paths.
- Dismiss stale approvals when new commits are pushed.

## Commit History Controls
- Enforce signed commits and GPG signature verification.
- Prevent force pushes and deletion of protected branches.
- Require linear history to encourage frequent, small merges.

## Additional Safeguards
- Enable automatic security updates for dependencies.
- Require successful resolution of secret scanning and Dependabot alerts before merge.
- Restrict who can push to `main` and `develop` to the release and platform teams.

Document ownership: `@lataupe-bunker/security-office`.
