# v0.1.0: build your own Databricks agent

This release generates a **separate project** from a JSON configuration. The root
bundle is the author's customer-support example; do not deploy it into your
workspace unchanged. Start from the versioned release or GitHub template.

## 1. Prerequisites

- Python 3.11, uv, Git and Databricks CLI 1.0 or newer.
- A Databricks workspace with serverless notebook jobs, Model Serving, Apps,
  Unity Catalog and a SQL warehouse. Use your own account and compute budget.
- Access to the configured LLM endpoints. The example names are suggestions;
  verify availability and tool-calling support in your workspace.
- An existing catalog/schema dedicated to this project. For CSV/PDF onboarding,
  create a managed volume in it and grant the job identity read access to its files.
- The job identity needs USE CATALOG/SCHEMA, SELECT on existing source tables,
  warehouse CAN USE, function/model creation privileges, and table creation for
  ingestion. App deployment and serving creation need appropriate workspace rights.
  Exact grants depend on your workspace policies; preflight does not grant access.

All configured tables must belong to the same catalog/schema. v0.1.0 supports
simple names containing letters, digits and underscores, starting with a letter
or underscore. Table descriptions are context for the model, not executable code.

## 2. Install and configure

```powershell
git clone https://github.com/Pratik2895/ai-data-agent.git
cd ai-data-agent
git checkout v0.1.0
uv venv --python 3.11
uv pip install --python .venv/Scripts/python.exe -r requirements.txt -r requirements-starter.txt -r src/app/requirements.txt pytest
databricks auth login --profile my-workspace
Copy-Item examples/sales/project.json my-project.json
```

On macOS/Linux use `.venv/bin/python` and `cp` instead of the Windows commands.
Edit `my-project.json`: profile, HTTPS host, warehouse, catalog/schema/volume,
project name, models, table descriptions, enabled agents and checks. No tokens or
secrets belong in this file. Keep it private if it contains sensitive resource names.

The sales example enables SQL only and expects **five orders**. `checks[].contains`
is a case-insensitive substring check, not an exact numeric or semantic evaluator;
choose discriminating expected values and review outputs. For another dataset,
replace both the questions and expectations with facts you have verified.

## 3. Bring your data

**CSV mode:** upload `examples/sales/orders.csv` to
`/Volumes/<catalog>/<schema>/<volume>/orders.csv`. One CSV per configured table,
with a header row. For example:

```powershell
databricks fs cp examples/sales/orders.csv dbfs:/Volumes/YOUR_CATALOG/YOUR_SCHEMA/YOUR_VOLUME/orders.csv --profile my-workspace
```

The job infers column types and creates Delta tables. It refuses to overwrite
existing business tables. On subsequent setup runs, change `mode` to `existing`
and regenerate the bundle. Ingestion is not transactional across multiple tables;
after a partial failure inspect the created tables before rerunning. For strict
typing or large production datasets, prepare governed tables yourself.

**Existing mode:** set `mode` to `existing` and list your current tables. Setup
verifies them and creates schema context without rewriting their data.

**Optional documents:** add `KNOWLEDGE` to `agents` and put PDFs in
`/Volumes/<catalog>/<schema>/<volume>/documents/`. Setup refreshes the reserved
derived table `product_docs`; do not store unrelated data in that name. Only
text PDFs are supported, not scanned documents without prior OCR. PDF ingestion
collects text on the driver and is intended for small document collections.

**Optional ETL:** add `ETL` and explicitly list approved public API hostnames in
`allowed_hosts`. The APIs must return JSON without separate credentials; redirects
are rejected. The example `jsonplaceholder.typicode.com` is an external test API,
not included data. Output CSVs live temporarily on a serving instance, so requests
to different instances or after scale-to-zero may not find earlier files.

## 4. Validate and generate

```powershell
.venv/Scripts/python.exe -m starter.preflight --config my-project.json
.venv/Scripts/python.exe -m starter.preflight --config my-project.json --online
.venv/Scripts/python.exe -m starter.generate --config my-project.json --output generated/my-agent
cd generated/my-agent
databricks bundle validate --strict --profile my-workspace
```

