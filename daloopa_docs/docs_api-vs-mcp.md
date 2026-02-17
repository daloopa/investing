---
title: API vs. MCP
url: https://docs.daloopa.com/docs/api-vs-mcp
path: /docs/api-vs-mcp
---

# API vs. MCP

# API vs. MCP

# 

Choosing Between API and MCP Integration

Daloopa offers two programmatic ways to access financial data: the API and MCP (Model Context Protocol) server. Each approach has distinct strengths and ideal use cases.

## 

Use the API When:

✅ **Building production data pipelines**

  * Automated ETL processes
  * Scheduled data refreshes
  * Batch processing workflows



✅ **You need deterministic, repeatable queries**

  * Specific endpoints with known parameters
  * Consistent data structures
  * Full control over requests



✅ **Performance and cost optimization are critical**

  * Direct API calls are faster
  * No LLM token costs
  * Predictable pricing



**Best for:** Software engineers, data engineers, backend systems, automated workflows

* * *

## 

Use MCP Integration When:

✅ **Working with LLMs and AI assistants (Claude, ChatGPT)**

  * Ad-hoc analysis and exploration
  * Natural language queries
  * Conversational data access



✅ **Rapid prototyping and analysis**

  * Quick questions without writing code
  * Exploring data interactively
  * Generating insights on the fly



✅ **Non-technical users need data access**

  * Analysts without coding experience
  * Business users asking financial questions
  * Executive dashboards with AI assistants



**Best for:** Software engineers, analysts, researchers, exploratory analysis

* * *

## 

Comparison Table

Feature| API| MCP  
---|---|---  
**Query Method**|  Structured HTTP requests| Natural language  
**Speed**|  Faster (direct)| Depends on LLM  
**Cost**|  API calls only| API + LLM tokens  
**Flexibility**|  High (programmatic)| Very high (conversational)  
**Learning Curve**|  Steeper (requires coding)| Easier (plain English)  
**Use Case**|  Production systems| Analysis & exploration  
  
* * *

## 

Available Tools & Endpoints

MCP tools are built on top of API endpoints. Here's how they map:

MCP Tool| API Endpoints| What It Does  
---|---|---  
**discover_companies**| `GET /api/v2/companies`| Search companies by ticker or name. Returns company_id, ticker, name, latest_quarter  
**discover_company_series**| `GET /api/v2/companies/series`| Find available metrics for a company. Filter by keywords (e.g., "revenue", "EBITDA"). Returns series_id and full_series_name  
**get_company_fundamentals**| `GET /api/v2/companies/fundamentals`| Retrieve financial data for specific series and periods. Supports quarterly (2024Q1) and annual (2024FY) formats. Returns values with source citations and hyperlinks  
**search_documents** (Beta)| `POST /api/v2/documents/keyword-search`| Keyword search across SEC filings (10-K, 10-Q, 8-K). Search by keywords, company, and periods. Returns document matches with context snippets  
  
### 

Additional API Capabilities

The API offers many more endpoints beyond what's available through MCP:

**Company & Series Discovery:**

  * Check Company Model Status - View update status and latest data timestamps
  * List Taxonomy Metrics - Find standardized metrics across companies
  * Get Series Continuation - Handle deprecated/updated series IDs



**Fundamental Data:**

  * Export Company Data (CSV) - Bulk export of all company data
  * Get Fundamental Updates - Track data corrections and changes



**Models & Documents:**

  * Download Company Model (Excel) - Get full Excel model
  * Download Industry Model (Excel) - Get industry comparison models
  * Company Document Lookup (Beta) - Find financial filings and documents
  * Retrieve Document (Beta) - Access specific document content



**Company Management:**

  * Get Company Industry Model Mappings - View industry classifications
  * Add/Remove Company Subscriptions - Manage tracked companies



**Webhooks:**

  * Real-time event notifications for data updates



* * *

## 

Can I Use Both?

**Yes!** Many teams use or test both approaches:

  * **MCP for exploration** : Analysts explore data and identify insights
  * **API for production** : Convert proven queries into automated pipelines
  * **Hybrid workflows** : Use MCP to discover series IDs, then API for bulk retrieval



* * *

## 

Getting Started

  * **API** : See [API Authentication](/docs/api-authentication) and [Best Practices](/docs/best-practices-for-using-the-daloopa-api)
  * **MCP** : See [Using Daloopa's MCP Server](/docs/daloopa-mcp)

  


__Updated 9 days ago

* * *

[Single Sign-On](/docs/single-sign-on)[Docs MCP Server](/docs/mcp)

Ask AI

