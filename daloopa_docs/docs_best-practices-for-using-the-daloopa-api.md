---
title: Happy Flows
url: https://docs.daloopa.com/docs/best-practices-for-using-the-daloopa-api
path: /docs/best-practices-for-using-the-daloopa-api
---

# Happy Flows

# Happy Flows

This guide provides step-by-step workflows for common Daloopa API tasks. Each workflow includes complete examples with actual endpoints and parameters.

## 

Quick Start: Choose Your Workflow

Workflow| When to Use| Inputs| Outputs  
---|---|---|---  
Company-First| You know the company ticker/name and want to retrieve specific financial data| Company Ticker or Name| Fundamental Data  
[Taxonomy-First](https://docs.daloopa.com/docs/best-practices-for-using-the-daloopa-api#taxonomy-first-workflow-beta)| You want to compare a specific metric across multiple companies| Standardized Metric| Fundamental Data  
Poll for Updates| You need to monitor companies for earnings updates and retrieve new data| Webhook(s) or Company ID(s)| Fundamental Data  
Export to CSV| You want to bulk export all datapoints for a company| Company Ticker| CSV file with Fundamental Data  
Download Models| You prefer working with Excel models for analysis| Company ID| CSV file with Fundamental Data  
Industry Analysis| You want to compare companies within an industry| None or sub-industry| Fundamental Data  
[Document Search (Beta)](https://docs.daloopa.com/docs/best-practices-for-using-the-daloopa-api#document-search-workflow-beta)| You need to find specific information in SEC filings| Keyword| Snippets from Documents  
  
* * *

## 

Company-First Workflow

**Use this when:** You know the company ticker or name and want to retrieve specific financial metrics.

### 

Step 1: Discover the Company

Search for companies by ticker symbol or name:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/companies?keyword=AAPL' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    [
      {
        "id": 2,
        "name": "Apple Inc.",
        "ticker": "AAPL",
        "industry_": "Technology Hardware, Storage and Peripherals",
        "sector_": "Information Technology",
        "companyidentifier_set": [
          {
            "identifier_type": "CIK",
            "identifier_value": "320193"
          },
          {
            "identifier_type": "CapIQCompanyId",
            "identifier_value": "24937"
          },
          {
            "identifier_type": "CapIQCompanyTicker",
            "identifier_value": "NasdaqGS:AAPL"
          },
          {
            "identifier_type": "CapIQCompanyId",
            "identifier_value": "IQ24937"
          },
          {
            "identifier_type": "ISIN",
            "identifier_value": "I_US0378331005"
          }
        ],
        "model_updated_at": "2026-02-02T12:12:38.482128Z",
        "earliest_quarter": "2012Q4",
        "latest_quarter": "2025Q4"
      }
    ]

**What to capture:**

  * `id`: Company ID (needed for all subsequent requests)
  * `latest_quarter`: Most recent quarter available
  * `latest_datapoint_created_at`: Last update timestamp (for polling)



### 

Step 2: Discover Available Series

Find what financial metrics are available for this company:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/companies/series?company_id=2&keywords=revenue&keywords=sales' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Tips:**

  * Use multiple `keywords` parameters to search for related metrics
  * Common keywords: `revenue`, `net income`, `EPS`, `cash flow`, `gross profit`
  * Results show the exact series names and IDs available



**Response:**

JSON
    
    
    [
        {
          "id": 2467997,
          "full_series_name": "Income Statement | Net sales | Products"
        },
        {
          "id": 2467998,
          "full_series_name": "Income Statement | Net sales | Services"
        },
        {
          "id": 2467999,
          "full_series_name": "Income Statement | Total net sales"
        },
      ]

### 

Step 3: Retrieve Fundamentals

Now fetch the actual financial data:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/companies/fundamentals?company_id=2&periods=2024Q1&periods=2024Q2&series_ids=12345&series_ids=12346' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    {
      "count": 2,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 95541471,
          "label": "Total net sales",
          "category": "Income Statement",
          "restated": false,
          "filing_type": "8-K",
          "series_id": 2467999,
          "title": "Income Statement | Total net sales",
          "value_raw": 90753,
          "value_normalized": 90753,
          "unit": "Million",
          "calendar_period": "2024Q1",
          "fiscal_period": "2024Q2",
          "span": "Quarterly",
          "fiscal_date": "2023-03-30",
          "document_id": 25165413,
          "filing_date": "2024-05-02",
          "document_released_at": "2024-05-02T20:30:34Z",
          "created_at": "2024-05-02T20:33:56.013697Z",
          "updated_at": "2026-02-02T12:12:56.284556Z"
        },
        {
          "id": 102519304,
          "label": "Total net sales",
          "category": "Income Statement",
          "restated": false,
          "filing_type": "8-K",
          "series_id": 2467999,
          "title": "Income Statement | Total net sales",
          "value_raw": 85777,
          "value_normalized": 85777,
          "unit": "Million",
          "calendar_period": "2024Q2",
          "fiscal_period": "2024Q3",
          "span": "Quarterly",
          "fiscal_date": "2024-06-29",
          "document_id": 26052485,
          "filing_date": "2024-08-01",
          "document_released_at": "2024-08-01T20:30:26Z",
          "created_at": "2024-08-01T20:40:09.417865Z",
          "updated_at": "2026-02-02T12:12:56.284616Z"
        }
      ]
    }

