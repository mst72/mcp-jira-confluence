# MCP Server Fix Specification - Response Size Limit Issue

## Problem Statement

**Error:**
```
MCP tool "jira_get_issue" response (64611 tokens) exceeds maximum allowed tokens (25000)
```

**Issue ID:** PROJ-1157 - "Analytics - Chat Logs (Model Analytics)"

The `jira_get_issue` tool returns responses that can exceed MCP's token limit of 25,000 tokens, causing the tool to fail.

---

## Root Cause Analysis

### Why Response is Too Large

Jira issues can contain:
1. **Large description field** - Can contain extensive documentation, tables, images
2. **Many comments** - Issues with long discussion threads
3. **Large attachments metadata** - Multiple files with full metadata
4. **Extensive custom fields** - Jira has 100+ custom fields per project
5. **Full changelog** - Complete history of all changes
6. **All issue links** - Related issues with full metadata

### Current Implementation Problem

```python
# Current implementation in jira_confluence_mcp/server.py
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "jira_get_issue":
        result = client.get_jira_issue(arguments["issue_key"])
        # Returns ENTIRE response from Jira API without any filtering
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

The current implementation returns the **entire** Jira API response without:
- Field filtering
- Comment limiting
- Attachment limiting
- Changelog exclusion
- Custom field pruning

---

## Solution Specification

### Option 1: Field Filtering (RECOMMENDED)

Add optional field selection to return only essential fields by default.

#### Implementation

```python
def get_jira_issue(
    self,
    issue_key: str,
    fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get a Jira issue with optional field filtering.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        fields: Optional list of fields to return. If None, returns essential fields only.

    Default fields (if not specified):
        - key, summary, description, status, priority, assignee, reporter,
          created, updated, issuetype, parent, subtasks, issuelinks, labels
    """
    if fields is None:
        # Essential fields only (reduces response size by ~80%)
        fields = [
            "key",
            "summary",
            "description",
            "status",
            "priority",
            "assignee",
            "reporter",
            "created",
            "updated",
            "resolutiondate",
            "issuetype",
            "parent",
            "subtasks",
            "issuelinks",
            "labels",
            "fixVersions",
            "components"
        ]

    params = {
        "fields": ",".join(fields)
    }

    response = self.session.get(
        f"{self.base_url}/rest/api/3/issue/{issue_key}",
        params=params
    )
    response.raise_for_status()
    return response.json()
```

#### MCP Tool Registration

```python
server.list_tools()
def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="jira_get_issue",
            description="Get detailed information about a Jira issue with optional field filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Issue key (e.g., 'PROJ-123')"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: List of fields to return. Omit for default essential fields. Use '*all' for all fields (may exceed token limit for large issues)."
                    }
                },
                "required": ["issue_key"]
            }
        ),
        # ... other tools
    ]
```

---

### Option 2: Separate Tools for Comments

Create separate tools for getting issue details and comments.

```python
@server.tool()
async def jira_get_issue_comments(
    issue_key: str,
    max_results: int = 10,
    offset: int = 0
) -> list[types.TextContent]:
    """
    Get comments for a Jira issue with pagination.

    Args:
        issue_key: Issue key
        max_results: Maximum comments to return (default: 10, max: 50)
        offset: Starting index for pagination
    """
    result = client.get_jira_comments(issue_key, max_results, offset)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

Implementation in client:
```python
def get_jira_comments(
    self,
    issue_key: str,
    max_results: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """Get comments for an issue with pagination."""
    params = {
        "maxResults": min(max_results, 50),  # Cap at 50
        "startAt": offset
    }

    response = self.session.get(
        f"{self.base_url}/rest/api/3/issue/{issue_key}/comment",
        params=params
    )
    response.raise_for_status()
    return response.json()
```

---

### Option 3: Response Truncation with Warning

Add automatic truncation when response is too large.

```python
def get_jira_issue_safe(
    self,
    issue_key: str,
    max_tokens: int = 20000  # Safety margin below 25k limit
) -> Dict[str, Any]:
    """
    Get issue with automatic truncation if too large.
    """
    # Get with minimal fields first
    result = self.get_jira_issue(issue_key, fields=ESSENTIAL_FIELDS)

    # Estimate token count (rough: 1 token ≈ 4 characters)
    estimated_tokens = len(json.dumps(result)) // 4

    if estimated_tokens > max_tokens:
        # Remove large fields progressively
        if "description" in result.get("fields", {}):
            desc = result["fields"]["description"]
            result["fields"]["description"] = {
                "truncated": True,
                "preview": str(desc)[:500] + "...",
                "message": "Description truncated due to size"
            }

        if "comment" in result.get("fields", {}):
            comments = result["fields"]["comment"]
            result["fields"]["comment"] = {
                "truncated": True,
                "total": comments.get("total", 0),
                "message": f"Comments truncated. Use jira_get_issue_comments for full comments."
            }

    return result
```

---

## Recommended Implementation Plan

### Phase 1: Quick Fix (Option 1)
1. ✅ Add field filtering to `get_jira_issue()` method
2. ✅ Set default to essential fields only
3. ✅ Update MCP tool schema to include optional `fields` parameter
4. ✅ Update documentation in SPECIFICATION.md

**Timeline:** 1-2 hours
**Impact:** Reduces response size by ~80% for typical issues

### Phase 2: Enhanced Tools (Option 2)
1. Add `jira_get_issue_comments` tool for paginated comments
2. Add `jira_get_issue_changelog` tool if needed
3. Update CLAUDE.md with usage examples

**Timeline:** 2-3 hours
**Impact:** Complete control over response size

### Phase 3: Safety Net (Option 3)
1. Add response size validation
2. Implement automatic truncation with warnings
3. Add token estimation utility

**Timeline:** 2-3 hours
**Impact:** Prevents future failures

---

## Testing Plan

### Test Cases

```python
# Test 1: Normal issue (should work)
def test_small_issue():
    result = client.get_jira_issue("PROJ-1930")
    assert len(json.dumps(result)) < 100000  # ~25k tokens

# Test 2: Large issue with default fields (should work)
def test_large_issue_default_fields():
    result = client.get_jira_issue("PROJ-1157")  # The problematic issue
    assert len(json.dumps(result)) < 100000

# Test 3: Large issue with all fields (may fail, should handle gracefully)
def test_large_issue_all_fields():
    try:
        result = client.get_jira_issue("PROJ-1157", fields=["*all"])
        # Should either work or raise clear error
        assert True
    except Exception as e:
        assert "too large" in str(e).lower()

# Test 4: Comments pagination
def test_comments_pagination():
    result = client.get_jira_comments("PROJ-1157", max_results=5, offset=0)
    assert result["maxResults"] == 5
    assert "comments" in result
```

### Manual Testing

```bash
# Test with MCP Inspector
npm run inspector

# Then try:
# 1. Get issue with default fields (should work)
{
  "issue_key": "PROJ-1157"
}

# 2. Get issue with specific fields
{
  "issue_key": "PROJ-1157",
  "fields": ["key", "summary", "status", "assignee"]
}

# 3. Get comments separately
{
  "issue_key": "PROJ-1157",
  "max_results": 10,
  "offset": 0
}
```

---

## Code Changes Required

### File: `jira_confluence_mcp/client.py`

```python
# Add to JiraConfluenceClient class

def get_jira_issue(
    self,
    issue_key: str,
    fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a Jira issue.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        fields: Optional list of fields to return. If None, returns essential fields.
                Use "*all" to get all fields (may be very large).

    Returns:
        Complete issue data including specified fields

    Example:
        # Get essential fields only
        issue = client.get_jira_issue("PROJ-1157")

        # Get specific fields
        issue = client.get_jira_issue("PROJ-1157",
                                      fields=["key", "summary", "status"])

        # Get all fields (use with caution)
        issue = client.get_jira_issue("PROJ-1157", fields=["*all"])
    """
    # Default essential fields
    if fields is None:
        fields = [
            "key", "summary", "description", "status", "priority",
            "assignee", "reporter", "created", "updated", "resolutiondate",
            "issuetype", "parent", "subtasks", "issuelinks", "labels",
            "fixVersions", "components"
        ]

    # Build params
    params = {}
    if fields != ["*all"]:
        params["fields"] = ",".join(fields)

    response = self.session.get(
        f"{self.base_url}/rest/api/3/issue/{issue_key}",
        params=params
    )
    response.raise_for_status()
    return response.json()

def get_jira_comments(
    self,
    issue_key: str,
    max_results: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get comments for a Jira issue with pagination.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        max_results: Maximum comments to return (1-50, default 10)
        offset: Starting index for pagination (default 0)

    Returns:
        Comments data with pagination info
    """
    params = {
        "maxResults": min(max(1, max_results), 50),
        "startAt": offset
    }

    response = self.session.get(
        f"{self.base_url}/rest/api/3/issue/{issue_key}/comment",
        params=params
    )
    response.raise_for_status()
    return response.json()
```

### File: `jira_confluence_mcp/server.py`

```python
# Update tool registration

server.list_tools()
def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="jira_get_issue",
            description="""Get detailed information about a Jira issue.
            By default returns essential fields only.
            For large issues with many comments/attachments, use jira_get_issue_comments separately.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Issue key (e.g., 'PROJ-123')"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": """Optional: List of field names to return.
                        Omit for default essential fields.
                        Use ['*all'] to get all fields (may exceed token limit).
                        Common fields: key, summary, description, status, priority,
                        assignee, reporter, created, updated, issuetype, parent,
                        subtasks, comment, attachment"""
                    }
                },
                "required": ["issue_key"]
            }
        ),
        types.Tool(
            name="jira_get_issue_comments",
            description="Get comments for a Jira issue with pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Issue key (e.g., 'PROJ-123')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum comments to return (1-50, default: 10)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Starting index for pagination (default: 0)",
                        "minimum": 0,
                        "default": 0
                    }
                },
                "required": ["issue_key"]
            }
        ),
        # ... other tools
    ]

