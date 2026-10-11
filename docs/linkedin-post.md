# LinkedIn post — draft

I’m building on my data engineering experience to move into AI engineering. My latest project puts that transition into practice: an AI Data Agent deployed on Databricks.

The application lets users ask questions about customer-support data, search product manuals, and extract and transform data from an approved API through one chat interface.

I built a LangGraph workflow that routes requests to three specialized paths:

• SQL analyst: schema context, SQL generation, SELECT-only validation, warehouse execution, and answer formatting.
• Document search: retrieval from extracted PDF text through Unity Catalog functions, with source filenames in responses.
• ETL analyst: bounded tool calls for API extraction and CSV transformation, with answers grounded in executed tool results.

My data engineering foundation helped with the tables, schemas, and data preparation. The AI engineering work extended into agent state, tool boundaries, model serving, service-principal permissions, and end-to-end verification.

The deployed stack includes Python, LangGraph, MLflow ResponsesAgent, Databricks Model Serving, Unity Catalog, a SQL warehouse, Gradio, and Declarative Automation Bundles. GitHub Actions runs the offline checks.

Verified results:
• SQL and app chat returned the warehouse-verified total of 1,023 tickets.
• Document search answered a product question with a PDF citation.
• ETL extracted and transformed 100 records into the requested columns.
• All four deployment checks passed; the latest local test run passed 19 tests.

One practical lesson: a successful deployment job does not guarantee a working AI application. Endpoint readiness, app permissions, and the full request path need their own checks.

This is a working portfolio deployment. ETL outputs are temporary, and broader answer-quality evaluation is still a next step.

I’m looking for AI Engineer and Applied AI Engineer opportunities where I can combine data engineering experience with agent development, LLM application integration, and deployment. If your team is hiring for that work, I’d welcome a conversation.

Project: https://github.com/Pratik2895/ai-data-agent

#AIEngineering #DataEngineering #Databricks #LangGraph #OpenToWork
