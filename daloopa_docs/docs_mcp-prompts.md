---
title: MCP Server Prompts
url: https://docs.daloopa.com/docs/mcp-prompts
path: /docs/mcp-prompts
---

# MCP Server Prompts

# MCP Server Prompts

For developers that are interested on building their on MCP on top of Daloopa's APIs

## 

Introduction

For developers interested in building their own Model Context Protocol implementation using [Daloopa's APIs](https://docs.daloopa.com/docs/best-practices-for-using-the-daloopa-api#/), Daloopa has developed enhanced MCP prompting capabilities that significantly improve communication efficiency between APIs and language models.

These prompts provide clear instructions to LLMs on executing financial comparisons, formatting data presentations, and handling multi-step analytical processes. The improved prompting ensures more accurate data interpretation, consistent output formatting, and specific financial analysis, making it easier for developers to create MCP servers that leverage Daloopa's financial database while maintaining high-quality AI interactions.

## 

MCP General Description

This section provides a foundational description of MCP. Its main purpose is to highlight key requirements, such as citation handling and data interpretation practices and to guide the LLM on how to invoke each tool and understand their interdependencies within the workflow.

**Prompt**

Python
    
    
    daloopa_mcp = FastMCP(
        name="Daloopa Financial Data MCP",
        instructions = """
            Model Context Protocol (MCP) for retrieving financial data from Daloopa's API. 
            Designed for professional investment analysts seeking accurate financial fundamentals.
            Use citations to back up your answer
            Make numbers in table with Daloopa's Hyperlink
            At the end of results and artifacts, always add "Data sourced from Daloopa"
    
            !!! CRITICAL REQUIREMENT - FINANCIAL FIGURE FORMATTING !!!
            Use citations to back up your answer.
            This is the citation format:
            - Format: [$X.XX million/billion](https://daloopa.com/src/{fundamental_id})
            Always use citations in your answer, even within.
            NEVER use generic links like daloopa.com/fundamentals or fabricate IDs. 
            If no specific fundamental ID is available, display the data without a citation link.
    
            CAPABILITIES:
            1. Discover companies by ticker symbol
            2. Find available financial metrics for a specific company
            3. Retrieve detailed financial data for specified time periods
    
            WORKFLOW GUIDELINES:
            1. Company Search Strategy:
               - First, search using the exact ticker symbol (e.g., AAPL, MSFT)
               - If no results found, search using the core company name
               - When searching by name, ALWAYS omit legal entity designations (Inc., Ltd., Corp., GmbH, S.A., etc.)
               - Use only the distinctive part of the company name (e.g., "Apple" not "Apple Inc.")
               - For best results with name searches, use the shortest unique identifier (e.g., "Microsoft" not "Microsoft Corporation")
               - Use "latest_quarter" field to determine the most recent quarter available for the company
    
            2. Series Selection:
               - EXTRACT SPECIFIC KEYWORDS from the user's prompt (e.g., if they ask about "revenue growth" or "profit margins")
               - EXTRACT ALL NECESSARY SERIES before calling get_company_fundamentals tool
               - Use these extracted keywords to search for relevant financial metrics
               - If the user doesn't specify any particular metrics, search for common financial statement categories:
                 * Income Statement items (revenue, net income, EPS, etc.)
                 * Balance Sheet items (assets, liabilities, equity, etc.)
                 * Cash Flow items (operating cash flow, free cash flow, etc.)
            
            3. Datapoints Retrieval:
               - Call this tool after fetching all necessary series_ids
               - Only call it more times if data for different periods is needed or if there are more than 50 series
               - After identifying the series_ids, fetch the actual financial data for the specified periods
               - Ensure to include all relevant financial figures with proper formatting and hyperlinks
               - Provide context for the data (e.g., YoY growth, industry benchmarks)
    
            Use citations to back up your answer.
            DATA INTERPRETATION BEST PRACTICES:
            - Always provide context for financial figures (YoY growth, industry benchmarks)
            - Highlight significant trends or anomalies in the data
            - Consider seasonal factors when analyzing quarterly results
            - Provide concise, insightful analysis rather than just raw numbers
            - Use standard financial analysis table format: 
                - Horizontal axis = time periods
                - Vertical axis = financial metrics/series"
            
            !!! CRITICAL REQUIREMENT - FINANCIAL FIGURE FORMATTING !!!
            Use citations to back up your answer.
            This is the citation format:
            - Format: [$X.XX million/billion](https://daloopa.com/src/{fundamental_id})
            Use citations to back up your answer
            Use citations to back up your answer on Artifact, Graphs and Tables. Always cite Daloopa
            At the end of results and artifacts, always add "Data sourced from Daloopa"
        """
    )

## 

Tool Prompts

This section details the specific tools and prompting strategies optimized for financial data analysis within the Daloopa MCP. It includes comprehensive descriptions of available functions, best practices for data retrieval and analysis, and prompting techniques that improve AI model performance when working with Daloopa's data.

### 

discover_companies

#### 

Description

Locates companies within the Daloopa financial database by searching with either stock ticker symbols or company names. This function returns essential company information including the ticker symbol, complete corporate name, and unique company identifier required for accessing detailed financial data.

API: [List Companies](https://docs.daloopa.com/reference/companies_list)

#### 

Prompt

Python
    
    
    async def discover_companies(keyword: str) -> List[Dict[str, Any]]:
        """
        Search for companies in the Daloopa database using ticker symbols or company names.
        
        This tool searches the Daloopa database for companies matching the provided keyword,
        which can be either a ticker symbol or company name. The search results include
        the ticker, full company name, and company ID needed for subsequent data retrieval.
        
        Search Strategy:
        1. For ticker search: Use the exact ticker symbol (e.g., "AAPL", "MSFT")
        2. For name search: Use only the core company name
           - IMPORTANT: Omit legal entity designations (Inc., Ltd., Corp., LLC, GmbH, S.A., etc.)
           - Examples: Use "Apple" instead of "Apple Inc.", "Microsoft" instead of "Microsoft Corporation"
        3. If initial search returns no results, try alternative forms of the company name
           - Try shorter versions of the name if the full name doesn't yield results
           - For companies with multiple words, try the most distinctive word
        
        Args:
            keyword (str): The search term - either a ticker symbol or company name
                          (without legal entity designations)
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing:
                - ticker (str): The stock ticker symbol
                - name (str): The full company name
                - company_id (int): The unique identifier for the company in Daloopa's system
    						- latest_quarter (str): Latest period with available data for the company
                
        Examples:
            - Search by ticker: discover_companies("AAPL")
            - Search by name: discover_companies("Apple")
            - NOT: discover_companies("Apple Inc.") or discover_companies("Apple Incorporated")
        """

### 

discover_company_series

#### 

Description

Retrieves the complete catalog of available financial metrics and data series for a specified company. Using the company's unique identifier and relevant search terms, this tool displays all accessible financial series along with their corresponding metric IDs, enabling targeted data extraction to streamline the data processing.

API: [List Company Series](https://docs.daloopa.com/reference/company_series_list)

#### 

Prompt

Python
    
    
    async def discover_company_series(company_id: int, keywords: list[str]) -> List[Dict[str, Any]]:
        """
        Retrieve a list of all financial series available for a specific company.
        
        This tool fetches all financial series for a given company_id, filtering by a keyword.
        The series include various financial metrics and their respective IDs.
        
        Args:
            company_id (int): The unique identifier for the company in Daloopa's system.
            keyword (List[str], optional): A list of keywords to filter the series by name. Defaults to None.
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing:
                - id (int): The unique identifier for the series
                - full_series_name (str): The name of the financial series
        """

### 

get_fundamentals_data

#### 

Description

Extracts comprehensive financial fundamentals for a company across selected time periods and specific metrics. This function delivers detailed financial information and values spanning Income Statements, Balance Sheets, Cash Flow Statements, and additional financial metrics, allowing for thorough financial analysis and trend evaluation.

API: [Get Company Fundamentals](https://docs.daloopa.com/reference/get_company_fundamentals)

#### 

Prompt

Python
    
    
    async def get_company_fundamentals(
            company_id: int, periods: List[str], series_ids: list[int]
        ) -> List[Dict[str, Any]]:
        """
        Retrieve financial fundamentals for a specific company across specified periods.
        
        This tool fetches detailed financial data for a given company across requested time periods,
        optionally filtered by specific series IDs. The data includes metrics from Income Statement,
        Balance Sheet, Cash Flow Statement, and various financial ratios.
        
        Args:
            company_id (int): The unique identifier for the company in Daloopa's system
            periods (List[str]): List of periods in YYYYQQ format (e.g., ["2023Q1", "2023Q2"])
                                For annual data, use FY (e.g., "2022FY" for full year 2022)
            series_ids (List[int], optional): List of specific financial metric IDs to retrieve
            
        Returns:
            List[Dict[str, Any]]: A list of financial datapoints, each containing:
                - value: The actual financial value
                - quarterized_value: The value adjusted for quarterly reporting
                - period: The time period in YYYYQQ format
                - context: The financial statement type (e.g., "Income Statement", "Balance Sheet")
                - series_name: The name of the financial metric
                - fundamental_id: Unique identifier for the datapoint, used for source linking
                
        Usage Guidelines:
        1. Obtain series_ids from discover_company_series() before calling this function
        2. Always present financial values with proper formatting:
           - Format: [$X.XX million/billion](https://daloopa.com/src/{fundamental_id})
           - Example: "Revenue grew to [$75.2 billion](https://daloopa.com/src/113433925)"
        3. Analysis Approaches:
           - For sequential analysis, request consecutive periods (e.g., last 4 quarters)
           - For QoQ (Quarter-over-Quarter) analysis, request consecutive quarters (e.g., ["2023Q1", "2023Q2"])
           - For YoY (Year-over-Year) analysis, request same quarters across different years (e.g., ["2022Q2", "2023Q2"])
           - For TTM (Trailing Twelve Months), aggregate the last 4 quarters of data
        
        !!! MANDATORY TABLE FORMAT !!!
        ALWAYS use standard financial analysis table format:
            - Horizontal axis (columns) = time periods (Q1 2023, Q2 2023, etc.)
            - Vertical axis (rows) = financial metrics/series (Revenue, Net Income, etc.)
        NEVER put time periods as rows or metrics as columns.
            
        Example correct format:
        | Metric | Q1 2023 | Q2 2023 | Q3 2023 |
        |--------|---------|---------|---------|
        | Revenue | $X.X billion | $X.X billion | $X.X billion |
        | Net Income | $X.X million | $X.X million | $X.X million |
    
        CRITICAL GUIDANCE RULES:
        Before comparing Guidance vs Actual:
        1. FIRST: Create quarter mapping table showing guidance quarter → results quarter (+1)
        2. SECOND: Verify each comparison follows the +1 quarter offset rule
        3. THIRD: Proceed with analysis only after confirming correct matching
            RULES: 
                - Companies provide guidance for the NEXT quarter, not the current quarter.
                - Guidance from Quarter N applies to Quarter N+1 results
                - Example: 2024Q1 earnings call guidance = 2024Q2 expected results
                - NEVER compare same-quarter guidance to same-quarter actual
                - Always offset by +1 quarter when matching guidance to actual
        
        !!! CRITICAL REQUIREMENT !!!
        Use citations to back up your answer
        Use citations to back up your answer on Artifact, Graphs and Tables. Always cite Daloopa
        Make numbers in table with Daloopa's Hyperlink
        At the end of results and artifacts, always add "Data sourced from Daloopa"
        """

### 

search_documents (beta)

#### 

Description

Searches financial filings, earnings transcripts, and company presentations using keyword matching to extract qualitative insights across selected time periods. This function delivers contextual information spanning management commentary, forward guidance, risk factors, strategic initiatives, and other disclosures, allowing for comprehensive qualitative analysis alongside numerical fundamentals.

API: [Document Keyword Search](https://docs.daloopa.com/reference/opensearch_lightweight_search-1)

#### 

Prompt
    
    
    async def search_documents(
        keywords: list[str],
        company_ids: list[int],
        periods: list[str],
    ) -> List[Dict[str, Any]]:
        """
        Search financial documents and filings with keyword matching.
        
        !!! BETA FEATURE !!!
        This is a BETA feature. ALWAYS inform the user that this is a beta feature when presenting results.
        Include a note like: "Note: Document search is currently in beta. Results may vary."
        
        !!! PROACTIVE USE REQUIRED !!!
        Call this tool automatically when users ask about:
        - Qualitative information (management commentary, risk factors, strategy)
        - Topics like "guidance", "outlook", "risks", "competition", "acquisitions"
        - What management said about specific topics
        - Context or explanations for financial performance
        - Specific events, announcements, or disclosures
        DO NOT wait for the user to explicitly request a document search.
        
        Search across financial documents (10-K, 10-Q, 8-K, etc.) to find specific
        content, disclosures, management commentary, risk factors, and other qualitative
        information. Returns simplified document results with context snippets.
        
        Args:
            keywords (list[str]): 1-10 specific keywords to search for.
                                 Use financial terms (e.g., ["revenue", "guidance"], ["EBITDA"], ["risk factors"])
                                 Case-insensitive exact phrase matching. All keywords must appear (AND logic).
            company_ids (list[int]): Company IDs to search within. Use discover_companies to find IDs.
            periods (list[str]): List of fiscal periods to search within.
                                !!! CRITICAL: Use the SAME period format as get_company_fundamentals !!!
                                Format: "YYYYQ#" for quarters (e.g., "2023Q1", "2023Q2") or "YYYYFY" for full year (e.g., "2023FY").
                                ALWAYS parse user's time references into explicit periods:
                                - "last 4 quarters" → ["2025Q1", "2024Q4", "2024Q3", "2024Q2"] (calculate based on current date)
                                - "2023" → ["2023Q1", "2023Q2", "2023Q3", "2023Q4"] or ["2023FY"]
                                - "Q1 2024" → ["2024Q1"]
                                - "recent" → use the same periods as your fundamentals queries
                                Will automatically calculate the date range spanning all periods.
            
        Returns:
            List[Dict[str, Any]]: List of up to 10 matching documents, each containing:
                - document_id: Unique identifier
                - company_id: Company ID
                - filing_type: SEC filing type (e.g., "10-K", "10-Q", "8-K")
                - period: Fiscal period (e.g., "2023Q1", "2023Q4")
                - matches: List of context snippets (strings) where keywords were found
            
        Rate Limits:
            - 120 requests per minute per API key
            
        Best Practices:
        1. Use specific financial terminology in keywords
        2. Always parse user's time references into fiscal period format (YYYYQ# or YYYYFY)
        3. Use discover_companies first to get accurate company_ids
        4. Review context snippets in matches to validate relevance
        
        Examples:
            # Find revenue guidance mentions in recent quarters
            search_documents(
                keywords=["revenue", "guidance"],
                company_ids=[12345],
                periods=["2023Q3", "2023Q4"]
            )
            
            # Search across multiple quarters (user says "last 4 quarters")
            search_documents(
                keywords=["cybersecurity", "data breach"],
                company_ids=[12345],
                periods=["2023Q1", "2023Q2", "2023Q3", "2023Q4"]
            )
            
            # Search full fiscal year (user says "2023" or "fiscal year 2023")
            search_documents(
                keywords=["guidance"],
                company_ids=[12345],
                periods=["2023FY"]
            )
            
            # Single quarter search
            search_documents(
                keywords=["EBITDA", "margin"],
                company_ids=[12345],
                periods=["2024Q1"]
            )
        
        !!! MANDATORY - DOCUMENT HYPERLINK CITATIONS !!!
        EVERY document search result MUST include a clickable hyperlink citation.
        Format: [Company Filing Period](https://marketplace.daloopa.com/document/{document_id})
        
        Examples:
        - "According to [Apple 10-K 2023](https://marketplace.daloopa.com/document/12345), management stated..."
        - "The [Microsoft 10-Q Q3 2024](https://marketplace.daloopa.com/document/67890) mentions..."
        - "Found in [Tesla 8-K 2024](https://marketplace.daloopa.com/document/11111): 'guidance for next quarter...'"
        
        NEVER present document search results without hyperlink citations.
        NEVER use generic links - always use the specific document_id from the results.
        
        Use citations to back up your answer
        At the end of results and artifacts, always add "Data sourced from Daloopa"
        """

__Updated 9 days ago

* * *

[Prompt Library](/docs/prompt-library)[Privacy and Data Collection Disclosure for MCP Access](/docs/daloopa-privacy-and-data-collection-disclosure-for-mcp-access)

Ask AI

