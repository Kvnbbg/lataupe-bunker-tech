# CodeQL Advanced Setup Review

This document captures the tailored CodeQL configuration for the Lataupe Bunker Tech repository and maps it to the official GitHub Advanced setup guidance.

## Objectives

1. **Enforce repeatable security scanning** leveraging GitHub-hosted runners and CodeQL Advanced configuration.
2. **Align with GitHub's recommended practices** for language selection, query packs, and result triage.
3. **Document repository-specific inclusions/exclusions** to reduce noise and focus findings on production code paths.

## Workflow Configuration

- **Workflow file**: `.github/workflows/codeql.yml`
- **Trigger strategy**: Executes on pushes and pull requests to `main` and `develop`, and runs a scheduled scan every Monday at 06:00 UTC.
- **Languages analyzed**: Python (matrix-driven for easy expansion).
- **Artifacts**: SARIF results are uploaded for historical tracking and offline triage.

Key implementation choices based on [GitHub's Advanced setup guide](https://docs.github.com/en/code-security/code-scanning/creating-an-advanced-setup-for-code-scanning/customizing-your-advanced-setup-for-code-scanning):

| Recommendation | Implementation |
| --- | --- |
| Use a dedicated advanced workflow | `.github/workflows/codeql.yml` initializes CodeQL with `build-mode: none` for Python and disables fail-fast for broader coverage. |
| Apply a configuration file for custom query selection | `.github/codeql/codeql-config.yml` defines security-focused query packs and filters out low-severity warnings. |
| Restrict analysis to relevant directories | `paths` target `src/`, `app/`, and root-level Python modules while `paths-ignore` excludes test fixtures, media assets, and generated content. |
| Capture SARIF artifacts for triage | Workflow uploads SARIF output (`codeql-sarif/`) as an artifact after each run. |

## Configuration File

The repository-level configuration can be tuned as the codebase evolves:

```yaml
name: "lataupe-bunker-tech"
description: "Custom CodeQL configuration aligned with Lataupe Bunker Tech modernization goals."
queries:
  - uses: security-extended
  - uses: security-and-quality
paths:
  - src
  - app
  - '*.py'
paths-ignore:
  - tests
  - DATA
  - music
  - story
  - images
  - instance
  - __pycache__
query-filters:
  - exclude:
      problem.severity: warning
```

## Integration with GitHub Code Scanning

- **Default configuration baseline**: The GitHub UI shows two prior automatic CodeQL setup attempts ([cb352878](https://github.com/Kvnbbg/lataupe-bunker-tech/security/code-scanning/tools/CodeQL/status/configurations/automatic/cb352878fc00ce92fa0e7ca94fa2a7f880ac2ea080dda214800273fd201f0d6b) and [5d08659](https://github.com/Kvnbbg/lataupe-bunker-tech/security/code-scanning/tools/CodeQL/status/configurations/automatic/5d08659845ad3b91205b0b520d61773e1e8910862573306bebfc686b0dcca762)) that can now be superseded by the advanced workflow.
- **Repository security view**: After merging, the new workflow will appear under [Security → Code scanning alerts](https://github.com/Kvnbbg/lataupe-bunker-tech/security/code-scanning) with configuration status tracked [here](https://github.com/Kvnbbg/lataupe-bunker-tech/security/code-scanning/tools/CodeQL/status/configurations/automatic).
- **Alert triage**: SARIF uploads enable GitHub's code scanning UI to surface actionable findings. Dismissals or suppressions should be captured via alert tracking issues or future ADRs.

## Next Steps

1. **Enable required status checks** for `CodeQL Advanced` on protected branches once the workflow runs successfully.
2. **Tune filters** as noise is evaluated; consider re-enabling selected warnings or adding `exclude` entries for generated code.
3. **Extend coverage** by adding JavaScript/TypeScript or Infrastructure-as-Code scanning if those stacks are introduced.
4. **Automate alert ownership** via CODEOWNERS mappings for SARIF paths to ensure the right teams triage results quickly.

---
Maintainer: `@lataupe-bunker/secops`
