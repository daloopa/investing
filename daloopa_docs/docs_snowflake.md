---
title: Snowflake
url: https://docs.daloopa.com/docs/snowflake
path: /docs/snowflake
---

# Snowflake

# Snowflake

Daloopa's fundamental data is now available natively in your Snowflake environment via the Snowflake Marketplace. Access our data in your own workspace without building ETL pipelines or managing data movement.

## 

Data Availability

Clients using Snowflake have access to three core tables:

  * **Companies** : Company identifiers, metadata, and reference information
  * **Series** : Time-series financial data with period identifiers
  * **Fundamentals** : Core fundamental metrics and financial statement data



## 

Snowflake vs. API Coverage

Capability| Snowflake| API  
---|---|---  
Companies| ✓| ✓  
Series| ✓| ✓  
Fundamentals| ✓| ✓  
Download (company model)| —| ✓  
Export (CSV with series and datapoints)| —| ✓  
Industry Models| —| ✓  
Taxonomy (standardized metrics mapping)| —| ✓  
Documents (download and keyword search)| —| ✓  
  
**Future Data:** Additional data sources, including our taxonomy table and potentially documents, will be added in future releases.

**Important Details:** Columns and fields for each table mirror our API responses with minor differences — clients familiar with our API will recognize the same structure.

## 

Key Benefits

  * **Zero Setup Time** : Access data within 15 minutes of provisioning via the marketplace
  * **No ETL Required** : Data appears natively in your Snowflake account
  * **Seamless Integration** : Join Daloopa data with internal datasets without data movement
  * **Scalable Access** : Multiple teams can query without hitting API rate limits
  * **Instant Updates** : Data refreshes reflect immediately in your environment
  * **Enterprise Security** : Native Snowflake role-based access control



## 

How It Works

Daloopa distributes data via a private listing on the Snowflake Marketplace. Once access is provisioned, you subscribe to the listing and can access data instantly in your Snowflake environment.

## 

Getting Started

### 

1\. Create Database from Listing

Install the Daloopa listing from the Snowflake Marketplace and create a database from it.

### 

2\. Access Data

SQL
    
    
    -- Query the companies table (fully available)
    SELECT * FROM <database_name>.SHARED.COMPANIES ORDER BY ID ASC;
    
    -- Query restricted tables (only shows data for subscribed companies)
    SELECT * FROM <database_name>.SHARED.SERIES;
    
    SELECT * FROM <database_name>.SHARED.FUNDAMENTALS WHERE IS_INCREMENTAL_UPDATE;

The **COMPANIES** table is fully available, allowing you to browse all companies and decide which ones to subscribe to. The **SERIES** and **FUNDAMENTALS** tables are restricted and only return data for companies you are subscribed to. The **FUNDAMENTALS** table is further restricted — only users with a Daloopa Plus subscription are able to see fundamentals that are incremental.

### 

3\. Subscribe to Companies

To access data in SERIES and FUNDAMENTALS for a specific company, subscribe using the following endpoint with an API key:

**Endpoint:** `POST https://app.daloopa.com/api/v2/snowflake/company-subscription`

**Request Body:**

JSON
    
    
    {
      "company_id": <company_id>
    }

  


__Updated 3 days ago

* * *

[Privacy and Data Collection Disclosure for MCP Access](/docs/daloopa-privacy-and-data-collection-disclosure-for-mcp-access)[Databricks](/docs/databricks)

Ask AI

