# MCP Integration Guide

## Using .mcp.json for Local Development

The `.mcp.json` file in this directory is configured for **local development and testing** with MCP tools.

### Current Configuration

```json
{
  "mcpServers": {
    "jira-confluence": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp-jira-confluence",
        "python",
        "-m",
        "jira_confluence_mcp.server"
      ],
      "env": {
        "JIRA_BASE_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

### How to Use

#### 1. Update Credentials in .mcp.json

Replace the placeholder values in the `env` section:

```json
"env": {
  "JIRA_BASE_URL": "https://your-domain.atlassian.net",
  "JIRA_EMAIL": "your-real-email@example.com",
  "JIRA_API_TOKEN": "your-real-api-token"
}
```

#### 2. Test the Server

```bash
# Test MCP tools registration
uv run python test_mcp_server.py

# Test connection to Jira/Confluence (requires real credentials)
uv run python test_connection.py
```

#### 3. Use with MCP Inspector (if available)

If you have the MCP Inspector installed:

```bash
npx @modelcontextprotocol/inspector uv run python -m jira_confluence_mcp.server
```

This will open a web interface to test your MCP tools interactively.

### Alternative: Using .env File

Instead of putting credentials in `.mcp.json`, you can use a `.env` file:

1. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

2. Simplify `.mcp.json`:
```json
{
  "mcpServers": {
    "jira-confluence": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/jira-confluence",
        "python",
        "-m",
        "jira_confluence_mcp.server"
      ]
    }
  }
}
```

The server will automatically load credentials from `.env` file.

## For Claude Desktop Integration

**Do NOT use `.mcp.json` for Claude Desktop!**

Instead, configure `claude_desktop_config.json`:

### macOS
`~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
`%APPDATA%\Claude\claude_desktop_config.json`

### Linux
`~/.config/Claude/claude_desktop_config.json`

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "jira-confluence": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/jira-confluence",
        "python",
        "-m",
        "jira_confluence_mcp.server"
      ],
      "env": {
        "JIRA_BASE_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/jira-confluence` with the actual path!

## Testing Your Setup

### 1. Test Tools Registration

```bash
uv run python test_mcp_server.py
```

Expected output:
```
✅ All tools registered successfully
✅ Total: 10 tools
✅ Jira: 6 tools
✅ Confluence: 4 tools
```

### 2. Test API Connection

```bash
uv run python test_connection.py
```

Expected output:
```
✅ Jira connection successful!
✅ Confluence connection successful!
```

### 3. Test with MCP Client

If using an MCP client (like Claude Desktop or Inspector):

**Jira Commands:**
```
"Show me open issues in project TEST"
"Create a bug: 'Login fails on mobile'"
"Add comment to TEST-123: 'Working on this'"
```

**Confluence Commands:**
```
"Find pages in DOCS space"
"Show page 123456"
"Create page 'API Guide' in DOCS"
```

## Security Notes

⚠️ **Never commit `.mcp.json` with real credentials to git!**

The `.gitignore` already includes `.mcp.json` if you add credentials there, but best practice is:

1. Use `.env` file for credentials (already in `.gitignore`)
2. Keep `.mcp.json` with placeholder values
3. For Claude Desktop, put credentials in its config file

## Troubleshooting

### Server Won't Start

```bash
# Check if dependencies are installed
uv pip list | grep mcp

# Try running directly
uv run python -m jira_confluence_mcp.server
```

### Tools Not Showing

```bash
# Verify tools are registered
uv run python test_mcp_server.py
```

### Connection Fails

```bash
# Test credentials
uv run python test_connection.py

# Check environment variables
env | grep JIRA
```

### MCP Client Can't Connect

1. Check the absolute path in config
2. Verify `uv` is in PATH
3. Test command manually:
   ```bash
   uv run --directory /path/to/jira-confluence python -m jira_confluence_mcp.server
   ```

## Available Tools

### Jira (6 tools)
1. **jira_search** - Search with JQL queries
2. **jira_get_issue** - Get issue details
3. **jira_create_issue** - Create new issues
4. **jira_add_comment** - Add comments
5. **jira_get_transitions** - Get available transitions
6. **jira_transition** - Change issue status

### Confluence (4 tools)
7. **confluence_search** - Search with CQL queries
8. **confluence_get_page** - Get page content
9. **confluence_create_page** - Create new pages
10. **confluence_update_page** - Update existing pages

## Next Steps

1. ✅ Update credentials in `.mcp.json` or `.env`
2. ✅ Test connection: `uv run python test_connection.py`
3. ✅ Configure Claude Desktop (if using)
4. ✅ Start using the tools!

For more information, see:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- [SPECIFICATION.md](SPECIFICATION.md) - Technical details
