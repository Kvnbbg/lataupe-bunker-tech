# Project Velocity — Sprint 1 Execution Plan

## 1. Mission Focus
- **Sprint duration:** 2 weeks (10 working days)
- **Strategic intent:** Activate the highest-priority deliverables from the Expansion Blueprint to harden delivery infrastructure, unlock observability, and stage probabilistic alerting pilots without destabilizing the current MVP.
- **Primary success criteria:** Production-quality CI/CD baseline, instrumented telemetry flows, and an enhanced alert triage experience ready for user feedback.

## 2. Quantum Backlog Snapshot
| ID | Stream | Backlog Item | Description | Dependencies |
| --- | --- | --- | --- | --- |
| FEAT-01 | Features | Adaptive Alert Triage Workspace | Introduce role-aware alert queues with status transitions and audit trail to support security & resident roles. | Existing Flask routes, database schema alignment |
| FEAT-02 | Features | Sensor Replay Sandbox | Provide historical playback in dashboard for operations to analyze anomalies. | SQLite data availability, Chart.js components |
| OPT-01 | Optimization | Database Performance Hardening | Add SQLAlchemy session scoping, query indices, and caching for dashboard queries to cut P95 response time. | Migration scripts, ORM models |
| OPT-02 | Optimization | Telemetry Pipeline Foundations | Embed OpenTelemetry tracing + Prometheus metrics exporter in Flask service. | Application factory refactor, dependency addition |
| UIX-01 | UI/UX | Responsive Command Center Layout | Rebuild dashboard layout with Tailwind grid, dark mode polish, and accessibility fixes. | Tailwind build pipeline |
| UIX-02 | UI/UX | Incident Timeline Visualization | Add chronological incident heatmap and filters for analysts. | Sensor Replay Sandbox |
| DEP-01 | Deployment | Activate CI/CD Workflow | Operationalize GitHub Actions blueprint with lint, tests, SAST, SBOM upload, and status checks. | `.github/workflows` ownership, secrets |
| DEP-02 | Deployment | Harden Container Delivery | Convert Dockerfile to multi-stage build, sign images, and push to registry with provenance metadata. | Container registry access |
| GOV-01 | Governance | DORA Telemetry Collector | Automate deployment frequency and MTTR gathering from GitHub API and incident logs. | Observability stack |
| SEC-01 | Security | Vault-backed Secret Distribution | Stand up HashiCorp Vault integration for local + CI workflows. | Secrets management plan |

## 3. Sprint 1 Commitments
The squad will execute the following backlog items:

### 3.1 DEP-01 — Activate CI/CD Workflow
- **Key Tasks**
  1. Adapt `artifacts/ci/github-actions.yml` into production-ready workflows under `.github/workflows/` (build-test, security, deploy).
  2. Configure matrix testing for Python 3.11 & 3.12, execute pytest with coverage, run `pip-audit`, build container image, generate SBOM via Syft.
  3. Wire GitHub branch protection to require workflow success and CodeQL results.
- **Definition of Done**
  - Workflows pass on `main` and a test branch; coverage uploaded as artifact and summarized in PR comment.
  - Branch protection rule documented in `artifacts/security/branch-protection-policy.md` and enforced in repo settings.
  - SBOM published as build artifact and linked from README "CI/CD" section.
- **Acceptance Evidence**: GitHub Actions run history screenshots/logs, README diff, policy update commit.

### 3.2 OPT-02 — Telemetry Pipeline Foundations
- **Key Tasks**
  1. Introduce OpenTelemetry instrumentation within Flask app factory, exporting traces to OTLP endpoint with local collector manifest.
  2. Add Prometheus metrics exporter (e.g., `prometheus_flask_exporter`) capturing request latency, error count, and custom alert metrics.
  3. Document local observability stack startup in `SECURITY.md` (ops section) and `README` troubleshooting.
- **Definition of Done**
  - Application exposes `/metrics` with key counters/histograms; traces visible via local collector (e.g., Jaeger) per runbook.
  - Automated tests updated to validate metrics endpoint health.
  - Observability section added to Modernization Briefing referencing metrics & traces.

### 3.3 FEAT-01 — Adaptive Alert Triage Workspace
- **Key Tasks**
  1. Extend alert model with status (`new`, `acknowledged`, `resolved`) and assigned role fields via migration script.
  2. Build new Flask blueprint `routes/alerts.py` endpoints and templates for queue management, filtering by severity and role.
  3. Integrate websocket or Server-Sent Events channel for live updates, backed by caching layer (Redis in dev via docker-compose).
  4. Write end-to-end tests validating role-based access control and status transitions.
- **Definition of Done**
  - UI renders responsive triage board with accessibility compliance (keyboard navigation, aria labels).
  - Database migration reversible and documented; tests cover new workflow with >85% coverage on alert module.
  - Release notes prepared summarizing workflow change for bunker staff.

### 3.4 UIX-01 — Responsive Command Center Layout
- **Key Tasks**
  1. Introduce Tailwind build pipeline (npm + `tailwind.config.js`) and restructure static assets (`static/css`, `static/js`).
  2. Redesign dashboard template using CSS grid, dark-mode toggles, and improved typography for bunker displays.
  3. Run axe-core accessibility scan in CI (storybook or Playwright smoke test) and address violations.
