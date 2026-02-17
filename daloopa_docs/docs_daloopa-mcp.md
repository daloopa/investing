---
title: How to Use
url: https://docs.daloopa.com/docs/daloopa-mcp
path: /docs/daloopa-mcp
---

# How to Use

# How to Use

Get started with the Daloopa's MCP server

## 

Introduction

### 

What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open standard that creates a unified way for large language models to connect with external applications and data sources. Rather than having each AI system use different methods to access tools and information, MCP establishes a common framework for these interactions. This protocol enables bidirectional communication, allowing AI models not only to retrieve data from various sources but also to perform actions within connected applications. Essentially, MCP serves as a standardized interface that streamlines how AI agents work with external resources and tools.

### 

Daloopa's MCP

Daloopa’s MCP allows our best-in-class data to be flexibly and securely accessed by LLMs, for use in various AI applications. Our MCP enables LLMs to communicate effectively with our database and gives systematic instructions to our client’s LLM on how to query and pull our data into their systems. This means that LLM’s can efficiently digest Daloopa’s vast and deep fundamental database, without overloading their system, saving our clients significant time and resources. AI agents won’t spend time generating inaccurate data, and can focus on generating actionable insights instead.

### 

Highlights

  * Remote MCP using [Streamable HTTP Protocol](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http) with a URL that integrates into your LLM
  * Compatible with all LLMs that follow MCP Standard Protocol (Claude and OpenAI LLM APIs)
  * Source location mapped to every output derived from a Daloopa datapoint.
  * Three tools that enable your AI agent to:
    * Find all companies covered by Daloopa;
    * Search for specific series, metrics and line items for target companies;
    * Fetch values of identified series.



### 

Server

Remote Daloopa's MCP Server URL: <https://mcp.daloopa.com/server/mcp>

To integrate the Daloopa MCP server with compatible applications, configure your MCP client using the provided server URL. This remote server connection enables direct access to Daloopa's comprehensive financial database through the standardized MCP protocol.

## 

Available Tools

**discover_companies:** Locates companies within the Daloopa financial database by searching with either stock ticker symbols or company names. This function returns essential company information including the ticker symbol, complete corporate name, and unique company identifier required for accessing detailed financial data.

**discover_company_series:** Retrieves the complete catalog of available financial metrics and data series for a specified company. Using the company's unique identifier and relevant search terms, this tool displays all accessible financial series along with their corresponding metric IDs, enabling targeted data extraction to streamline the data processing.

**get_fundamentals_data:** Extracts comprehensive financial fundamentals for a company across selected time periods and specific metrics. This function delivers detailed financial information and values spanning Income Statements, Balance Sheets, Cash Flow Statements, and additional financial metrics, allowing for thorough financial analysis and trend evaluation.

**search_documents (beta):** Searches financial filings, transcripts and company presentations using keyword matching to extract qualitative insights across selected time periods. This function delivers contextual information spanning management commentary, forward guidance, risk factors, strategic initiatives, and other disclosures from 10-K, 10-Q, and 8-K filings, earnings transcripts and company presentations, allowing for comprehensive qualitative analysis alongside numerical fundamentals.

## 

Authentication

### 

OAuth

The Daloopa MCP server implements [MCP OAuth Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization). When configuring the server connection, users will be redirected to a Daloopa authentication page where they can enter their username and password credentials.

