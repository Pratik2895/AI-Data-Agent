# Changelog

## 0.1.0 — 2026-10-11

First Databricks Multi-Agent Starter Kit release.

- Validated JSON configuration and standalone DAB generator.
- Existing-table and non-overwriting CSV onboarding modes.
- Configurable SQL, ETL and document workflows; disabled routes decline requests.
- SQL table allowlist and MLflow dependencies generated from project configuration.
- Optional PDF ingestion and document search; explicit ETL hostname allowlist.
- Serving readiness/version checks and user-defined endpoint/app smoke checks.
- Five-row fictional sales dataset, onboarding guide, MIT license and release packaging.

The original customer-support app remains the reference example. Its model v5
passed four live checks. The generic release has separate validation evidence;
those earlier results must not be presented as a fresh generic deployment test.

### Scope

One catalog/schema per project; simple SQL identifiers; JSON configuration.
Lexical PDF retrieval, no OCR or Vector Search. Temporary CSV ETL output.
App authentication uses a service principal: access is shared at the app level,
not delegated per user. Verification uses expected substrings, not semantic accuracy
evaluation. Existing business tables are not overwritten. Model provider packages
may evolve; `databricks-agents` remains unpinned as in the reference deployment.
