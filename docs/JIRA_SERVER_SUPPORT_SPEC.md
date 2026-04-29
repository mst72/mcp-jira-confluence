# Specification: Jira Server/Data Center Support

## Overview

The current `jira-confluence-mcp` server only supports **Jira Cloud** (REST API v3). This specification describes the changes required to add support for **Jira Server/Data Center** (REST API v2).

## Problem Statement

| Aspect | Jira Cloud | Jira Server/Data Center |
|--------|------------|-------------------------|
| API Version | REST API v3 | REST API v2 |
| Base Path | `/rest/api/3/` | `/rest/api/2/` |
| Search Endpoint | `POST /rest/api/3/search/jql` | `GET /rest/api/2/search` |
| Description Format | ADF (Atlassian Document Format) | Plain text / Wiki markup |
| Comment Format | ADF | Plain text / Wiki markup |
| Authentication | API Token + Email | API Token or Username + Password |

**Current Error:**
```
HTTP Status 404 – Not Found
The requested resource [/rest/api/3/search/jql] is not available
```

---

## Proposed Solution

### 1. Add Configuration Parameter

Add a new environment variable `JIRA_API_VERSION` to specify the API version:

```
JIRA_API_VERSION=2   # For Jira Server/Data Center
JIRA_API_VERSION=3   # For Jira Cloud (default)
```

**Alternative:** Auto-detect based on server response or URL pattern.

### 2. API Endpoint Changes

#### 2.1 Search Issues

| API v3 (Cloud) | API v2 (Server) |
|----------------|-----------------|
| `POST /rest/api/3/search/jql` | `GET /rest/api/2/search` |
| Body: `{"jql": "...", "maxResults": 50}` | Query params: `?jql=...&maxResults=50` |

**Code Change in `client.py:95-137`:**

```python
def search_jira_issues(self, jql: str, max_results: int = 50, offset: int = 0) -> Dict[str, Any]:
    if self.api_version == 2:
        # Jira Server/Data Center
        params = {
            'jql': jql,
            'maxResults': max_results,
            'startAt': offset,
            'fields': 'summary,status,assignee,reporter,priority,created,updated,description,issuetype,project'
        }
        return self._request('GET', '/rest/api/2/search', params=params)
    else:
        # Jira Cloud (existing implementation)
        payload = {
            'jql': jql,
            'fields': ['summary', 'status', 'assignee', ...],
            'maxResults': max_results
        }
        return self._request('POST', '/rest/api/3/search/jql', json=payload)
```

#### 2.2 Get Issue

| API v3 (Cloud) | API v2 (Server) |
|----------------|-----------------|
| `GET /rest/api/3/issue/{key}` | `GET /rest/api/2/issue/{key}` |

**Code Change in `client.py:139-197`:**

```python
def get_jira_issue(self, issue_key: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
    api_path = f'/rest/api/{self.api_version}/issue/{issue_key}'
    return self._request('GET', api_path, params=params)
```

#### 2.3 Create Issue

| API v3 (Cloud) | API v2 (Server) |
|----------------|-----------------|
| `POST /rest/api/3/issue` | `POST /rest/api/2/issue` |
| Description: ADF format | Description: Plain text |

**Code Change in `client.py:199-240`:**

```python
def create_jira_issue(self, project_key: str, summary: str,
                      issue_type: str = "Task", description: str = "") -> Dict[str, Any]:
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type}
        }
    }

    if description:
        if self.api_version == 2:
            # Jira Server - plain text
            payload["fields"]["description"] = description
        else:
            # Jira Cloud - ADF format
            payload["fields"]["description"] = plain_text_to_adf(description)

    return self._request('POST', f'/rest/api/{self.api_version}/issue', json=payload)
```

#### 2.4 Add Comment

| API v3 (Cloud) | API v2 (Server) |
|----------------|-----------------|
| `POST /rest/api/3/issue/{key}/comment` | `POST /rest/api/2/issue/{key}/comment` |
| Body: `{"body": <ADF>}` | Body: `{"body": "plain text"}` |

**Code Change in `client.py:259-277`:**

```python
def add_jira_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
    if self.api_version == 2:
        # Jira Server - plain text
        payload = {"body": comment}
    else:
        # Jira Cloud - ADF format
        payload = {"body": plain_text_to_adf(comment)}

    return self._request('POST', f'/rest/api/{self.api_version}/issue/{issue_key}/comment', json=payload)
```

#### 2.5 Update Issue

| API v3 (Cloud) | API v2 (Server) |
|----------------|-----------------|
| `PUT /rest/api/3/issue/{key}` | `PUT /rest/api/2/issue/{key}` |

**Code Change in `client.py:242-257`:**

