# Databricks notebook source
# MAGIC %pip install pypdf==6.19.0
# COMMAND ----------
dbutils.library.restartPython()
# COMMAND ----------
config = PROJECT_CONFIG_LITERAL
from databricks.sdk import WorkspaceClient
from pypdf import PdfReader
from pathlib import Path
client = WorkspaceClient()
catalog, schema = config['catalog'], config['schema']
prefix = f'{catalog}.{schema}'
base = f"/Volumes/{catalog}/{schema}/{config['volume']}"
# The namespace and input volume must be provisioned by the user; no implicit ownership changes.
if config['mode'] == 'csv':
    # Never overwrite existing tables, even on a repeated setup run.
    existing = {t.name for t in client.tables.list(catalog_name=catalog, schema_name=schema)}
    collisions = existing & {t['name'] for t in config['tables']}
    if collisions:
        raise ValueError(f'Tables already exist: {sorted(collisions)}. Switch mode to existing to reuse them.')
    for table in config['tables']:
        name = table['name']
        spark.read.option('header', True).option('inferSchema', True).csv(f'{base}/{name}.csv').write.format('delta').mode('errorifexists').saveAsTable(f'{prefix}.{name}')
else:
    for table in config['tables']:
        client.tables.get(f"{prefix}.{table['name']}")
if 'KNOWLEDGE' in config['agents']:
    docs = []
    for path in sorted(Path(base, 'documents').glob('*.pdf')):
        docs.append((path.name, str(path), path.stat().st_size, [p.extract_text() or '' for p in PdfReader(path).pages]))
    if not docs:
        raise ValueError(f'KNOWLEDGE requires readable PDFs in {base}/documents')
    # Reserved derived table is refreshed; business tables are never overwritten.
    spark.createDataFrame(docs, 'file_name string, file_path string, file_size long, text_content array<string>').write.mode('overwrite').option('overwriteSchema',True).saveAsTable(f'{prefix}.product_docs')
print('Configured data sources are ready')
