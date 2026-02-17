---
title: Best Practices
url: https://docs.daloopa.com/docs/best-practices
path: /docs/best-practices
---

# Best Practices

# Best Practices

Best practices when using Daloopa's API

  


### 

Period Format Standards

Always use these formats for periods:

Format| Description| Example  
---|---|---  
`YYYYQQ`| Quarterly data| `2024Q1`, `2024Q2`  
`YYYYHH`| Semi-Annual data| `2024H1`, `2024H2`  
`YYYYFY`| Fiscal year (annual)| `2023FY`, `2024FY`  
  
### 

Rate Limits

  * 120 requests per minute
  * Batch requests when possible to reduce call volume



### 

Caching Strategy

To minimize API calls:

  1. **Cache company IDs** : Store `company_id` mappings locally (they don't change)
  2. **Cache series IDs** : Store series structure, refresh weekly
  3. **Cache fundamentals** : Store datapoint values, only refresh after `latest_datapoint_created_at` changes
  4. **Cache documents** : Full documents rarely change, cache for 30+ days



### 

Authentication

All API requests require Basic Auth:

Bash
    
    
    # Format: base64(email:api_key)
    Authorization: Basic YOUR_ENCODED_API_KEY

 __Updated 7 days ago

* * *

[Authentication](/docs/api-authentication)[Happy Flows](/docs/best-practices-for-using-the-daloopa-api)

Ask AI

