# Specification: MCP Server for Jira and Confluence

## 📋 Project Description

Development of an MCP (Model Context Protocol) server for integration with Atlassian Jira and Confluence through REST API. The server provides a set of tools for working with Jira issues and Confluence pages from Claude Desktop.

---

## 🎯 Project Goals

1. Provide a convenient interface for working with Jira through Claude
2. Enable access to Confluence documentation
3. Implement basic CRUD operations for both systems
4. Maximize simplicity of setup and usage
5. Ensure security through API tokens

---

## 🏗️ Architecture

### Project Structure

```
jira-confluence/
├── jira_confluence_mcp/
│   ├── __init__.py           # Package initialization
│   ├── server.py             # Main server code
│   ├── client.py             # HTTP client for APIs
│   ├── errors.py             # Error handling
│   └── formatters.py         # Data format converters
├── pyproject.toml            # Project config and dependencies
├── README.md                 # Documentation
├── SPECIFICATION.md          # This file
├── CLAUDE.md                 # Claude Code instructions
├── TESTING.md                # Testing guide
├── .env.example              # Example configuration
└── .gitignore                # Ignored files
```

### System Components

#### 1. JiraConfluenceClient (class)
**Purpose:** Handle all API requests to Jira and Confluence

**Attributes:**
- `base_url: str` - base URL of Atlassian instance
- `auth: tuple` - tuple (email, api_token) for authentication
- `session: requests.Session` - session for HTTP requests

**Methods:**

##### General
- `__init__(base_url, email, api_token)` - initialize client
- `_request(method, endpoint, **kwargs)` - base method for API requests

##### Jira
- `search_jira_issues(jql, max_results)` - search issues by JQL
- `get_jira_issue(issue_key)` - get issue details
- `create_jira_issue(project_key, summary, issue_type, description)` - create issue
- `update_jira_issue(issue_key, **fields)` - update issue fields
- `add_jira_comment(issue_key, comment)` - add comment
- `get_jira_transitions(issue_key)` - get available transitions
- `transition_jira_issue(issue_key, transition_id)` - change status

##### Confluence
- `search_confluence(cql, limit)` - search pages by CQL
- `get_confluence_page(page_id, expand)` - get page
- `create_confluence_page(space_key, title, body, parent_id)` - create page
- `update_confluence_page(page_id, title, body, version)` - update page

#### 2. MCP Server (functions)
**Purpose:** Register and handle MCP tools

**Functions:**
- `create_server(client)` - create and configure MCP server
- `list_tools()` - register available tools
- `call_tool(name, arguments)` - handle tool calls
- `main()` - application entry point

---

## 🔧 Technical Requirements

### Dependencies

```toml
[project]
dependencies = [
    "mcp>=1.20.0",      # MCP SDK for creating servers
    "requests>=2.31.0", # HTTP client for API requests
    "python-dotenv>=1.0.0", # Environment variable management
]
```

### Environment Variables

```bash
JIRA_BASE_URL      # https://your-domain.atlassian.net
JIRA_EMAIL         # your-email@example.com
JIRA_API_TOKEN     # API token from Atlassian
```

### System Requirements

- Python >= 3.10
- uv package manager
- Internet access for API requests
- Claude Desktop (for using MCP)

---

## 📊 API Endpoints

### Jira REST API v3

| Operation | Endpoint | Method | Parameters |
|----------|----------|--------|-----------|
| Search issues | `/rest/api/3/search/jql` | POST | jql, maxResults, fields |
| Get issue | `/rest/api/3/issue/{issueKey}` | GET | - |
| Create issue | `/rest/api/3/issue` | POST | project, summary, issuetype, description |
| Update issue | `/rest/api/3/issue/{issueKey}` | PUT | fields |
| Add comment | `/rest/api/3/issue/{issueKey}/comment` | POST | body |
| Get transitions | `/rest/api/3/issue/{issueKey}/transitions` | GET | - |
| Change status | `/rest/api/3/issue/{issueKey}/transitions` | POST | transition |

### Confluence REST API v1

| Operation | Endpoint | Method | Parameters |
|----------|----------|--------|-----------|
| Search pages | `/wiki/rest/api/content/search` | GET | cql, limit, expand |
| Get page | `/wiki/rest/api/content/{id}` | GET | expand |
| Create page | `/wiki/rest/api/content` | POST | type, title, space, body, ancestors |
| Update page | `/wiki/rest/api/content/{id}` | PUT | version, title, type, body |

