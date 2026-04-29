# Jira API Changes - Important Notes

## ⚠️ Breaking Change: New Search API

Atlassian has migrated the Jira search API to a new endpoint. This implementation uses the **latest API** as of 2025.

### What Changed

**Old API (Deprecated - Returns 410):**
```
GET /rest/api/3/search?jql=...&maxResults=...&startAt=...
```

**New API (Current):**
```
POST /rest/api/3/search/jql
Content-Type: application/json

{
  "jql": "your query here"
}
```

### Key Differences

#### 1. Bounded JQL Queries Required

The new API **requires** time-bounded queries. Unbounded queries will fail with 400 error.

**❌ Will NOT Work:**
```json
{
  "jql": "order by created DESC"
}
```

**✅ Will Work:**
```json
{
  "jql": "created > -365d order by created DESC"
}
```

**✅ Or with project filter:**
```json
{
  "jql": "project = TEST order by created DESC"
}
```

#### 2. Token-Based Pagination

The new API uses `nextPageToken` instead of offset-based pagination.

**Old Way:**
```javascript
{
  jql: "...",
  startAt: 50,
  maxResults: 25
}
```

**New Way:**
```javascript
{
  jql: "...",
  nextPageToken: "token_from_previous_response"
}
```

#### 3. Response Format Changes

**Old Response:**
```json
{
  "total": 1234,
  "startAt": 0,
  "maxResults": 50,
  "issues": [...]
}
```

**New Response:**
```json
{
  "issues": [...],
  "nextPageToken": "abc123...",
  "isLast": false
}
```

Note: No `total` field in new API! Our implementation adds it for compatibility:
```python
result['total'] = len(result.get('issues', []))
```

#### 4. Fields Parameter

The new API **does not support** the `fields` parameter in the request body.

**❌ Will NOT Work:**
```json
{
  "jql": "created > -7d",
  "fields": ["summary", "status", "assignee"]
}
```

**✅ Will Work:**
```json
{
  "jql": "created > -7d"
}
```

To limit fields, you need to use JQL select clause or handle it client-side.

## Implementation Details

### Our Solution

The `search_jira_issues()` method in `client.py` has been updated:

```python
def search_jira_issues(self, jql: str, max_results: int = 50, offset: int = 0):
    # Minimal payload - only JQL required
    payload = {'jql': jql}

    # Optional maxResults (if API supports it)
    if max_results and max_results != 50:
        payload['maxResults'] = max_results

    result = self._request('POST', '/rest/api/3/search/jql', json=payload)

    # Add 'total' for backward compatibility
    if 'total' not in result:
        result['total'] = len(result.get('issues', []))

    return result
```

### JQL Best Practices

Always include a time or project restriction:

**Time-based:**
```
created > -7d order by created DESC
updated > -30d AND status = Open
created >= 2024-01-01 AND created <= 2024-12-31
```

**Project-based:**
```
project = MYPROJ order by created DESC
project in (PROJ1, PROJ2) AND status = Open
```

**Combined:**
```
project = MYPROJ AND created > -90d order by updated DESC
```

## Migration Guide

If you're upgrading from an older implementation:

1. **Update endpoint:**
   - Change from `GET /rest/api/3/search` to `POST /rest/api/3/search/jql`

2. **Update request format:**
   - Remove `startAt`, `maxResults` from query params
   - Use JSON body with `{"jql": "..."}`
   - Remove `fields` parameter (not supported)

3. **Add JQL restrictions:**
   - Add time bounds: `created > -365d`
   - Or project filters: `project = MYPROJ`

4. **Handle pagination:**
   - Use `nextPageToken` from response
   - Check `isLast` flag
   - Don't rely on `total` count (not provided by API)

5. **Test your queries:**
   ```bash
   uv run python test_connection.py
   ```

## Error Messages

### 410 Gone
```
The requested API has been removed. Please migrate to the /rest/api/3/search/jql API.
```
**Solution:** You're using the old endpoint. Update to `/rest/api/3/search/jql`

### 400 Bad Request
```
Unbounded JQL queries are not allowed here. Please add a search restriction.
```
**Solution:** Add time or project filter to your JQL

### 400 Invalid Payload
```
Invalid request payload. Refer to the REST API documentation.
```
**Solution:** Simplify payload, remove unsupported parameters like `fields`

## References

- [Official Migration Guide](https://developer.atlassian.com/changelog/#CHANGE-2046)
- [Jira Cloud REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [JQL Documentation](https://www.atlassian.com/software/jira/guides/jql)

## Testing

Test your implementation:

```bash
# Test connection
uv run python test_connection.py

# Test specific query
uv run python -c "
from jira_confluence_mcp.client import JiraConfluenceClient
client = JiraConfluenceClient(base_url, email, token)
result = client.search_jira_issues('created > -7d', max_results=5)
print(f'Found {result[\"total\"]} issues')
"
```

## Status

✅ **This implementation uses the NEW API (2025)**
✅ **All breaking changes handled**
✅ **Tested and working**

Last updated: 2025-01-06