# Update call handlers
@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:
    try:
        if name == "jira_get_issue":
            fields = arguments.get("fields")
            result = client.get_jira_issue(
                arguments["issue_key"],
                fields=fields
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "jira_get_issue_comments":
            result = client.get_jira_comments(
                arguments["issue_key"],
                max_results=arguments.get("max_results", 10),
                offset=arguments.get("offset", 0)
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        # ... other handlers

    except requests.exceptions.HTTPError as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"HTTP {e.response.status_code}",
                "message": str(e),
                "details": e.response.text
            }, indent=2)
        )]
```

---

## Documentation Updates

### Update CLAUDE.md

Add section:

```markdown
## Response Size Optimization

### Issue Details

By default, `jira_get_issue` returns only essential fields to avoid token limits:
- key, summary, description, status, priority
- assignee, reporter, created, updated
- issuetype, parent, subtasks, issuelinks, labels

For large issues with extensive comments/attachments, use separate tools:
- `jira_get_issue` - Core issue data
- `jira_get_issue_comments` - Comments with pagination

### Examples

```python
# Get essential fields (recommended)
issue = jira_get_issue(issue_key="PROJ-1157")

# Get specific fields
issue = jira_get_issue(
    issue_key="PROJ-1157",
    fields=["key", "summary", "status", "assignee"]
)

# Get comments separately
comments = jira_get_issue_comments(
    issue_key="PROJ-1157",
    max_results=20,
    offset=0
)
```
```

### Update SPECIFICATION.md

Update jira_get_issue specification:

```markdown
### jira_get_issue

