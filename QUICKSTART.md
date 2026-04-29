# Quick Start Guide

Get your Jira-Confluence MCP server running in 5 minutes!

## 1. Install Dependencies

```bash
uv pip install -e .
```

## 2. Get Your API Token

1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Name it (e.g., "Claude MCP")
4. Copy the token (shown only once!)

## 3. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env  # or use any text editor
```

Add your credentials:
```env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
```

## 4. Test Connection

```bash
uv run python test_connection.py
```

Expected output:
```
✅ Jira connection successful!
✅ Confluence connection successful!
```

## 5. Configure Claude Desktop

Edit your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

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

To get the absolute path:
```bash
pwd
```

## 6. Restart Claude Desktop

Completely quit and reopen Claude Desktop.

## 7. Try It Out!

In Claude Desktop, try these commands:

### Jira Examples
```
"Show me all open issues in project TEST"
"Create a bug in TEST: 'Login button not working'"
"Add a comment to TEST-123: 'Working on this now'"
"What status transitions are available for TEST-123?"
```

### Confluence Examples
```
"Find all pages in DOCS space"
"Show me page 123456"
"Create a new page in DOCS titled 'API Guide' with overview section"
```

## Troubleshooting

### Connection test fails?
- Check your credentials in `.env`
- Verify `JIRA_BASE_URL` is correct (should be like `https://your-domain.atlassian.net`)
- Make sure API token hasn't expired

### Claude Desktop doesn't show tools?
- Check the config file path is correct
- Verify absolute path in config is correct
- Check Claude Desktop logs for errors
- Make sure you fully quit and reopened Claude Desktop

### Permission errors?
- Verify your Atlassian account has access to the projects/spaces
- Check API token permissions

## What's Available?

### 10 MCP Tools

**Jira (6 tools):**
1. Search issues with JQL
2. Get issue details
3. Create issues
4. Add comments
5. Get status transitions
6. Change issue status

**Confluence (4 tools):**
7. Search pages with CQL
8. Get page content
9. Create pages
10. Update pages

### Auto-Features

✅ **Plain text → ADF/Storage Format** - No need to format manually
✅ **Auto-version fetching** - Don't worry about Confluence versions
✅ **Pagination** - Handle large result sets
✅ **Markdown-like syntax** - Use **bold**, *italic*, `code`, etc.

## Need Help?

- See [README.md](README.md) for full documentation
- Check [SPECIFICATION.md](SPECIFICATION.md) for detailed API info
- Review [CLAUDE.md](CLAUDE.md) for development guidance

## Example Workflows

### Create and Track a Bug
```
1. "Create a bug in TEST: 'Login fails on iOS'"
2. "Show me TEST-456"  (assuming that's the created issue)
3. "Add comment to TEST-456: 'Reproduced on iPhone 12'"
4. "What transitions are available for TEST-456?"
5. "Move TEST-456 to In Progress"
```

### Document an API
```
1. "Search for 'API' pages in DOCS space"
2. "Create a new page in DOCS: 'REST API v2 Documentation'"
3. "Update page 123456 with the new endpoint information"
```

---

**That's it!** You're ready to use Jira and Confluence from Claude Desktop.