**Key fields:**

  * `fundamental_id`: Unique ID for this datapoint (use for source linking: `https://daloopa.com/src/{fundamental_id}`)
  * `value`: The actual financial value
  * `quarterized_value`: Normalized to quarterly basis (useful for comparing Q vs annual data)
  * `period`: Time period in `YYYYQQ` format (e.g., `2024Q1`) or `YYYYFY` for annual (e.g., `2023FY`)
  * `unit`: Scale of the number (billion, million, percent, etc.)



### 

Extra Credit: Check for Deprecated Series IDs

Some series IDs may have been replaced over time. Check for continuations:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/series-continuation?company_id=2' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    [
      {
        "old_series": [
          {
            "id": 303689,
            "full_series_name": "Other Breakdown | Purchases of equity securities by the issuer and affiliated purchasers | Total number of shares purchased | Period 2 | ASR 2",
            "created_at": "2020-10-15T11:42:27.469449Z"
          },
          {
            "id": 303685,
            "full_series_name": "Other Breakdown | Purchases of equity securities by the issuer and affiliated purchasers | Total number of shares purchased | Period 1 | ASR 2",
            "created_at": "2020-10-15T11:42:26.131450Z"
          }
        ],
        "new_series": [
          {
            "id": 3544161,
            "full_series_name": "Other Breakdown | Purchases of equity securities by the issuer and affiliated purchasers | Total number of shares purchased | First month | ASR 2",
            "created_at": "2022-11-07T08:55:26.660085Z"
          },
          {
            "id": 3544162,
            "full_series_name": "Other Breakdown | Purchases of equity securities by the issuer and affiliated purchasers | Total number of shares purchased | Second month | ASR 2",
            "created_at": "2022-11-07T08:55:26.670273Z"
          }
        ],
        "type": "COMPOSITE",
        "created_at": "2022-11-07T08:55:28.392781Z"
      }
    ]

**When to use this:**

  * You're using cached series IDs that may be outdated
  * You get unexpected missing data in your fundamentals response
  * You want to ensure you're always using the latest series structure



* * *

## 

Taxonomy-First Workflow (Beta)

**Use this when:** You want to compare a specific metric (like "Total Revenue") across multiple companies.

### 

Step 1: Search Taxonomy Metrics

