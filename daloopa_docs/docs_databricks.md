---
title: Databricks
url: https://docs.daloopa.com/docs/databricks
path: /docs/databricks
---

# Databricks

# Databricks

Daloopa's fundamental data is now available natively in your Databricks environment via the Databricks Marketplace. Access our data in your own workspace without building ETL pipelines or managing data movement.

## 

Data Availability

Clients using Databricks have access to three core tables:

  * **Companies** : Company identifiers, metadata, and reference information
  * **Series** : Time-series financial data with period identifiers
  * **Fundamentals** : Core fundamental metrics and financial statement data



## 

Databricks vs. API Coverage

Capability| Databricks| API  
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

  * **Zero Setup Time** : Access data within minutes of provisioning
  * **No ETL Required** : Data appears natively in your Databricks environment
  * **ML/AI Ready** : Direct integration with Databricks ML workflows, notebooks, and feature stores
  * **Seamless Integration** : Join Daloopa data with internal datasets without data movement
  * **Scalable Access** : Multiple teams can query without hitting API rate limits
  * **Enterprise Security** : Native Databricks access controls and Unity Catalog integration



## 

How It Works

Daloopa distributes data via a private listing on the Databricks Marketplace using Delta Sharing. Once access is provisioned, you subscribe to the listing and can access data instantly in your Databricks environment.

## 

Getting Started

### 

1\. Verify Provider Access

SQL
    
    
    -- List all available providers
    SHOW PROVIDERS;
    
    -- View Daloopa provider details
    DESCRIBE PROVIDER daloopa;
    
    -- List available shares
    SHOW SHARES IN PROVIDER daloopa;

### 

2\. Create Catalog and Access Data

SQL
    
    
    -- Create a catalog for Daloopa data
    CREATE CATALOG IF NOT EXISTS daloopa USING SHARE daloopa.daloopa_share;
    
    -- Query the companies table (fully available)
    SELECT * FROM daloopa.shared.companies ORDER BY id ASC;
    
    -- Query restricted tables (only shows data for subscribed companies)
    SELECT * FROM daloopa.shared.series;
    
    SELECT * FROM daloopa.shared.fundamentals WHERE is_incremental_update;

The **companies** table is fully available, allowing you to browse all companies and decide which ones to subscribe to. The **series** and **fundamentals** tables are restricted and only return data for companies you are subscribed to. The **fundamentals** table is further restricted — only users with a Daloopa Plus subscription are able to see fundamentals that are incremental.

### 

3\. Subscribe to Companies

To access data in **series** and **fundamentals** for a specific company, subscribe using the following endpoint with an API key:

**Endpoint:** `POST https://app.daloopa.com/api/v2/databricks/company-subscription`

**Request Body:**

JSON
    
    
    {
      "company_id": <company_id>
    }

__Updated 3 days ago

* * *

[Snowflake](/docs/snowflake)[Coverage](/docs/coverage)

Ask AI