---

## 🛠️ MCP Tools

### Jira Tools

#### 1. jira_search
**Description:** Search Jira issues by JQL query

**Parameters:**
```typescript
{
  jql: string,           // JQL query
  max_results?: number,  // Max results (default: 50)
  offset?: number        // Pagination offset (default: 0)
}
```

**Example:**
```
jql: "project = MYPROJ AND status = Open"
max_results: 20
```

**Returned fields:**
- summary (title)
- status (status)
- assignee (assignee)
- reporter (reporter)
- priority (priority)
- created (creation date)
- updated (update date)
- description (description)

#### 2. jira_get_issue
**Description:** Get detailed information about a Jira issue with optional field filtering

**Parameters:**
```typescript
{
  issue_key: string,           // Issue key (e.g., "PROJ-123")
  fields?: string[]            // Optional: List of fields to return
                               // Omit for default essential fields
                               // Use ["*all"] for all fields (may exceed token limits)
}
```

**Default Essential Fields (when fields parameter is omitted):**
- key, summary, description, status, priority
- assignee, reporter, created, updated, resolutiondate
- issuetype, parent, subtasks, issuelinks, labels
- fixVersions, components

**Response Size:**
- Default fields: ~5-18k tokens (safe for MCP 25k limit)
- All fields `["*all"]`: 10k-100k+ tokens (may exceed limits for large issues)

**Returns:** Issue data with specified fields in JSON format

**Best Practices:**
- Use default fields for most operations (reduces response by ~80%)
- For large issues with many comments, use `jira_get_issue_comments` separately
- Request specific fields when you need only certain data
- Avoid `["*all"]` unless you specifically need custom fields or full history

**Example:**
```json
// Get essential fields only (recommended)
{
  "issue_key": "PROJ-1157"
}

// Get specific fields
{
  "issue_key": "PROJ-1157",
  "fields": ["key", "summary", "status", "assignee"]
}

// Get all fields (use with caution)
{
  "issue_key": "PROJ-1157",
  "fields": ["*all"]
}
```

#### 3. jira_get_issue_comments
**Description:** Get comments for a Jira issue with pagination

**Parameters:**
```typescript
{
  issue_key: string,       // Issue key (e.g., "PROJ-123")
  max_results?: number,    // Maximum comments to return (1-50, default: 10)
  offset?: number          // Starting index for pagination (default: 0)
}
```

**Returns:** Comments data with pagination info:
```typescript
{
  issue_key: string,
  total: number,           // Total number of comments
  startAt: number,         // Starting index
  maxResults: number,      // Max results returned
  count: number,           // Actual count in this response
  comments: [              // Array of comment objects
    {
      id: string,
      author: string,
      created: string,
      updated: string,
      body: object         // ADF format
    }
  ]
}
```

**Best Practices:**
- Use for issues with many comments (>10)
- Start with 10-20 comments per request
- Use pagination for issues with 50+ comments
- Helps avoid token limits when combined with `jira_get_issue`

**Example:**
```json
// Get first 10 comments
{
  "issue_key": "PROJ-1157"
}

// Get next 20 comments
{
  "issue_key": "PROJ-1157",
  "max_results": 20,
  "offset": 20
}
```

#### 4. jira_create_issue
**Description:** Create a new issue

**Parameters:**
```typescript
{
  project_key: string,    // Project key
  summary: string,        // Issue title
  issue_type?: string,    // Type (default: "Task")
  description?: string    // Description (optional)
}
```

**Issue types:**
- Task
- Bug
- Story
- Epic
- Subtask

#### 5. jira_add_comment
**Description:** Add a comment to an issue

**Parameters:**
```typescript
{
  issue_key: string,  // Issue key
  comment: string     // Comment text
}
```

#### 6. jira_get_transitions
**Description:** Get available status transitions

**Parameters:**
```typescript
{
  issue_key: string  // Issue key
}
```

**Returns:** List of available transitions with IDs

#### 7. jira_transition
**Description:** Change issue status

**Parameters:**
```typescript
{
  issue_key: string,     // Issue key
  transition_id: string  // Transition ID
}
```

**Note:** First get transition_id via `jira_get_transitions`

### Confluence Tools