The generator refuses existing output directories. Configuration is baked into
notebooks: editing the generated `project.json` alone does not reconfigure the
runtime. Edit your original config and generate into a new directory, retaining
the same project name and deployment target to update the same bundle.

The App resource is staged in `app.resource.yml` until the endpoint exists.
Generated app names default to a project prefix plus the current user's domain-
friendly name. Inspect the resolved name: lowercase letters/digits/hyphens, at
most 30 characters. If too long, persist a unique shorter name in
`.databricks/bundle/dev/variable-overrides.json`:

```json
{"app_name":"sales-agent-yourname","endpoint_name":"sales-agent-yourname-endpoint"}
```

Choose resource names unique to you. Preserve this override when regenerating.
Inspect the validated bundle before deploying; setup can incur compute charges.

## 5. Deploy and wait for serving

```powershell
databricks bundle deploy --profile my-workspace
databricks bundle run setup --profile my-workspace
uv run --no-project --with PyYAML==6.0.3 python enable_app.py
databricks bundle validate --strict --profile my-workspace
databricks bundle deploy --profile my-workspace
databricks bundle run agent_app --profile my-workspace
```

The job prepares data, creates only enabled tools, logs the configured model
resources, and deploys the endpoint. It waits up to 30 minutes for READY /
NOT_UPDATING and 100% traffic to the new version. Failed or timed-out provisioning
fails the job. Inspect serving logs/capacity before rerunning; repeated model
deployments may retain old versions and consume free-tier concurrency.

Enable the App after the endpoint is ready, so resource binding never references
a nonexistent endpoint. Rerunning `enable_app.py` is safe. Inspect the resolved
app name and apply a shorter override if needed before the second deployment.

Apps use uploaded local source by default. If your workspace requires Git-backed
Apps, commit the generated project to your own repository. Replace the App's
`source_code_path` in its bundle with:

```yaml
git_repository:
  url: https://github.com/YOUR_ORG/YOUR_GENERATED_PROJECT.git
  provider: gitHub
git_source:
  branch: main
  source_code_path: src/app
```

Configure Databricks Git access and push before deployment. If the generated
project is in a repository subfolder, include that prefix in `source_code_path`.

## 6. Verify the full request path

From your generated directory, install its verification dependencies in a local
environment, then use the actual resolved resource names:

```powershell
uv venv --python 3.11
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe verify.py --endpoint YOUR_ENDPOINT --app YOUR_APP
```

Each configured question is checked against both the serving endpoint and the
app API. The report is local and contains answers, not credentials. Review it
before sharing if your data is sensitive. The App's resource binding requests
CAN_QUERY. If an endpoint was recreated, inspect that permission for the app
service principal; reapply it through your authorized workspace process.

## Security and customization

- SQL executes with serving credentials and a configured table allowlist, in
  addition to Unity Catalog permissions. It cannot modify business tables.
- Apps use their service principal. Every authorized app user shares that data
  access; this release does not implement per-user data authorization.
- The router chooses one enabled specialist per request. It does not automatically
  chain all agents together. ETL/document loops have a 20-step limit.
- API hostname allowlisting is not a replacement for workspace egress controls;
  use only trusted hosts. No arbitrary generated Python is executed.
- Add evaluation cases for your domain before production use. No accuracy or
  safety guarantee follows from a handful of smoke tests.
- For new tools, extend `src/agents/runtime.py` and the specialist graph, declare
  required resources in the deployment notebook, and add tests.

## Updating and cleanup

Keep your config and generated bundle in your own version control. Review release
changes before regenerating and redeploying. Pin a release tag for reproducibility.
There are no breaking-change guarantees before 1.0.

`databricks bundle destroy` removes bundle-managed jobs/apps after confirmation;
it does **not** remove notebook-created tables/functions, volumes, registered
models or serving endpoints. Inventory those by your project namespace and remove
only resources you own through Databricks. Do not delete a shared warehouse or catalog.

The fictional five-row CSV is included under the repository's MIT license.