Find the standardized metric you want:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/taxonomy/metrics?keyword=total%20revenue' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    {
      "count": 8,
      "next": null,
      "previous": null,
      "results": [
        {
          "metric_id": 1617,
          "metric_name": "Total Revenue",
          "metric_description": "This metric measures the total amount of money a company earns from its business activities before any expenses are deducted, typically over a specific period such as a quarter or year."
        },
      ]
    }

### 

Step 2: Find Companies in Taxonomy

Discover which companies have this metric:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/taxonomy/metrics/501' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    {
      "metric_id": 1617,
      "metric_name": "Total Revenue",
      "metric_description": "This metric measures the total amount of money a company earns from its business activities before any expenses are deducted, typically over a specific period such as a quarter or year.",
      "metric_series": [
        {
           "company_id": 2,
           "ticker": "AAPL",
           "series_id": 2467999,
           "full_series_name": "Income Statement | Total net sales"
         },
        {
          "company_id": 135,
          "ticker": "MSFT",
          "series_id": 2542359,
          "full_series_name": "Income Statement | Total revenue"
        }
      ]
    }

### 

Step 3: Retrieve Fundamentals for All Companies

Use the company IDs to fetch the metric across all companies:

Bash
    
    
    # For Apple
    curl --location 'https://app.daloopa.com/api/v2/companies/fundamentals?company_id=2&periods=2024Q1&periods=2024Q2&series_ids=2467999' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'
    
    # For Microsoft
    curl --location 'https://app.daloopa.com/api/v2/companies/fundamentals?company_id=135&periods=2024Q1&periods=2024Q2&series_ids=2542359' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Pro tip:** You can batch requests by making multiple API calls in parallel to speed up data retrieval.

* * *

## 

Poll for Updates Workflow

**Use this when:** You want to automatically detect when companies release new earnings data and retrieve it.

### 

Approach 1: Webhooks (Recommended)

Webhooks push updates to your server automatically when new data is available.

**How it works:**

  1. Contact Daloopa support to configure webhooks for your companies
  2. Daloopa team adds webhook subscriptions for the companies you care about
  3. When new data is available, Daloopa sends a POST request to your endpoint



**Webhook payload example:**

JSON
    
    
    {
      "event_type": "clientview_updated",
      "company_id": 2,
      "series": {
        "SERIES_ID_1": {
          "periods": [
            "2025Q1"
          ]
        },
        "SERIES_ID_2": {
          "periods": [
            "2025Q1"
          ]
        }
      }
    }

**Your endpoint should:**

  1. Receive the POST request
  2. Validate the payload
  3. Call `/api/v2/companies/fundamentals` to fetch the new data
  4. Return a `200 OK` response



**Testing your webhook endpoint:**

  * Use [ngrok](https://ngrok.com) to expose localhost for testing
  * Use [webhook.site](https://webhook.site) to inspect incoming payloads
  * Test with a company you don't actively monitor



### 

Approach 2: Polling (Alternative)

If webhooks aren't set up yet, you can poll for updates:

Bash
    
    
    curl --location --request POST 'https://app.daloopa.com/api/v2/companies/status' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)' \
    --header 'Content-Type: application/json' \
    --data '{
      "company_ids": [2]
    }'

**Response:**

JSON
    
    
    [
      {
        "company_id": 2,
        "latest_datapoint_created_at": "2026-02-02T11:57:43.113262Z",
        "latest_period": "2025Q4",
        "model_updated_at": "2026-02-02T12:13:55.029076Z"
      }
    ]

**Polling logic:**

  1. Store the last `latest_datapoint_created_at` timestamp for each company
  2. Poll `/api/v2/companies/status` every 15-30 minutes
  3. Compare new `latest_datapoint_created_at` with stored timestamp
  4. If changed, fetch new data with `/api/v2/companies/fundamentals`



**Best practices:**

  * Poll during market hours when earnings are typically released
  * Use exponential backoff if you're polling frequently
  * Consider time zones (most earnings are released 4-5 PM ET)



### 

Comparison: Webhooks vs Polling

Feature| Webhooks| Polling  
---|---|---  
**Latency**|  Instant (< 1 minute)| 5 minutes (depends on poll frequency)  
**Server load**|  Low (only when updates occur)| Higher (constant requests)  
**Setup complexity**|  Requires Daloopa team setup| Self-service via API  
**Best for**|  Production systems, real-time needs| Testing, low-frequency monitoring  
  
* * *

## 

Export to CSV Workflow

**Use this when:** You want to export all datapoints for a company to analyze in Excel or other tools.

### 

Base Export (Historical Data)

Export all historical datapoints:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/export/AAPL' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)' \
    --output aapl_data.csv

**What you get:**

  * CSV format with all datapoints
  * Includes: `id`, `label`, `category`, `span`, `calendar_period`, `fiscal_period`, `value_raw`, `value_normalized`, `unit`, `source_link`, `series_id`
  * Historical data available in the published datasheet



### 

Real-Time Export (Latest Updates)

Export incrementally updated data that hasn't been published to the datasheet yet:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/export/MMM?real_time=true&show_historical_data=false' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)' \
    --output mmm_realtime.csv