```python
def update_jira_issue(self, issue_key: str, **fields) -> Dict[str, Any]:
    payload = {"fields": fields}
    return self._request('PUT', f'/rest/api/{self.api_version}/issue/{issue_key}', json=payload)
```

#### 2.6 Get Transitions

| API v3 (Cloud) | API v2 (Server) |
|----------------|-----------------|
| `GET /rest/api/3/issue/{key}/transitions` | `GET /rest/api/2/issue/{key}/transitions` |

#### 2.7 Execute Transition

| API v3 (Cloud) | API v2 (Server) |
|----------------|-----------------|
| `POST /rest/api/3/issue/{key}/transitions` | `POST /rest/api/2/issue/{key}/transitions` |

#### 2.8 Get Comments

| API v3 (Cloud) | API v2 (Server) |
|----------------|-----------------|
| `GET /rest/api/3/issue/{key}/comment` | `GET /rest/api/2/issue/{key}/comment` |

---

### 3. Client Initialization Changes

**File: `client.py:13-41`**

```python
class JiraConfluenceClient:
    def __init__(self, base_url: str, email: str, api_token: str, api_version: int = 3):
        """
        Initialize the Jira/Confluence client.

        Args:
            base_url: Base URL of Atlassian instance
            email: Account email address (or username for Server)
            api_token: API token or password
            api_version: Jira REST API version (2 for Server, 3 for Cloud)
        """
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.api_version = api_version  # NEW
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(email, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
```

---

### 4. Environment Variables

**Current:**
```
JIRA_BASE_URL=https://your-jira-server.com/
JIRA_EMAIL=user@company.com
JIRA_API_TOKEN=xxx
```

**Proposed (add):**
```
JIRA_API_VERSION=2
```

**File to modify: `server.py` or main entry point**

```python
import os

api_version = int(os.environ.get('JIRA_API_VERSION', '3'))
client = JiraConfluenceClient(
    base_url=os.environ['JIRA_BASE_URL'],
    email=os.environ['JIRA_EMAIL'],
    api_token=os.environ['JIRA_API_TOKEN'],
    api_version=api_version
)
```

---

### 5. Response Format Differences

#### 5.1 Description Field

**API v3 (Cloud) - ADF:**
```json
{
  "description": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [{"type": "text", "text": "Description text"}]
      }
    ]
  }
}
```

**API v2 (Server) - Plain text:**
```json
{
  "description": "Description text"
}
```

**Recommendation:** Add a response normalizer to convert API v2 responses to a common format, or document the differences for consumers.

---

### 6. Files to Modify

| File | Changes |
|------|---------|
| `jira_confluence_mcp/client.py` | Add `api_version` parameter, conditional logic for endpoints and formats |
| `jira_confluence_mcp/server.py` | Read `JIRA_API_VERSION` env var, pass to client |
| `jira_confluence_mcp/formatters.py` | (Optional) Add `adf_to_plain_text()` for response normalization |
| `.mcp.json` (user config) | Add `JIRA_API_VERSION` to env |

---

### 7. Testing Checklist

- [ ] Search issues (JQL query)
- [ ] Get single issue by key
- [ ] Create new issue
- [ ] Update issue fields
- [ ] Add comment to issue
- [ ] Get available transitions
- [ ] Execute transition (change status)
- [ ] Get issue comments
- [ ] Pagination (offset/startAt)

---

### 8. Migration Guide for Users

To use with Jira Server/Data Center, update `.mcp.json`:

```json
{
  "mcpServers": {
    "jira-confluence": {
      "command": "...",
      "args": ["..."],
      "env": {
        "JIRA_BASE_URL": "https://your-jira-server.com/",
        "JIRA_EMAIL": "your_username",
        "JIRA_API_TOKEN": "your_password_or_token",
        "JIRA_API_VERSION": "2"
      }
    }
  }
}
```

---

### 9. Alternative: Auto-Detection

Instead of manual configuration, auto-detect API version:

```python
def _detect_api_version(self) -> int:
    """Try API v3, fall back to v2 if 404."""
    try:
        self._request('GET', '/rest/api/3/serverInfo')
        return 3
    except JiraConfluenceError:
        return 2
```

**Pros:** No user configuration needed
**Cons:** Extra request on init, may have edge cases

---

## Summary

| Priority | Task | Effort |
|----------|------|--------|
| P0 | Add `api_version` to client init | Low |
| P0 | Update search endpoint (v3 POST → v2 GET) | Medium |
| P0 | Update all endpoint paths (`/api/3/` → `/api/{version}/`) | Low |
| P1 | Handle description format (ADF vs plain text) | Medium |
| P1 | Handle comment format (ADF vs plain text) | Medium |
| P2 | Add response normalization | Medium |
| P2 | Add auto-detection | Low |
| P2 | Update documentation | Low |

**Estimated total effort:** 2-4 hours
