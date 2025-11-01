# Secrets Management Plan

## Objectives
- Remove all hard-coded secrets and environment variables from the repository.
- Centralize credential storage using HashiCorp Vault with dynamic secrets for databases and third-party APIs.
- Provide developers with a secure workflow for local development.

## Implementation Steps
1. **Inventory Existing Secrets**
   - Use `detect-secrets` baseline to identify committed secrets.
   - Audit `.env.example`, deployment scripts, and CI variables for sensitive data.
2. **Provision Vault**
   - Deploy HashiCorp Vault (managed or self-hosted) with auto-unseal using cloud KMS.
   - Enable AppRole authentication for CI/CD and JWT auth for platform services.
3. **Define Secret Engines**
   - `kv-v2` for application configuration (Flask secret key, JWT secret, third-party tokens).
   - `database` engine for rotating PostgreSQL credentials when production database is introduced.
   - `transit` engine for cryptographic operations (encrypting resident PII if stored).
4. **Integrate with Application**
   - Replace `.env` loading with Vault client using short-lived tokens retrieved via AppRole during deployment.
   - Cache secrets in memory with TTL ≤ 1 hour; refresh automatically before expiry.
5. **Integrate with CI/CD**
   - Store Vault credentials (AppRole ID/Secret ID) in GitHub Actions secrets.
   - Fetch runtime secrets as part of deployment jobs and inject them via environment variables or files consumed by the container entrypoint.
6. **Operational Controls**
   - Enable audit logging and forward Vault logs to the centralized logging stack.
   - Configure alerting for secret rotation failures or unauthorized access attempts.

## Developer Experience
- Provide a `vault/README.md` quick-start for running Vault via Docker Compose locally.
- Offer mock secret provider for automated tests to avoid Vault dependency.
- Add pre-commit hook to run `detect-secrets` to prevent secret leaks.
