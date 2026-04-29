# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ IMPORTANT PROJECT RULES

### Language and Documentation Standards

**ALL code, comments, documentation, and commit messages MUST be in English ONLY.**

This is a strict requirement for this project:
- ✅ **Code**: All variable names, function names, class names in English
- ✅ **Comments**: All inline comments and docstrings in English
- ✅ **Documentation**: All `.md` files, README, guides in English
- ✅ **Commit messages**: All git commit messages in English
- ✅ **Error messages**: All user-facing errors in English
- ❌ **NO Russian** or any other language in code or documentation

**Rationale:**
- International collaboration and open-source potential
- Industry standard practice
- Better integration with tools and IDEs
- Wider community accessibility

## Project Overview

This is an MCP (Model Context Protocol) server for Atlassian Jira and Confluence REST API integration. The server provides tools to manage Jira issues and Confluence pages from Claude Desktop.

**Current Status:** Production Ready - fully implemented and tested.

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv
uv pip install -e .

# Or install specific dependencies
uv pip install mcp requests

# Run the server (once implemented)
uv run python -m jira_confluence_mcp.server
```

### Testing
```bash
# Load environment variables and test
source .env  # or set -a; source .env; set +a
uv run python -m jira_confluence_mcp.server

# Run all tests
uv run pytest tests/

# Test specific module
uv run python tests/test_connection.py
```

### Package Management
- Using **uv** as the package manager
- Python version: **3.12.11** (specified in .python-version)

## Architecture

### Package Structure
```
jira-confluence/
├── jira_confluence_mcp/     # Main package
│   ├── __init__.py          # Package initialization
│   ├── server.py            # MCP server and tool definitions
│   ├── client.py            # HTTP client for Atlassian APIs
│   ├── models.py            # Data models
│   ├── formatters.py        # Response formatters
│   └── errors.py            # Error handling
├── tests/                   # Test suite
│   ├── test_connection.py   # API connection tests
│   ├── test_mcp_tools.py    # MCP tool tests
│   └── ...
├── docs/                    # Documentation
│   ├── SPECIFICATION.md     # Technical specification
│   ├── API_CHANGES.md       # API changelog
│   └── ...
├── pyproject.toml           # Project configuration
├── README.md                # User documentation
└── CLAUDE.md                # AI assistant instructions
```

### Core Components

#### 1. JiraConfluenceClient Class
HTTP client for Atlassian APIs with Basic Auth using API tokens.

**Supports:**
- Jira Cloud REST API v3 (default, uses Atlassian Document Format)
- Jira Server/Data Center REST API v2 (uses plain text/wiki markup)
- Confluence Cloud REST API v1

**Key Methods:**
- Jira: `search_jira_issues()`, `get_jira_issue()`, `create_jira_issue()`, `update_jira_issue()`, `add_jira_comment()`, `get_jira_transitions()`, `transition_jira_issue()`
- Confluence: `search_confluence()`, `get_confluence_page()`, `create_confluence_page()`, `update_confluence_page()`, `get_confluence_labels()`, `add_confluence_labels()`, `remove_confluence_labels()`

#### 2. MCP Server Functions
- `create_server(client)` - Initialize MCP server with tools
- `list_tools()` - Register 15 MCP tools (8 Jira + 7 Confluence)
- `call_tool(name, arguments)` - Route tool calls to client methods
- `main()` - Entry point with environment variable loading

### API Endpoints

**Jira REST API v3 (Cloud - default):**
- Base path: `/rest/api/3/`
- Search: `POST /search/jql` with JSON body
- Issues: `/issue/{issueKey}`
- Comments: `/issue/{issueKey}/comment`
- Transitions: `/issue/{issueKey}/transitions`
- Rich text: Atlassian Document Format (ADF)

**Jira REST API v2 (Server/Data Center):**
- Base path: `/rest/api/2/`
- Search: `GET /search?jql=...` with query params
- Same endpoints for issues, comments, transitions
- Rich text: Plain text or wiki markup

**Confluence REST API v1:**
- Base path: `/wiki/rest/api/`
- Search: `/content/search` (CQL queries)
- Content: `/content/{id}`
- Labels: `/content/{id}/label` (GET, POST, DELETE)
- Supports storage format (HTML-like)

## Authentication

Uses **Basic Authentication** with API tokens:
- Header: `Authorization: Basic base64(email:api_token)`
- Get tokens at: https://id.atlassian.com/manage-profile/security/api-tokens

**Environment Variables Required:**
```bash
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
JIRA_API_VERSION=3  # Optional: "3" for Cloud (default), "2" for Server/Data Center
```

## MCP Tools (To Implement)

### Jira Tools
1. **jira_search** - Search issues with JQL queries
2. **jira_get_issue** - Get detailed issue information
3. **jira_create_issue** - Create new issue (project_key, summary, issue_type, description)
4. **jira_add_comment** - Add comment to issue
5. **jira_get_transitions** - Get available status transitions
6. **jira_transition** - Change issue status

### Confluence Tools
7. **confluence_search** - Search pages with CQL queries
8. **confluence_get_page** - Get page content and metadata
9. **confluence_create_page** - Create new page (space_key, title, body, parent_id)
10. **confluence_update_page** - Update existing page (requires version number)
11. **confluence_get_labels** - Get all labels for a page
12. **confluence_add_labels** - Add labels to a page (page_id, labels[])
13. **confluence_remove_labels** - Remove labels from a page (page_id, labels[])

## Response Size Optimization

### Issue Details and Token Limits

MCP has a token limit of 25,000 tokens per tool response. By default, `jira_get_issue` returns only essential fields to avoid exceeding this limit:

**Default Essential Fields:**
- key, summary, description, status, priority
- assignee, reporter, created, updated, resolutiondate
- issuetype, parent, subtasks, issuelinks, labels
- fixVersions, components

For large issues with extensive comments or attachments, use separate tools:
- `jira_get_issue` - Core issue data (default fields)
- `jira_get_issue_comments` - Comments with pagination

### Usage Examples

```python
# Get essential fields (recommended for large issues)
issue = jira_get_issue(issue_key="PROJ-1157")
# Returns ~15k tokens for typical large issues

