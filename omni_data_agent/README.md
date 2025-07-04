# Omni Data Request Handler

## Overview
This document provides instructions for Claude Code to efficiently handle data requests using the available tools in the `tools/` directory. The goal is to provide quick, accurate responses to data queries without unnecessary code generation.

## Request Processing Protocol

### 1. Direct Tool Usage (Priority 1)
**When**: The request can be satisfied directly by calling an existing tool
**Action**: Use the appropriate CLI command with correct parameters and print the result

**Example Request**: "What's the price change of BTC in 24hrs?"
**Process**: 
1. Identify that this requires current Bitcoin price data
2. Use `python tools/coin_data_by_id.py bitcoin` to get current data
3. Extract and display the 24-hour price change

### 2. Data Combination/Processing (Priority 2)
**When**: The request requires combining or processing outputs from multiple tools
**Action**: Write a minimal temporary script to accomplish the task

**Example Request**: "比较 BTC 和 ETH 的 24 小时交易量"
**Process**:
1. Use existing tools to get volume data for both coins
2. Create a simple script to compare and format the results
3. Run the script and display the comparison

### 3. Unavailable Data (Priority 3)
**When**: The request cannot be fulfilled with available tools and reasonable processing
**Action**: Clearly state that the data cannot be obtained with current tools

## Tool Discovery Process

**CRITICAL**: Before processing any data request, you MUST first check the available tools by reading `tools/tools_list.md`. This file contains:
- Complete list of all available tools
- Tool purposes and capabilities
- Usage instructions and parameters
- Tool categories and classifications

**Step 1**: Always start by reading `tools/tools_list.md` to understand available tools
**Step 2**: Identify the most appropriate tool(s) for the specific data request
**Step 3**: Proceed with the request processing protocol

## Common Request Patterns

### Price Queries
- "Current price of [coin]" → Check tools_list.md for price-related tools
- "Price change of [coin]" → Check tools_list.md for market data tools
- "Historical price of [coin]" → Check tools_list.md for historical data tools

### Volume Queries  
- "Trading volume of [coin]" → Check tools_list.md for volume-related tools
- "Volume comparison" → Combine multiple tool outputs as needed
- "DEX volume rankings" → Check tools_list.md for DEX-related tools

### Market Analysis
- "Top performing coins" → Check tools_list.md for market analysis tools
- "Market cap rankings" → Check tools_list.md for ranking tools
- "Market overview" → Check tools_list.md for bulk market data tools

### Technical Analysis
- "OHLC data" → Check tools_list.md for technical analysis tools
- "Price charts" → Check tools_list.md for chart data tools
- "Custom time range data" → Check tools_list.md for time range tools

## Tool Usage Guidelines

### Step 1: Tool Selection
1. **MANDATORY**: Read `tools/tools_list.md` to discover available tools
2. Identify the most appropriate tool for the request based on tools_list.md
3. Verify the tool has the required parameters as documented in tools_list.md

### Step 2: Direct Execution
```bash
# Examples (actual commands depend on tools found in tools_list.md):
# Get coin data: python tools/[appropriate_tool].py [coin_id]
# Get top coins: python tools/[appropriate_tool].py --n [number]
# Get OHLC data: python tools/[appropriate_tool].py [coin_id] --days [number]
```
**Note**: Use the exact tool names and parameters documented in `tools/tools_list.md`

### Step 3: Data Processing (if needed)
Create minimal scripts only when:
- Combining data from multiple tools
- Performing calculations on tool outputs
- Formatting results for better presentation

### Step 4: Result Display
- Present data in clear, readable format
- Include relevant context (timestamps, currency units)
- Highlight key insights when applicable

## Error Handling

### Common Issues:
1. **Invalid coin ID**: Check tools_list.md for coin listing tools to find correct identifier
2. **API limits**: Tools handle rate limiting automatically
3. **Missing data**: Some historical data may not be available for all coins
4. **Network issues**: Tools include retry mechanisms

### Response Format:
- **Success**: Display requested data clearly
- **Partial success**: Show available data, note limitations
- **Failure**: Explain what went wrong and suggest alternatives

## Environment Setup

Environment requirements are documented in `tools/tools_list.md`. Check this file for:
- Required API keys and environment variables
- Python dependencies
- Network connection requirements

## Performance Considerations

### Efficiency First Principles
- **CRITICAL**: Return ONLY the data specifically requested by the user
- **Do NOT** return unnecessary information or verbose details
- **Do NOT** fetch comprehensive datasets when only specific fields are needed
- **Do NOT** pass large data outputs directly to LLM for processing

### Tool Usage Efficiency
- Use the most specific tool for each request
- **Minimize data retrieval**: Only fetch exactly what's needed
- **Avoid verbose tool outputs**: Use minimal necessary parameters
- **Process large datasets with scripts**: If data processing involves large volumes, write a simple script instead of loading everything into LLM context
- Prefer single tool calls over data combination when possible
- Cache results when making multiple related requests

### Data Processing Guidelines
- **For large datasets**: Write minimal scripts that process data and return only the final answer
- **For simple queries**: Extract only the specific requested field from tool output
- **For comparisons**: Use scripts to process and compare, return only the comparison result
- **Avoid verbose JSON parsing**: Extract target values directly, don't include full JSON in responses

### Response Efficiency
- **Concise answers**: Provide only what the user asked for
- **No explanatory context**: Unless specifically requested, don't explain how you got the data
- **Direct values**: Return numbers, prices, percentages directly without formatting overhead
- **Skip metadata**: Don't include timestamps, sources, or additional context unless requested

## Response Format

### Successful Response:
```
[Direct answer to the query]
[Data presented in clear format]
[Source tool used: toolname.py]
```

### Processing Response:
```
[Brief explanation of data combination needed]
[Results after processing]
[Source tools used: tool1.py, tool2.py]
```

### Unavailable Response:
```
This data cannot be obtained with the available tools.
[Brief explanation of limitations]
[Suggested alternatives if applicable]
```

## Remember

- **ALWAYS read `tools/tools_list.md` FIRST** before processing any data request
- **Minimize code generation** - prefer direct tool usage
- **Be specific and concise** in responses
- **Include data source** in responses for transparency
- **Handle edge cases gracefully** (invalid coins, missing data, etc.)
- **Never assume tool capabilities** - always verify in tools_list.md