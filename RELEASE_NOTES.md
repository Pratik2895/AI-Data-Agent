# v0.1.0 — Databricks Multi-Agent Starter Kit

Build an agent over your own Databricks tables and documents with a validated
configuration file and a generated, independent deployment bundle.

Start with [the quickstart](docs/QUICKSTART.md). Use `examples/sales/project.json`
and `orders.csv` for a small reproducible example. Configure existing tables,
optional PDF retrieval and explicitly approved ETL APIs for your own domain.

The original customer-support deployment and public architecture page remain
available as a reference implementation. Generated projects use their own names,
workspace profile, data namespace and serving endpoint.

This is an initial portfolio/developer release. Read CHANGELOG.md for boundaries.
No hosted Databricks account, compute allowance, source customer data, or API
credentials are included. Cloud deployment requires your own permissions and capacity.

## Validation

- 34 local tests passed, including configuration rejection, table allowlists,
  disabled-agent routing, standalone generation and verification failure cases.
- Python compilation passed.
- Generated job-only and app-enabled bundles both passed strict Databricks CLI
  validation against the configured workspace; the resolved app name was checked.
- The generic starter was not newly deployed end-to-end for this release. The
  existing customer-support model v5 has separate, earlier live verification.

MIT licensed. The fictional sales CSV can be redistributed with the starter.
