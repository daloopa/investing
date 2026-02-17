---
title: Docs MCP Server
url: https://docs.daloopa.com/docs/mcp
path: /docs/mcp
---

# Docs MCP Server

# Docs MCP Server

Get up and running with our API and MCP server faster by giving this MCP to a LLM

The Daloopa KnowledgeBase Model Context Protocol (MCP) server enables AI-powered code editors like Cursor and Windsurf, plus general-purpose tools like Claude Desktop, to interact directly with your Daloopa KnowledgeBase API and documentation.

## 

What is MCP?

Model Context Protocol (MCP) is an open standard that allows AI applications to securely access external data sources and tools. The Daloopa KnowledgeBase MCP server provides AI agents with:

  * **Direct API access** to Daloopa KnowledgeBase functionality
  * **Documentation search** capabilities
  * **Real-time data** from your Daloopa KnowledgeBase account
  * **Code generation** assistance for Daloopa KnowledgeBase integrations



## 

Daloopa KnowledgeBase MCP Server Setup

Daloopa KnowledgeBase hosts a remote MCP server at `https://docs.daloopa.com/mcp`. Configure your AI development tools to connect to this server. If your APIs require authentication, you can pass in headers via query parameters or however headers are configured in your MCP client.

CursorWindsurfClaude Desktop

**Add to`~/.cursor/mcp.json`:**

JSON
    
    
    {
      "mcpServers": {
        "daloopaknowledgebase": {
          "url": "https://docs.daloopa.com/mcp"
        }
      }
    }

## 

Testing Your MCP Setup

Once configured, you can test your MCP server connection:

  1. **Open your AI editor** (Cursor, Windsurf, etc.)
  2. **Start a new chat** with the AI assistant
  3. **Ask about Daloopa KnowledgeBase** \- try questions like:
     * "How do I [common use case]?"
     * "Show me an example of [API functionality]"
     * "Create a [integration type] using Daloopa KnowledgeBase"



The AI should now have access to your Daloopa KnowledgeBase account data and documentation through the MCP server.

__Updated 9 days ago

* * *

[API vs. MCP](/docs/api-vs-mcp)[API](/docs/api)

Ask AI

