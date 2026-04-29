# Testing Guide for Jira-Confluence MCP Server

This guide explains how to test your MCP server using different tools.

## Table of Contents

1. [Manual Testing Scripts](#manual-testing-scripts)
2. [MCP Inspector (Official Tool)](#mcp-inspector-official-tool)
3. [Integration Testing](#integration-testing)
4. [Claude Desktop Testing](#claude-desktop-testing)

---

## 1. Manual Testing Scripts

### Basic Connection Test

Tests API connectivity and credentials:

```bash
uv run python test_connection.py
```

**Tests:**
- Environment variables loading
- Client initialization
- Jira API connection
- Confluence API connection

### Your Tasks Test

Gets your assigned issues and recently modified pages:

```bash
uv run python test_my_tasks.py
```

**Shows:**
- All Jira issues assigned to you
- Confluence pages you modified recently

### Raw API Response Test

Inspects the raw JSON structure returned by APIs:

```bash
uv run python test_raw_response.py
```

**Useful for:**
- Debugging API response structure
- Understanding available fields
- Troubleshooting data parsing issues

---

## 2. MCP Inspector (Official Tool)

**MCP Inspector** is the official interactive testing tool from Anthropic for MCP servers.

### Features

- 🎯 Interactive web UI for testing MCP tools
- 🔍 Real-time inspection of requests/responses
- 📝 Tool parameter validation
- 🐛 Detailed error messages
- 📊 JSON formatting and syntax highlighting

### Installation

No installation needed! Uses `npx` to run directly.

### Usage

#### Option A: Using the provided script

```bash
./test_with_inspector.sh
```

This will:
1. Set up environment variables
2. Start your MCP server
3. Launch MCP Inspector web interface
4. Open browser at `http://localhost:5173` (or similar)

#### Option B: Manual command

```bash
# Set environment variables first
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-token-here"

# Run inspector
npx @modelcontextprotocol/inspector uv run --directory "$(pwd)" jira-confluence-mcp
```

#### Option C: Using npx directly with config

```bash
cd /path/to/jira-confluence
npx @modelcontextprotocol/inspector uv run jira-confluence-mcp
```

### Using MCP Inspector

Once the web interface opens:

1. **View Available Tools**: See all 10 MCP tools (6 Jira + 4 Confluence)
2. **Test Tool Calls**:
   - Select a tool from the list
   - Fill in required parameters
   - Click "Execute"
   - View formatted response
3. **Inspect Errors**: See detailed error messages with status codes
4. **Test Different Scenarios**: Try various JQL/CQL queries

### Example Tests in Inspector

#### Test 1: Search Jira Issues
```json
Tool: jira_search
Parameters:
{
  "jql": "assignee = currentUser() ORDER BY updated DESC",
  "max_results": 5
}
```

#### Test 2: Search Confluence Pages
```json
Tool: confluence_search
Parameters:
{
  "cql": "type = page AND space = G ORDER BY lastModified DESC",
  "limit": 10
}
```

#### Test 3: Get Specific Issue
```json
Tool: jira_get_issue
Parameters:
{
  "issue_key": "PROJ-1157"
}
```

---

## 3. Integration Testing

### Test MCP Server via Python SDK

You can also write Python tests using the MCP SDK:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_jira_search():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "jira-confluence-mcp"],
        env={
            "JIRA_BASE_URL": "https://your-domain.atlassian.net",
            "JIRA_EMAIL": "your-email@example.com",
            "JIRA_API_TOKEN": "your-token"
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

            # Call a tool
            result = await session.call_tool(
                "jira_search",
                arguments={
                    "jql": "assignee = currentUser()",
                    "max_results": 5
                }
            )
            print(f"Result: {result}")

# Run test
asyncio.run(test_jira_search())
```

Save as `test_mcp_integration.py` and run:

```bash
uv run python test_mcp_integration.py
```

---

## 4. Claude Desktop Testing

### Setup

1. Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "jira-confluence": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/jira-confluence",
        "jira-confluence-mcp"
      ],
      "env": {
        "JIRA_BASE_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-token"
      }
    }
  }
}
```

2. Restart Claude Desktop

3. Look for the 🔨 hammer icon - your MCP tools should appear

### Test Commands in Claude Desktop

Once connected, you can ask Claude:

- "Show me my assigned Jira issues"
- "Search for Confluence pages about API in the DOCS space"
- "Get details for issue PROJ-1157"
- "Create a new Jira issue in project TEST with summary 'Bug fix needed'"
- "Add a comment to issue PROJ-1157 saying 'Working on this now'"

---

## Troubleshooting

### MCP Inspector doesn't start

**Check Node.js version:**
```bash
node --version  # Should be v18+
```

**Try clearing npx cache:**
```bash
npx clear-npx-cache
```

### Environment variables not loading

**Test manually:**
```bash
echo $JIRA_BASE_URL
echo $JIRA_EMAIL
```

**Source .env file:**
```bash
set -a; source .env; set +a
```

### Connection errors

**Test basic API access:**
```bash
uv run python test_connection.py
```

**Check credentials:**
- Verify your API token at https://id.atlassian.com/manage-profile/security/api-tokens
- Ensure base URL doesn't have trailing slash
- Confirm email matches your Atlassian account

### Tools not appearing in Claude Desktop

1. Check Claude Desktop logs (View → Troubleshooting → Logs)
2. Verify absolute paths in config
3. Test server starts manually: `uv run jira-confluence-mcp`
4. Restart Claude Desktop completely

---

## Available Tools Reference

### Jira Tools

1. **jira_search** - Search issues with JQL
2. **jira_get_issue** - Get detailed issue info
3. **jira_create_issue** - Create new issue
4. **jira_add_comment** - Add comment to issue
5. **jira_get_transitions** - Get available status transitions
6. **jira_transition** - Change issue status

### Confluence Tools

7. **confluence_search** - Search pages with CQL
8. **confluence_get_page** - Get page content
9. **confluence_create_page** - Create new page
10. **confluence_update_page** - Update existing page

---

## Performance Testing

Monitor MCP server performance:

```bash
# Start with timing
time uv run jira-confluence-mcp

# Monitor memory usage
ps aux | grep jira-confluence-mcp

# Test with multiple concurrent requests (using MCP Inspector)
```

---

## Additional Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Jira REST API Docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Confluence REST API Docs](https://developer.atlassian.com/cloud/confluence/rest/v1/)

---

## Quick Test Checklist

Before deploying or using in production:

- [ ] `test_connection.py` passes
- [ ] `test_my_tasks.py` returns real data
- [ ] MCP Inspector can connect and list tools
- [ ] All 10 tools callable in MCP Inspector
- [ ] Sample JQL/CQL queries work
- [ ] Error handling works (try invalid issue key)
- [ ] Claude Desktop recognizes the server
- [ ] Can successfully call tools from Claude Desktop

---

**Last Updated:** 2025-11-06
