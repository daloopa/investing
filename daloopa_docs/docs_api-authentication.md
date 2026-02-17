---
title: Authentication
url: https://docs.daloopa.com/docs/api-authentication
path: /docs/api-authentication
---

# Authentication

# Authentication

## 

Obtaining Your API Key

To access the API, you need an API key. Please contact our sales team to obtain your key.

## 

Authentication Type

The API uses Basic Authentication for secure access.

### 

Authentication Format

To authenticate, include the `Authorization` header in every API request. The header should contain a Base64-encoded string of your email address and API key.

**Format:**
    
    
    Authorization: Basic BASE64_ENCODED_CREDENTIALS

Where `BASE64_ENCODED_CREDENTIALS` is the Base64 encoding of:
    
    
    YOUR_EMAIL:YOUR_API_KEY

### 

How to Generate Your Credentials

  1. Combine your email and API key with a colon separator: `YOUR_EMAIL:YOUR_API_KEY`
  2. Encode the combined string using Base64



### 

Example

If your email is `[[email protected]](/cdn-cgi/l/email-protection)` and your API key is `abc123`:

  1. Combine them: `[[email protected]](/cdn-cgi/l/email-protection):abc123`
  2. Base64 encode: `dXNlckBleGFtcGxlLmNvbTphYmMxMjM=`
  3. Add the header:
         
         Authorization: Basic dXNlckBleGFtcGxlLmNvbTphYmMxMjM=




### 

Code Examples

#### 

cURL

Bash
    
    
    curl -X GET "https://app.daloopa.com/api/v2/companies" \
      -H "Authorization: Basic $(echo -n '[[email protected]](/cdn-cgi/l/email-protection):abc123' | base64)"

#### 

Python

Python
    
    
    import base64
    import requests
    
    email = "[[email protected]](/cdn-cgi/l/email-protection)"
    api_key = "abc123"
    
    credentials = base64.b64encode(f"{email}:{api_key}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {credentials}"
    }
    
    response = requests.get("https://app.daloopa.com/api/v2/companies", headers=headers)

#### 

JavaScript (Node.js)

JavaScript
    
    
    const email = "[[email protected]](/cdn-cgi/l/email-protection)";
    const apiKey = "abc123";
    
    const credentials = Buffer.from(`${email}:${apiKey}`).toString("base64");
    
    const response = await fetch("https://app.daloopa.com/api/v2/companies", {
      headers: {
        "Authorization": `Basic ${credentials}`
      }
    });

__Updated 9 days ago

* * *

[Docs MCP Server](/docs/mcp)[Best Practices](/docs/best-practices)

Ask AI

