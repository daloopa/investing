---
title: Webhook Integration
url: https://docs.daloopa.com/docs/webhook
path: /docs/webhook
---

# Webhook Integration

# Webhook Integration

## 

Overview

Daloopa webhooks provide real-time notifications when company data is updated.

### 

How Webhook Setup Works

Webhooks are configured by your Daloopa account team. To get started:

  1. **Provide your endpoint details** to your Daloopa representative:

     * **Webhook URL** : Your HTTPS endpoint that will receive events
     * **Authentication method** : Header name and secret token for verification
     * **Companies of interest** : Which companies you want to monitor
  2. **Daloopa configures the webhook** for your specified companies

  3. **Verify receipt** : Test that your endpoint receives and processes webhook events




### 

What You Need to Provide

When requesting webhook setup, share these details with your Daloopa team:

Field| Description| Example  
---|---|---  
**url**|  Your webhook endpoint (must be HTTPS)| `https://your-domain.com/webhooks/daloopa`  
**header_name**|  Authentication header name| `Authorization` or `X-API-Key`  
**auth_secret**|  Your secret token for webhook verification| `your_secret_token`  
**prefix** (optional)| Prefix for the auth header value| `Bearer` or `X-API-KEY`  
**companies**|  Company IDs or tickers to monitor| `AAPL, MSFT, GOOGL`  
  
### 

Initial Live Testing

Currently, the best way to test webhooks is to:

  1. Subscribe to a test company (a company you're monitoring but don't need immediate updates for)
  2. Wait for that company's next data update event
  3. Verify your endpoint receives and processes the webhook correctly



Note: Daloopa is developing improved testing capabilities in the future.

### 

Monitoring Webhook Delivery

After your first webhook arrives:

  * Log all received events for debugging
  * Monitor for HTTP 200 responses from your endpoint
  * Check that authentication is working correctly



### 

Event Types

Currently, we support the following events:

  * `clientview_updated` \- Triggered when a new ClientView model is generated for the company
  * `incremental_update` \- Triggered over any new group of datapoints published, either by analyst or autotagger
  * `series_updated` \- Triggered when fundamental data errors/changes are detected in the last 5 minutes



For all events, the webhook payload includes relevant data about the updates, with the specific structure varying by event type.

### 

Request Format

When a webhook event is triggered, our system will send an HTTP POST request to your specified URL with the following:

### 

Headers
    
    
    Content-Type: application/json
    {header_name}: {prefix} {auth_secret}

**Example**

  * url: <https://yoururl.com>
  * header_name: Authorization
  * prefix: X-API-KEY
  * auth_secret: secret_api_key



Webhook triggers a POST request to <https://yoururl.com> with the following headers:
    
    
    Content-Type: application/json
    Authorization: X-API-KEY secret_api_key

### 

Body

#### 

Clientview Updated

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

#### 

Incremental Update

JSON
    
    
    {
      "event_type": "incremental_update",
      "company_id": 2,
      "series": {
        "SERIES_ID_3": {
          "periods": [
            "2025Q1"
          ]
        },
        "SERIES_ID_4": {
          "periods": [
            "2025Q1"
          ]
        }
      }
    }

#### 

Series Updated

JSON
    
    
    {
      "event_type": "series_updated",
      "company_id": 2,
      "series": [
        {
          "id": 2,
          "type": "MERGING_ERROR",
          "period": "2024Q1",
          "run_date": "2024-06-02T12:00:00Z",
          "details": {
            "fundamental_id": 13,
            "series_id": 102,
            "field_changed": "series_id",
            "new_value": 102,
            "old_value": 103
          }
        },
        {
          "id": 3,
          "type": "TAGGING_ERROR",
          "period": "2024Q1",
          "run_date": "2024-06-03T12:00:00Z",
          "details": {
            "fundamental_id": 13,
            "series_id": 202,
            "field_changed": "fundamental_id",
            "new_value": 13,
            "old_value": 12
          }
        },
        {
          "id": 4,
          "type": "VALUE_ERROR",
          "period": "2024Q2",
          "run_date": "2024-06-04T12:00:00Z",
          "details": {
            "fundamental_id": 15,
            "series_id": 105,
            "field_changed": "fundamental_value",
            "new_value": 1500,
            "old_value": 1200
          }
        }
      ]
    }

**Series Updated Event Details:**

The `series_updated` webhook is triggered every 5 minutes when fundamental data errors or corrections are detected. It includes:

  * **Supported Error Types** : `VALUE_ERROR`, `TAGGING_ERROR`, `MERGING_ERROR`
  * **Frequency** : Triggered every 5 minutes for companies with recent errors
  * **Payload Structure** : Contains an array of error objects with detailed information about what changed
  * **Details Object** : Includes the fundamental_id, series_id, field that changed, and both old and new values



This webhook provides granular notifications about data corrections, merges, tagging changes, and other meaningful updates to help you track data quality changes in real-time.

## 

Interpreting the Results

The `details` object contains different information depending on the error type. Here's how to interpret each field:

### 

VALUE_ERROR

**Meaning:** Fundamental with id `fundamental_id` changed value from `old_value` to `new_value`

**Example:** Fundamental 45672 changed value from 1,200,000 to 1,500,000

  * `fundamental_id`: The ID of the fundamental datapoint that was corrected
  * `series_id`: The series/row where this fundamental belongs
  * `field_changed`: Always "fundamental_value" for value corrections
  * `old_value`: The previous (incorrect) value
  * `new_value`: The corrected value



### 

TAGGING_ERROR

**Meaning:** Series with id `series_id` removed Fundamental with id `old_value` and received a new Fundamental with id `new_value`

**Example:** Series 12346 removed Fundamental 45670 and received new Fundamental 45673

  * `fundamental_id`: The current fundamental ID after the change
  * `series_id`: The series/row that was affected by the retagging
  * `field_changed`: Always "fundamental_id" for tagging changes
  * `old_value`: The ID of the fundamental that was removed from this series
  * `new_value`: The ID of the fundamental that was assigned to this series



### 

MERGING_ERROR

**Meaning:** Fundamental with id `fundamental_id` changed series/row from `old_value` to `new_value`

**Example:** Fundamental 45674 moved from series 12340 to series 12347

  * `fundamental_id`: The ID of the fundamental that was moved
  * `series_id`: The current series/row after the merge
  * `field_changed`: Always "series_id" for merging operations
  * `old_value`: The previous series ID before merging
  * `new_value`: The new series ID after merging



## 

Need Help?

If you encounter any issues with webhook configuration or delivery, please contact your Sales Representative

 __Updated 9 days ago

* * *

[Happy Flows](/docs/best-practices-for-using-the-daloopa-api)[Tag ID Preview](/docs/tag-id-preview)

Ask AI