![](https://files.readme.io/2ce088d18c74508222588111775a94746deffc17cfcdabe3d0ed2fb85850f53e-Screenshot_2025-12-05_at_2.16.33_PM.png)

MCP OAuth Login Page

Upon successful authentication, the system generates a bearer token that must be included in the request headers for all subsequent tool calls and redirects to the provided redirect URL. This OAuth flow ensures secure access to financial data while maintaining compliance with MCP authorization standards.

For more details on the OAuth flow to Authenticate at Daloopa MCP, please check [Daloopa OAuth API](https://mcp.daloopa.com/redoc#tag/Auth)

### 

API Key and Bearer Token

For users who possess a Daloopa API Key, an alternative authentication method is available through direct token generation. By making a POST request to [Generate Token](https://mcp.daloopa.com/redoc#tag/Auth/operation/api_key_token_auth_token_post) with their existing API Key, users can obtain a bearer token without going through the OAuth flow.

These generated tokens remain valid for 24 hours, after which a new token must be requested.

### 

Direct API Key Authentication (Header-Based)

For customers who prefer a simpler authentication mechanism, Daloopa also supports **direct API key authentication** via request headers.

Instead of generating a bearer token or using the OAuth flow, customers can include their API key directly in each request using the `X-API-KEY` header.

**How it works:**

  * The API key is sent with every request.
  * No token generation or refresh is required.



## 

Integrations

### 

OpenAI LLM API

To integrate the Daloopa MCP server with OpenAI LLM API, you'll need both an [OpenAI API Key](https://platform.openai.com/api-keys) and a Daloopa Bearer Token. The Daloopa token can be obtained through either the OAuth authentication flow or by generating one using your existing Daloopa API key.

This integration allows OpenAI LLM to access Daloopa's financial database through the standardized MCP protocol.

Example using Python:

Python
    
    
    from openai import OpenAI
    
    # Your Open AI APIKey
    OPEN_AI_APIKEY = ""
    
    # Daloopa Generated MCP Token
    DALOOPA_MCP_TOKEN = ""
    
    client = OpenAI(api_key=OPEN_AI_APIKEY)
    
    response = client.responses.create(
      model="gpt-5.1",
      input=[],
      text={
        "format": {
          "type": "text"
        }
      },
      reasoning={},
      tools=[
        {
          "type": "mcp",
          "server_label": "Daloopa",
          "server_url": "https://mcp.daloopa.com/server/mcp",
          "headers": {
            "Authorization": f"Bearer {DALOOPA_MCP_TOKEN}"
          },
          "allowed_tools": [
            "discover_companies",
            "discover_company_series",
            "get_company_fundamentals"
          ],
          "require_approval": "never"
        }
      ],
      temperature=1,
      max_output_tokens=2048,
      top_p=1,
      store=True
    )

### 

Claude

**Step 1: Manage Connectors**

Go to <https://claude.ai/settings/connectors> and click on "Organization connectors" on the top right to manage your **Claude Connectors**.

If you are part of an organization, you may need your administrators to set up the connector before you can use it.

![](https://files.readme.io/878987f38c256f732bb2b5d479d0ec52005695b7f8b8dac83c94006ee7287197-image.png)

**Step 2: Add Daloopa**

Click on "Browse connectors", scroll to Daloopa's connector and click on it.

![](https://files.readme.io/3c0ca401d859abf1f042ce604d749407161f51832f68869f8df480e85de89141-Screenshot_2025-10-23_at_1.14.43_PM.png)

**Step 3: Connect Daloopa MCP**

Click **Connect** in MCP details view.

![](https://files.readme.io/d4768aa8c3e5ba6f24df2a0c88dafd6ed0958adfba161c125d6fe1d4b17590c2-Screenshot_2025-10-23_at_1.14.32_PM.png)

**Step 4: Login at Daloopa**

When connecting to the Daloopa MCP server, Claude will automatically redirect you to the [Daloopa MCP Login Page](https://docs.daloopa.com/docs/daloopa-mcp#oauth). Simply enter your registered Daloopa email address and password on this authentication page. Upon successful login verification, you'll be redirected back to Claude with full authentication established for the Daloopa MCP connection.

![](https://files.readme.io/d7a84a7fb67656c63bc67a44983419c6928babc64012a503699f88b74f60315b-Screenshot_2025-12-05_at_2.16.33_PM.png)

**Step 5: Verify Enabled Tools**

Back to Claude, you can verify if all Daloopa MCP tools are correctly available.

![](https://files.readme.io/eec004c736d8e0592f3d2639aec9f8fba47ef370de468ce5bf32e8c69c72d28d-image.png)

You are ready to use Daloopa MCP with Claude!

### 

ChatGPT

**Step 1: Go to your Settings → Apps & Connectors:**

Go to [https://chatgpt.com/#settings](https://chatgpt.com/admin/ca)

![](https://files.readme.io/6772b554de1e68b49ebd577cc18adf41cbc430ff02a0a6cd5692e0d231d98142-Screenshot_2025-12-05_at_2.16.08_PM.png)

**Step 2: Add Daloopa:**

Click **Daloopa** under Browse apps.

![](https://files.readme.io/f00ec88c3990705243a0c0ec7c9a5c676fa75d468193a699e80fcac973470cb0-Screenshot_2025-12-05_at_2.16.18_PM.png)

**Step 3: Login to Daloopa**

ChatGPT will automatically redirect you to the [Daloopa MCP Login Page](https://docs.daloopa.com/docs/daloopa-mcp#oauth). Simply enter your registered Daloopa email address and password on this authentication page.

![](https://files.readme.io/7389a317439bd865c749e79d348238d2f75124af3d02078635203667f6334000-Screenshot_2025-12-05_at_2.16.33_PM.png)   


**Step 4: Add Daloopa to the Chat**

Go to a new chat, click the **Add** icon, go to the More menu and click **Daloopa**

![](https://files.readme.io/9e8bb0f5cee3de3398a10cc5070302c2d52989fa180d01957ba829340988349b-Screenshot_2025-12-05_at_2.17.00_PM.png)

You are ready to use the Daloopa Connector with ChatGPT!

**Here are some callouts that might be helpful when using the Daloopa Connector in ChatGPT:**

  * GPT-5-Thinking produces more thoughtful answers than GPT-5-Instant but will take longer. Choose wisely.
  * A more comprehensive and explicit prompt is better than a vague and implicit prompt.



### 

Feedback and Support

If you have any feedback, suggestions or questions, please [contact us](https://docs.daloopa.com/docs/contact-us).

  


__Updated 7 days ago

* * *

[Tag ID Preview](/docs/tag-id-preview)[Prompt Library](/docs/prompt-library)

Ask AI

