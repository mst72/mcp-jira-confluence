# jira_create_issue: Support arbitrary fields (parent, components, labels, etc.)

## Problem

`jira_create_issue` only accepts 4 hardcoded parameters: `project_key`, `summary`, `issue_type`, `description`. Many Jira projects require additional fields on creation (e.g., `parent` for epic linking), causing the API to reject the request:

```
Bad request: Field Parent is required.
```

**Workaround today:** create the issue manually in Jira UI, then use `jira_update_issue` (which supports arbitrary fields) to fill in the description. This defeats the purpose of having an MCP tool.

## Root Cause

In `server.py:164-200`, `jira_create_issue` has a fixed signature. In `client.py:250-266`, the payload is built from only `project`, `summary`, `issuetype`, and `description` — no way to pass additional fields.

Meanwhile, `jira_update_issue` (`server.py:378`) already accepts a flexible `fields: dict` parameter with auto-conversion for common field types.

## Proposed Fix

### server.py

Add an optional `fields: dict = None` parameter to `jira_create_issue`, reusing the same field-conversion logic from `jira_update_issue`:

```python
@mcp.tool()
def jira_create_issue(
    project_key: str,
    summary: str,
    issue_type: str = "Task",
    description: str = "",
    fields: dict | None = None,    # <-- NEW
) -> dict:
```

### client.py

Merge the extra fields into the payload:

```python
payload = {
    "fields": {
        "project": {"key": project_key},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }
}
if description:
    payload["fields"]["description"] = ...
if fields:
    converted = self._convert_fields(fields)  # reuse update logic
    payload["fields"].update(converted)
```

## Use Cases Unlocked

| Field | Example |
|---|---|
| `parent` | `{"parent": {"key": "PROJ-2105"}}` — required by many projects |
| `components` | `["VO"]` |
| `labels` | `["backend", "bug"]` |
| `priority` | `"High"` |
| `assignee` | `"user@company.com"` |
| `fixVersions` | `["v2.0"]` |
| Custom fields | `{"customfield_11700": ...}` |

## Scope

- ~20 lines changed across `server.py` and `client.py`
- Fully backward-compatible — `fields` is optional
- Reuses existing field-conversion logic from `jira_update_issue` path