- **Definition of Done**
  - Tailwind build integrated into CI workflow; compiled CSS committed or built dynamically depending on deploy target.
  - Lighthouse report >= 90 for accessibility & performance on dashboard page (documented in artifacts).
  - UX documentation updated with screenshots and interaction notes.

### 3.5 DEP-02 (Partial) — Harden Container Delivery (Spike)
- **Key Tasks**
  1. Produce spike document evaluating multi-stage Docker build, image signing (cosign), and registry options.
  2. Prototype multi-stage Dockerfile locally, recording build metrics and challenges.
- **Definition of Done**
  - Spike findings captured in `artifacts/planning/DEP-02-spike.md` with recommendation and next steps.
  - Decision review scheduled during Sprint 1 review for implementation commitment in Sprint 2.

## 4. Delivery Cadence & Ceremonies
- **Sprint Planning:** Day 1 — finalize estimates (story points) and align owner assignments.
- **Daily Quantum Stand-up:** Focus on blockers impacting entanglements (shared dependencies) and telemetry health.
- **Mid-Sprint Review (Day 6):** Validate CI pipeline runs, metrics endpoint availability, and UI prototypes with bunker stakeholders.
- **Sprint Review & Demo:** Day 10 — showcase alert workspace, metrics dashboards, CI pipeline, and share deployment readiness.
- **Retrospective:** Immediately post-review, capture process adjustments for Sprint 2 prioritization.

## 5. Feedback Loop Instrumentation
- **Metrics to Observe:**
  - P95 dashboard response time (Prometheus histogram `http_request_duration_seconds`).
  - Error rate (`http_request_errors_total`) correlated with new alert routes.
  - CI pipeline success rate and mean duration from GitHub Actions insights.
  - Deployment frequency (target: ≥2 per week) derived from DORA collector script (GOV-01 dependency).
- **Alerting Rules:**
  - Trigger regression alert if P95 latency > 1.5s for 3 consecutive scrapes post-deployment.
  - Trigger rollback if change failure rate exceeds 20% in sprint (more than 1 failed deployment requiring hotfix).
- **Validation Ritual:**
  - After each deployment, run smoke tests, check metrics dashboards, and log summary in `operations/journal/YYYY-MM-DD.md`.
  - Weekly telemetry review meeting to adjust backlog priorities.

## 6. Expected Impact on KPIs & DORA Metrics
| Target | Baseline | Sprint 1 Goal | Impact Rationale |
| --- | --- | --- | --- |
| Deployment Frequency | Ad-hoc manual releases | ≥2 production-simulated deploys/week | CI pipeline enables automated builds/tests unlocking faster releases. |
| Lead Time for Changes | >5 days (manual testing) | ≤2 days from merge to deploy | Automated tests + branch protection reduce waiting time. |
| Change Failure Rate | Unknown | Measured and ≤20% | Telemetry + rollback criteria provide visibility and guardrails. |
| MTTR | Undefined | Initial measurement established | Metrics & runbooks shorten detection and response.
| Dashboard P95 Latency | ~1.8s (est.) | ≤1.2s | Database optimization + Tailwind layout efficiency. |
| User Satisfaction (CSAT) | Not tracked | Collect first qualitative feedback | New alert workspace & UX improvements. |

## 7. Dependencies & Resource Allocation
- **Team Roles:**
  - Tech Lead (QEA) — ensures cross-stream coherence, merges.
  - Backend Engineer — FEAT-01, OPT-02 instrumentation.
  - Frontend Engineer — UIX-01 redesign, accessibility.
  - DevOps Engineer — DEP-01 workflows, DEP-02 spike.
  - QA Engineer — Automated tests, accessibility audits.
- **External Dependencies:** Access to GitHub repository settings, container registry sandbox, Redis/Telemetry infrastructure (docker-compose extension), stakeholder availability for UI validation.

## 8. Risks & Mitigations
| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| Telemetry libraries destabilize existing routes | Medium | High | Implement feature flag for metrics endpoint; add smoke tests before enabling globally. |
| Tailwind pipeline complicates deployment | Medium | Medium | Document build steps, cache node modules in CI, provide fallback CSS build. |
| Alert triage changes require data migration downtime | Low | High | Run online migration with backfill script and allow rollback via migration downgrade. |
| CI secrets unavailable | Low | Medium | Engage platform admin early; store secrets in temporary GitHub environment before Vault integration. |

## 9. Exit Criteria
Sprint 1 is deemed complete when:
- DEP-01, OPT-02, FEAT-01, UIX-01 meet their Definitions of Done and are merged into `main` with green pipelines.
- DEP-02 spike documented and reviewed.
- Metrics dashboard screenshot + report stored in `artifacts/observability/`.
- Sprint review slide deck archived in `artifacts/planning/reviews/2024-Sprint-1.md` (template prepared during sprint).
- Retrospective action items logged for Sprint 2 planning.

---
**Prepared by:** Quantum Engineering Agent (Tech Lead) — Project Velocity.