**Parameters:**

  * `real_time=true`: Include incrementally updated data (not yet in published datasheet)
  * `show_historical_data=false`: Only return new incremental data (no historical)
  * `show_historical_data=true`: Return both historical + incremental data



**Use case:**

  * `real_time=true&show_historical_data=false`: Get only the latest earnings data before it's published
  * `real_time=true&show_historical_data=true`: Get complete dataset including latest updates



### 

CSV Schema

Column| Description| Example  
---|---|---  
`id`| Unique datapoint ID| 123456789  
`label`| Short description| "Total Revenue"  
`category`| Section in model| "Income Statement"  
`span`| Periodicity| "Quarterly"  
`calendar_period`| Calendar quarter/year| "2024Q2"  
`fiscal_period`| Fiscal quarter/year| "2024Q2"  
`fiscal_date`| End of fiscal period| "2024-06-30"  
`unit`| Scale| "billion"  
`filing_type`| SEC filing type| "10-Q"  
`value_raw`| Raw value| 90.753  
`value_normalized`| Normalized value| 90.753  
`source_link`| Link to source| "<https://daloopa.com/src/123456789>"  
`series_id`| Series identifier| 12345  
`filing_date`| Filing date| "2024-05-03"  
`restated`| Was restated?| false  
`title`| Full hierarchy| "Revenue | Total Revenue"  
`created_at`| Creation timestamp| "2024-05-03T14:30:00Z"  
`updated_at`| Last update| "2024-05-03T14:30:00Z"  
`document_released_at`| Document ingestion time| "2024-05-03T15:00:00Z"  
  
* * *

## 

Download Excel Model Workflow

**Use this when:** You want to download the full Excel model for offline analysis.

### 

Step 1: Request Download URL

Get a pre-signed URL to download the model:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/download-company-model?company_id=2&model_type=company' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    {
      "download_url": "https://daloopa-excel-model.s3.amazonaws.com/1031277.xlsx?AWSAccessKeyId=AKIAYH2MSS6UCWRAXJ23&Signature=XtKT7JwJYKSXOp3NPBl5tJWSRAw%3D&Expires=1770152604"
    }

### 

Step 2: Download the Model

Use the pre-signed URL to download:

Bash
    
    
    curl --location 'https://daloopa-models.s3.amazonaws.com/models/AAPL_model.xlsx?AWSAccessKeyId=...' \
    --output AAPL_model.xlsx

**Important:**

  * URLs expire after 1 hour
  * Download must complete before expiration
  * Models are full Excel files with all sheets and formulas



### 

What's in the Model?

  * **Historical data** : All quarters/years in the datasheet
  * **Line items** : Full detail for Income Statement, Balance Sheet, Cash Flow
  * **KPIs** : Company-specific metrics
  * **Guidance** : Management guidance when available
  * **Charts** : Pre-built visualizations