#### 7. confluence_search
**Description:** Search pages by CQL query

**Parameters:**
```typescript
{
  cql: string,      // CQL query
  limit?: number,   // Max results (default: 25)
  offset?: number   // Pagination offset (default: 0)
}
```

**CQL examples:**
```
space = DOCS AND type = page
title ~ "API" AND space = DEV
lastModified > now("-7d")
```

#### 8. confluence_get_page
**Description:** Get page content

**Parameters:**
```typescript
{
  page_id: string  // Page ID
}
```

**Returns:** Complete page content with metadata

#### 9. confluence_create_page
**Description:** Create a new page

**Parameters:**
```typescript
{
  space_key: string,   // Space key
  title: string,       // Page title
  body: string,        // Content (HTML/Storage format)
  parent_id?: string   // Parent page ID (optional)
}
```

**Body format:** Confluence Storage Format (HTML-like)

#### 10. confluence_update_page
**Description:** Update an existing page

**Parameters:**
```typescript
{
  page_id: string,  // Page ID
  title: string,    // New title
  body: string      // New content
}
```

**Note:** Version is automatically fetched and incremented

---

## 🔐 Security

### Authentication

**Method:** Basic Authentication with API Token

**Format:**
```
Authorization: Basic base64(email:api_token)
```

### Getting an API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Specify a name (e.g., "Claude MCP")
4. Copy the token (shown only once!)

### Credential Storage

**✅ Secure:**
- Environment variables
- `.env` file (added to `.gitignore`)
- Claude Desktop configuration

**❌ Insecure:**
- Storing in code
- Committing to Git
- Sharing in public channels

### Access Rights

API token inherits all rights of the user who created it. Recommendations:
- Use a separate account for automation
- Limit rights at Jira/Confluence project level
- Regularly rotate tokens

---

## 📝 Data Formats

### Jira Issue Description (Atlassian Document Format)

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "Your text here"
        }
      ]
    }
  ]
}
```

### Confluence Storage Format

```html
<p>Simple paragraph</p>
<h2>Heading</h2>
<ul>
  <li>List item</li>
</ul>
<ac:structured-macro ac:name="code">
  <ac:plain-text-body><![CDATA[code here]]></ac:plain-text-body>
</ac:structured-macro>
```

---

## 🚀 Installation and Setup

### Step 1: Clone/create project

```bash
mkdir jira-confluence-mcp
cd jira-confluence-mcp
```

### Step 2: Create structure

Create files according to specification:
- `pyproject.toml`
- `jira_confluence_mcp/__init__.py`
- `jira_confluence_mcp/server.py`
- `jira_confluence_mcp/client.py`
- `jira_confluence_mcp/errors.py`
- `jira_confluence_mcp/formatters.py`
- `README.md`
- `.env.example`
- `.gitignore`

### Step 3: Install dependencies

```bash
# Using uv
uv pip install -e .

# Or directly
uv pip install mcp requests python-dotenv
```

### Step 4: Configure environment variables

```bash
# Create .env file
cp .env.example .env

# Edit .env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-token-here
```

### Step 5: Testing

```bash
# Load environment variables
source .env  # Linux/Mac
# or
set -a; source .env; set +a  # Linux/Mac with export

