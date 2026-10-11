# LinkedIn post — draft

I’m taking my data engineering experience into AI engineering by building and deploying AI applications that work with data.

My latest project: a Multi-Agent AI Data Agent on Databricks, with three specialized workflows behind one chat interface.

Here’s what each agent does:

🔹 SQL Analyst
Turns a business question into a read-only query over customer-support tables. It adds schema context, generates SQL, validates it, runs an accepted query on a SQL warehouse, and explains the results.

🔹 ETL Analyst
Extracts JSON from an approved API and transforms it using bounded tools: selecting columns, removing duplicates, dropping nulls, and inspecting CSV data. Its final summary comes from executed tool results.

🔹 Knowledge Agent
Searches extracted product-manual text through Unity Catalog functions and answers documentation questions with source filenames.

How does the orchestration work?

User question → LangGraph router → selected specialist → data/tool execution → answer in chat.

The router classifies the latest request as SQL, ETL, or KNOWLEDGE. SQL follows a staged validation and execution graph. ETL and knowledge use bounded feedback loops: call a tool, read the result, and decide the next step. Each request follows one specialist branch.

What I verified in the deployed application:
• SQL and app chat returned the warehouse-verified total of 1,023 tickets.
• Document search answered a product question with a PDF citation.
• ETL transformed 100 API records into the requested id and title columns.
• All four live deployment checks passed; the latest offline run passed 19 tests.

The stack: Python, LangGraph, MLflow ResponsesAgent, Databricks Model Serving, Unity Catalog, Gradio, and Declarative Automation Bundles.

This project connects my data engineering foundation with agent orchestration, tool design, model deployment, authentication, and end-to-end verification. It is a working portfolio deployment; ETL outputs are temporary, and broader answer-quality evaluation is a next step.

I’m looking for AI Engineer / Applied AI Engineer opportunities where I can build on that combination. If your team is hiring, I’d welcome a conversation.

Architecture, screenshots, and a guide to adapting it to your own project:
https://pratik2895.github.io/ai-data-agent/

Source code:
https://github.com/Pratik2895/ai-data-agent

#AIEngineering #DataEngineering #Databricks #LangGraph #OpenToWork
