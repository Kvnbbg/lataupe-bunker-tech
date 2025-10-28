# DORA Metrics Implementation Plan

## Objectives
- Instrument and report on the four DORA metrics to evaluate delivery performance.
- Automate data collection where possible and visualize trends for leadership.

## Metrics & Data Sources
1. **Deployment Frequency**
   - Source: GitHub Actions deployment workflow runs tagged with `environment: production`.
   - Action: Standardize deployment workflow name `deploy-production` and export run metadata via GitHub API.
2. **Lead Time for Changes**
   - Source: Git history and pull request metadata (merge commit timestamp vs. first commit timestamp).
   - Action: Nightly scheduled job aggregates metrics using the `gh api repos/:owner/:repo/pulls` endpoint.
3. **Change Failure Rate**
   - Source: Incident tickets in issue tracker labeled `type:incident` linked to deployment IDs.
   - Action: Add checklist in deployment template to link incidents; analyze ratio of failed deployments to total deployments per week.
4. **Mean Time to Restore (MTTR)**
   - Source: Incident issue open/close timestamps.
   - Action: Require post-incident reviews to update resolution timestamp; scheduled report calculates average duration.

## Implementation Steps
1. Create a `scripts/metrics` package with Python utilities to call GitHub and issue tracker APIs.
2. Schedule a weekly GitHub Actions workflow (`metrics.yml`) to run the aggregation script and publish JSON/CSV artifacts.
3. Store aggregated metrics in an S3 bucket (or GitHub Pages branch) and visualize via Grafana or Looker Studio dashboard.
4. Share dashboard links in the engineering Slack channel and review metrics during weekly ops meeting.
5. Iterate quarterly on metric definitions to ensure alignment with product and ops goals.

## Ownership
- Metrics tooling owner: `@lataupe-bunker/architecture-council`.
- Reporting owner: `@lataupe-bunker/platform-team`.