* * *

## 

Industry Model Workflow

**Use this when:** You want to compare companies within the same industry using standardized metrics.

### 

Step 1: List Sub-Industries

Find available sub-industries:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/taxonomy/sub-industries' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    {
      "count": 220,
      "next": "http://app.daloopa.com/api/v2/taxonomy/sub-industries?limit=100&offset=100",
      "previous": null,
      "results": [
        {
          "sub_industry_id": 281,
          "sub_industry_name": "Cruise Lines",
          "industry_name": "Restaurants, Hotels & Leisure",
          "sub_sector_name": "Consumer Services",
          "sector_name": "Consumer Discretionary",
          "companies": [
            {
              "id": 312,
              "ticker": "CCL",
              "name": "Carnival Corp"
            },
            {
              "id": 508,
              "ticker": "NCLH",
              "name": "Norwegian Cruise Line Holdings Ltd."
            },
            {
              "id": 555,
              "ticker": "RCL",
              "name": "Royal Caribbean Cruises Ltd"
            }
          ]
    	   }
      ]
    }

### 

Step 2: Search Taxonomy Metrics

Find the standardized metric(s) you want using the sub_industry_id:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/taxonomy/metrics?sub_industry_id=281' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    {
      "count": 69,
      "next": null,
      "previous": null,
      "results": [
        {
          "metric_id": 1558,
          "metric_name": "Passenger Revenue",
          "metric_description": "Total revenue generated from transporting passengers, excluding ancillary (e.g., fees, onboard add-ons) and cargo/freight revenues. Includes passenger ticket sales and related passenger-service revenues across passenger transportation operators (e.g., airlines, cruise lines)."
        },
        {
          "metric_id": 1560,
          "metric_name": "Operating Income",
          "metric_description": "Operating Income (Loss) represents the profit or loss a company generates from its core operating activities before non-operating items (e.g., interest and other financing costs/income) and income taxes. It is generally calculated as revenue (or net sales) minus operating costs and expenses (e.g., cost of goods/services, selling/general/administrative, R&D, depreciation and amortization, and other operating items), and may be presented as EBIT when interest is excluded by definition."
        },
     ]
    }

### 

Step 3: Retrieve Company Series IDs for All Companies

Use the company IDs to fetch the metric across all companies:

Bash
    
    
    # For Passenger Revenue
    curl --request GET \
         --url 'https://app.daloopa.com/api/v2/taxonomy/metrics/1558?sub_industry_id=281' \
         --header 'Authorization: Basic YXBpLW1hcml6dUBwb2ludDcyLmNvbTp4cU84RFdNaFM5dkdzeWZ3SXI1cGVHMGFudUNXcGVMbThRelFzV1FYQW5WRnI3cjFHWHlEYUE=' \
         --header 'accept: application/json'
    
    # For Operating Income
    curl --request GET \
         --url 'https://app.daloopa.com/api/v2/taxonomy/metrics/1560?sub_industry_id=281' \
         --header 'Authorization: Basic YXBpLW1hcml6dUBwb2ludDcyLmNvbTp4cU84RFdNaFM5dkdzeWZ3SXI1cGVHMGFudUNXcGVMbThRelFzV1FYQW5WRnI3cjFHWHlEYUE=' \
         --header 'accept: application/json'

**Response:**

JSON
    
    
    {
      "count": 69,
      "next": null,
      "previous": null,
      "results": [
        {
          "metric_id": 1558,
          "metric_name": "Passenger Revenue",
          "metric_description": "Total revenue generated from transporting passengers, excluding ancillary (e.g., fees, onboard add-ons) and cargo/freight revenues. Includes passenger ticket sales and related passenger-service revenues across passenger transportation operators (e.g., airlines, cruise lines)."
        },
        {
          "metric_id": 1560,
          "metric_name": "Operating Income",
          "metric_description": "Operating Income (Loss) represents the profit or loss a company generates from its core operating activities before non-operating items (e.g., interest and other financing costs/income) and income taxes. It is generally calculated as revenue (or net sales) minus operating costs and expenses (e.g., cost of goods/services, selling/general/administrative, R&D, depreciation and amortization, and other operating items), and may be presented as EBIT when interest is excluded by definition."
        },
     ]
    }

