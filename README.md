# Jira-Confluence MCP Server

MCP (Model Context Protocol) server for integrating Atlassian Jira and Confluence with Claude Desktop.

## Features

- **10 MCP Tools** for Jira and Confluence operations
- **Automatic format conversion**: Plain text / ADF (Jira) and Storage Format (Confluence)
- **Pagination support** for search operations
- **Auto-version fetching** for Confluence page updates
- **Comprehensive error handling** with helpful messages

### Jira Tools (6)
1. `jira_search` - Search issues with JQL
2. `jira_get_issue` - Get detailed issue information
3. `jira_create_issue` - Create new issues
4. `jira_add_comment` - Add comments to issues
5. `jira_get_transitions` - Get available status transitions
6. `jira_transition` - Change issue status

### Confluence Tools (4)
7. `confluence_search` - Search pages with CQL
8. `confluence_get_page` - Get page content and metadata
9. `confluence_create_page` - Create new pages
10. `confluence_update_page` - Update existing pages

## Requirements

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Atlassian account with API token
- Claude Desktop (for MCP integration)

## Installation

### 1. Clone or download the repository

```bash
cd jira-confluence
```

### 2. Install dependencies

```bash
uv pip install -e .
```

Or install directly:

```bash
uv pip install mcp requests python-dotenv
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
```

#### Getting an API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**
3. Give it a name (e.g., "Claude MCP")
4. Copy the token (shown only once!)

### 4. Test the connection

```bash
uv run python test_connection.py
```

You should see:
```
 Jira connection successful!
 Confluence connection successful!
```

## Usage

### Running Locally (Development)

```bash
# Run the MCP server
uv run python -m jira_confluence_mcp.server

# Or use the MCP dev tools
uv run mcp dev jira_confluence_mcp/server.py
```

### Integrating with Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

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

**Important**: Replace `/absolute/path/to/jira-confluence` with the actual absolute path to this directory.

Restart Claude Desktop completely (quit and reopen).

## Example Usage in Claude

Once configured, you can use natural language commands in Claude Desktop:

### Jira Examples

```
"Show me all open bugs in project TEST"
"Create a bug in TEST project: 'Login button broken on mobile'"
"Add a comment to TEST-42: 'Working on this now'"
"What are the available status transitions for TEST-42?"
"Move TEST-42 to In Progress"
"Show details for issue TEST-123"
```

### Confluence Examples

```
"Find all pages in the DOCS space"
"Show me the content of Confluence page 123456"
"Create a new page in DOCS space titled 'API Documentation' with an overview section"
"Update page 123456 with new content"
```

### Query Languages

**JQL (Jira Query Language) Examples:**
```
project = MYPROJ AND status = Open
assignee = currentUser() AND status != Done
type = Bug AND updated > -7d ORDER BY updated DESC
priority in (High, Highest)
```

**CQL (Confluence Query Language) Examples:**
```
space = DOCS AND type = page
title ~ "API" AND space in (DEV, DOCS)
lastModified > now("-7d")
text ~ "authentication"
```

## Project Structure

```
├── jira_confluence_mcp/
│   ├── __init__.py       # Package initialization
│   ├── server.py         # MCP server with 10 tools
│   ├── client.py         # Jira/Confluence API client
│   ├── formatters.py     # ADF and Storage Format converters
│   ├── models.py         # Pydantic data models
│   └── errors.py         # Error handling
├── test_connection.py    # Connection test script
├── pyproject.toml        # Project configuration
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── SPECIFICATION.md     # Detailed specification
└── CLAUDE.md            # Claude Code guidance
```

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests (when implemented)
pytest
```

### Code Formatting

```bash
# Format code
black jira_confluence_mcp/

# Lint code
ruff check jira_confluence_mcp/

# Type checking
mypy jira_confluence_mcp/
```

## Troubleshooting

### Authentication Failed (401)
- Check your email and API token in `.env`
- Verify the token hasn't expired
- Create a new API token

### Permission Denied (403)
- Check that your account has access to the project/space
- Verify permissions in Jira/Confluence

### Resource Not Found (404)
- Verify issue keys and page IDs are correct
- Check that the resource exists

### Rate Limit Exceeded (429)
- Reduce the frequency of requests
- Wait a few minutes before retrying

### Connection Issues
- Verify `JIRA_BASE_URL` is correct
- Check your internet connection
- Ensure no firewall is blocking the connection

## Security

- **Never commit** `.env` file or API tokens to git
- Store credentials in environment variables or Claude Desktop config
- Rotate API tokens regularly
- Use dedicated service accounts for automation
- Limit token permissions to required projects/spaces

## API Documentation

- [Jira Cloud REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Confluence Cloud REST API v1](https://developer.atlassian.com/cloud/confluence/rest/v1/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [JQL Tutorial](https://www.atlassian.com/software/jira/guides/jql)
- [CQL Tutorial](https://developer.atlassian.com/cloud/confluence/cql/)

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the [SPECIFICATION.md](SPECIFICATION.md) for detailed documentation
2. Review [CLAUDE.md](CLAUDE.md) for development guidance
3. Verify your credentials and permissions
4. Check Atlassian API status

## Version

Current version: 0.1.0

## Author

Created for Claude Desktop MCP integration