# Get specific fields only
issue = jira_get_issue(
    issue_key="PROJ-1157",
    fields=["key", "summary", "status", "assignee"]
)
# Returns ~5k tokens with minimal data

# Get all fields (use with caution - may exceed token limits)
issue = jira_get_issue(issue_key="PROJ-1157", fields=["*all"])
# May return 50k+ tokens for issues with long history

# Get comments separately with pagination
comments = jira_get_issue_comments(
    issue_key="PROJ-1157",
    max_results=20,
    offset=0
)
# Returns first 20 comments

# Get next batch of comments
comments = jira_get_issue_comments(
    issue_key="PROJ-1157",
    max_results=20,
    offset=20
)
```

### Expected Response Sizes

| Scenario | Field Selection | Typical Size | Token Limit Safe |
|----------|----------------|--------------|------------------|
| Small issue | Default | ~5k tokens | ✅ Yes |
| Medium issue | Default | ~12k tokens | ✅ Yes |
| Large issue (PROJ-1157) | Default | ~18k tokens | ✅ Yes |
| Large issue | All fields `["*all"]` | 50k-100k tokens | ❌ No |
| Comments only | N/A (use jira_get_issue_comments) | ~2k-10k tokens | ✅ Yes |

### Best Practices

1. **Use default fields** for most operations - reduces response size by ~80%
2. **Request specific fields** when you only need certain data
3. **Get comments separately** for issues with many comments (>10)
4. **Avoid `["*all"]`** unless you specifically need custom fields or full history
5. **Use pagination** with `jira_get_issue_comments` for issues with 50+ comments

## Data Formats

### Jira Issue Description
Uses **Atlassian Document Format** (ADF):
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Your text"}]
    }
  ]
}
```

### Confluence Body
Uses **Storage Format** (HTML-like with macros):
```html
<h2>Heading</h2>
<p>Paragraph with <strong>formatting</strong></p>
<ac:structured-macro ac:name="code">
  <ac:plain-text-body><![CDATA[code here]]></ac:plain-text-body>
</ac:structured-macro>
```

## Query Languages

### JQL (Jira Query Language) Examples
```
project = MYPROJ AND status = Open
assignee = currentUser() AND status != Done
type = Bug AND updated > -7d ORDER BY updated DESC
assignee is EMPTY
priority in (High, Highest)
```

### CQL (Confluence Query Language) Examples
```
space = DOCS AND type = page
title ~ "API" AND space in (DEV, DOCS)
lastModified > now("-7d") AND type = page
creator = currentUser()
text ~ "authentication"
```

## Claude Desktop Integration

Add to `claude_desktop_config.json`:
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
        "JIRA_API_TOKEN": "your-token",
        "JIRA_API_VERSION": "3"
      }
    }
  }
}
```

**API Version:**
- `"3"` (default) - Jira Cloud with Atlassian Document Format
- `"2"` - Jira Server/Data Center with plain text/wiki markup

**Config locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

## Error Handling

Common HTTP status codes to handle:
- **401 Unauthorized** - Invalid credentials or expired token
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Invalid issue key, page ID, or endpoint
- **400 Bad Request** - Invalid JQL/CQL or request format
- **429 Too Many Requests** - Rate limit exceeded

Return errors in format:
```json
{
  "error": "Error description",
  "details": "API details"
}
```

## Implementation Notes

- Use `requests.Session` for connection pooling
- All API responses return JSON
- Jira fields should return: summary, status, assignee, reporter, priority, created, updated, description
- Confluence pages need version number for updates (increment by 1)
- Issue transitions require two-step process: get available transitions, then apply by ID
- Storage format preserves Confluence formatting and macros

## References

- [Jira Cloud REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Confluence Cloud REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [JQL Tutorial](https://www.atlassian.com/software/jira/guides/jql)
- [CQL Tutorial](https://developer.atlassian.com/cloud/confluence/cql/)
- [Confluence Storage Format](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)

## Detailed Specification

See `docs/SPECIFICATION.md` for comprehensive details including:
- Complete API endpoint mappings
- Detailed parameter specifications for all 15 tools
- Security and authentication guidelines
- Data format examples and workflows
- Phase 2 enhancement ideas (attachments, sprints, batch operations)