### 

Step 4: Retrieve Fundamentals for All Companies

Use the company IDs to fetch the metric across all companies:

Bash
    
    
    # For CCL
    curl --location 'https://app.daloopa.com/api/v2/companies/fundamentals?company_id=312&periods=2024Q1&periods=2024Q2&series_ids=2729066&series_ids=2729081' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'
    
    # For NCLH
    curl --location 'https://app.daloopa.com/api/v2/companies/fundamentals?company_id=508&periods=2024Q1&periods=2024Q2&series_ids=1866377&series_ids=1866391' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'
    
    # For RCL
    curl --location 'https://app.daloopa.com/api/v2/companies/fundamentals?company_id=555&periods=2024Q1&periods=2024Q2&series_ids=2865083&series_ids=2865097' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Pro tip:** You can batch requests by making multiple API calls in parallel to speed up data retrieval.

* * *

## 

Document Search Workflow (Beta)

**Use this when:** You need to find specific information in SEC filings (10-K, 10-Q, 8-K, earnings calls).

### 

Pattern 1: Keyword Search (Beta)

Search for keywords across all document types:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/documents/search?keyword=cybersecurity' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    {
      "success": true,
      "total_hits": 11,
      "documents": [
        {
          "document_id": "23465209",
          "company_id": 2,
          "filing_type": "PRIVATE",
          "affinitized_date": "2022-12-31",
          "document_title": "c3f1ec093cb388c4282baebcce982bf2",
          "score": 0.9860914,
          "matches": [
            {
              "keyword": "guidance",
              "indexed_position": "24187-24195",
              "context": "[...] ncertainty around the world in the near term, we are not providing revenue guidance, but we are sharing some directional insights based on the assumption that [...]",
              "match_id": "eyJkb2N1bWVudF9pZCI6ICIyMzQ2NTIwOSIsICJlbmQiOiAyNDE5NSwgImtleXdvcmQiOiAiZ3VpZGFuY2UiLCAic3RhcnQiOiAyNDE4N30="
            },
          ]
        }
      ],
      "offset": 0,
      "limit": 10
    }

### 

Pattern 2: Company-Specific Document Lookup

Find documents for a specific company:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/companies/2/documents?filing_type=10-Q&fiscal_period=2024Q2' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    {
      "company_id": 2,
      "ticker": "AAPL",
      "documents": [
        {
          "document_id": 789012,
          "filing_type": "10-Q",
          "fiscal_period": "2024Q2",
          "filing_date": "2024-05-03",
          "url": "https://daloopa.com/documents/789012"
        }
      ]
    }

### 

Pattern 3: Retrieve Full Document

Get the complete document content:

Bash
    
    
    curl --location 'https://app.daloopa.com/api/v2/documents/789012' \
    --header 'Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)'

**Response:**

JSON
    
    
    {
      "document_id": 789012,
      "company_id": 2,
      "ticker": "AAPL",
      "filing_type": "10-Q",
      "fiscal_period": "2024Q2",
      "filing_date": "2024-05-03",
      "content": "Full document text...",
      "source_url": "https://www.sec.gov/..."
    }

**Search tips:**

  * Use specific keywords for better results
  * Filter by `filing_type` to narrow search (10-K, 10-Q, 8-K)
  * Combine with `fiscal_period` to find specific quarterly/annual disclosures
  * Use `match_count` to prioritize documents with more mentions

  


__Updated 7 days ago

* * *

[Best Practices](/docs/best-practices)[Webhook Integration](/docs/webhook)

Ask AI