Get detailed information about a Jira issue.

**Endpoint:** `GET /rest/api/3/issue/{issueKey}`

**Parameters:**
- `issue_key` (string, required) - Issue key (e.g., "PROJ-123")
- `fields` (array of strings, optional) - List of fields to return
  - Default: Essential fields only (key, summary, description, status, etc.)
  - Use `["*all"]` for all fields (may exceed token limits for large issues)

**Response Size:**
- Default (essential fields): ~5-15k tokens
- All fields: 10k-100k+ tokens (may exceed MCP limits)

**Best Practices:**
- Use default fields for most operations
- For large issues, get comments separately with `jira_get_issue_comments`
- Request specific fields when you need only certain data

**Example:**
```json
{
  "issue_key": "PROJ-1157",
  "fields": ["key", "summary", "status"]
}
```
```

---

## Migration Guide for Users

If users have existing code using `jira_get_issue`, it will continue to work but will now return only essential fields by default.

### Before (returned everything):
```python
# Returned all fields including huge description, all comments, all history
issue = jira_get_issue(issue_key="PROJ-1157")
# Could fail with token limit error
```

### After (returns essential fields):
```python
# Returns essential fields only (safe)
issue = jira_get_issue(issue_key="PROJ-1157")

# To get all fields (opt-in)
issue = jira_get_issue(issue_key="PROJ-1157", fields=["*all"])

# To get specific fields
issue = jira_get_issue(
    issue_key="PROJ-1157",
    fields=["key", "summary", "status", "assignee"]
)

# To get comments separately
comments = jira_get_issue_comments(
    issue_key="PROJ-1157",
    max_results=10,
    offset=0
)
```

---

## Success Criteria

✅ **Phase 1 Complete When:**
- `jira_get_issue("PROJ-1157")` returns successfully without token limit error
- Default response size < 20k tokens for typical issues
- All existing tests pass
- Documentation updated

✅ **Phase 2 Complete When:**
- `jira_get_issue_comments` tool available and working
- Can retrieve comments for large issues in chunks
- Examples in documentation

✅ **Phase 3 Complete When:**
- Automatic size validation in place
- Clear error messages when response too large
- Token estimation utility available

---

## Rollout Plan

1. **Dev Environment Testing** (Day 1)
   - Implement Phase 1 changes
   - Test with problematic issue PROJ-1157
   - Verify reduced response size

2. **Integration Testing** (Day 2)
   - Test with Claude Desktop
   - Test with MCP Inspector
   - Verify backward compatibility

3. **Documentation** (Day 2)
   - Update CLAUDE.md, SPECIFICATION.md
   - Add examples to README
   - Update version to 0.2.0

4. **Production Rollout** (Day 3)
   - Deploy to production
   - Monitor for issues
   - Update user communications

---

## Estimated Token Reduction

| Scenario | Before | After | Reduction |
|----------|--------|-------|-----------|
| Small issue (PROJ-1930) | ~8k tokens | ~5k tokens | -37% |
| Medium issue (PROJ-1515) | ~25k tokens | ~12k tokens | -52% |
| Large issue (PROJ-1157) | ~65k tokens | ~18k tokens | -72% |
| Very large issue | 100k+ tokens | ~20k tokens | -80% |

---

*Specification Version: 1.0*
*Date: 2025-11-06*
*Author: Based on error analysis of PROJ-1157*