# Run server
uv run jira-confluence-mcp
```

### Step 6: Claude Desktop integration

**Config path:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Add configuration:**
```json
{
  "mcpServers": {
    "jira-confluence": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/jira-confluence-mcp",
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

**Important:** Specify absolute path to the project!

### Step 7: Restart Claude Desktop

Completely close and reopen Claude Desktop.

---

## 🧪 Testing

See [TESTING.md](./TESTING.md) for comprehensive testing guide.

### Quick connection test

```bash
uv run python test_connection.py
```

### Test your tasks

```bash
uv run python test_my_tasks.py
```

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run jira-confluence-mcp
```

---

## 🐛 Error Handling

### Common errors and solutions

#### 1. Authentication Failed (401)
**Cause:** Invalid email or API token
**Solution:** Check credentials, create new token

#### 2. Not Found (404)
**Cause:** Invalid issue key, page ID, or URL
**Solution:** Verify identifiers

#### 3. Permission Denied (403)
**Cause:** Insufficient access rights
**Solution:** Check user permissions in Jira/Confluence

#### 4. Bad Request (400)
**Cause:** Invalid data format
**Solution:** Check JQL, CQL, or request body format

#### 5. Rate Limit (429)
**Cause:** Request limit exceeded
**Solution:** Add delays between requests

### Logging

All errors are returned in format:
```json
{
  "error": "Error description",
  "details": "API details"
}
```

---

## 📚 Usage Examples

### JQL Query Examples

```python
# All open issues in project
"project = MYPROJ AND status = Open"

# Issues assigned to user
"assignee = currentUser() AND status != Done"

# Recently updated bugs
"type = Bug AND updated > -7d ORDER BY updated DESC"

# Issues without assignee
"project = MYPROJ AND assignee is EMPTY"

# By priority
"project = MYPROJ AND priority in (High, Highest)"
```

### CQL Query Examples

```python
# All pages in space
"space = DOCS AND type = page"

# Search by title
"title ~ 'API' AND space in (DEV, DOCS)"

# Recently modified
"lastModified > now('-7d') AND type = page"

# Created by user
"creator = currentUser()"

# By content text
"text ~ 'authentication' AND space = DOCS"
```

### Creating Confluence page with formatting

```html
<h1>Document title</h1>
<p>Introduction paragraph with <strong>bold</strong> text.</p>

<h2>Section 1</h2>
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>

<h2>Code</h2>
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:plain-text-body><![CDATA[
def hello_world():
    print("Hello, World!")
  ]]></ac:plain-text-body>
</ac:structured-macro>

<h2>Info panel</h2>
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>This is important information!</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

---

## 🔄 Workflow Examples

### Workflow 1: Creating and tracking a bug

```
1. Claude: "Create a bug in project TEST: 'Button not working'"
   → Issue TEST-456 created

2. Claude: "Show details for TEST-456"
   → See status "Open", assignee empty

3. Claude: "Add comment to TEST-456: 'Reproduced on staging'"
   → Comment added

4. Claude: "What statuses are available for TEST-456?"
   → See: Open, In Progress, Done (with IDs)

5. Claude: "Move TEST-456 to In Progress"
   → Use transition_id from step 4
```

### Workflow 2: Documenting in Confluence

```
1. Claude: "Find page about API in DOCS space"
   → Get page_id

2. Claude: "Show content of this page"
   → See current content and version

3. Claude: "Update this page, add section about new endpoint"
   → Use page_id and version+1
```

---

## 🎨 Extensions and Improvements

### Possible improvements (Phase 2)

1. **Additional operations:**
   - File attachments to issues
   - Working with sprints (Jira)
   - Exporting Confluence pages to PDF
   - Getting change history

2. **Optimization:**
   - Caching frequently used data
   - Batch operations for multiple updates
   - Retry mechanism for network errors

3. **Extended functionality:**
   - Working with Jira Workflows
   - Access rights management
   - Notifications and subscriptions
   - Integration with Jira Automation

4. **Resources (MCP):**
   - Providing project list as resources
   - Dynamic update of available Confluence spaces

5. **Prompts (MCP):**
   - Templates for creating issues
   - Templates for reports
   - Ready-made JQL/CQL queries

---

## 📖 References

### Official documentation

1. **Atlassian REST API:**
   - Jira Cloud: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
   - Confluence Cloud: https://developer.atlassian.com/cloud/confluence/rest/v1/

2. **MCP Protocol:**
   - Specification: https://spec.modelcontextprotocol.io/
   - Python SDK: https://github.com/modelcontextprotocol/python-sdk

3. **Authentication:**
   - API Tokens: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/

### Useful links

- JQL Tutorial: https://www.atlassian.com/software/jira/guides/jql
- CQL Tutorial: https://developer.atlassian.com/cloud/confluence/cql/
- Confluence Storage Format: https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html

---

## 📄 License

MIT License - free use and modification

---

## 👥 Support

If you encounter problems:

1. Check credential correctness
2. Ensure access rights in Jira/Confluence
3. Check request format (JQL/CQL)
4. Review official API documentation
5. Check Claude Desktop logs

---

## ✅ Readiness Checklist

- [ ] Python 3.10+ installed
- [ ] uv package manager installed
- [ ] API token obtained
- [ ] All project files created
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Test connection successful
- [ ] Claude Desktop configured
- [ ] First request executed successfully

---

**Specification created:** 2025-11-06
**Version:** 1.0
**Status:** Production Ready
