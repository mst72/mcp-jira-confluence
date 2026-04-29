# API Specification: jira_update_issue

## Overview

This specification defines the `jira_update_issue` MCP tool for updating Jira issue fields.

## Use Case: Update PROJ-123

### Current State

```json
{
  "key": "PROJ-123",
  "fields": {
    "issuetype": {
      "id": "3",
      "name": "Task"
    },
    "assignee": null,
    "components": [],
    "description": "Client: Client Company\n\nIdea: Building a proposal for RAI..."
  }
}
```

### Desired State

```json
{
  "key": "PROJ-123",
  "fields": {
    "issuetype": {
      "id": "13700",
      "name": "Task"
    },
    "assignee": {
      "name": "user@company.com"
    },
    "components": [
      {
        "id": "108014",
        "name": "Tasks: A.I."
      }
    ],
    "description": "|*Client*:*|Client Company\n[Pursuit Engagement: SAMPLE - Dynamics 365|https://sample.crm.dynamics.com/main.aspx?appid=sample&pagetype=entityrecord&etn=engagement&id=sample]|\n|*Idea*:*|Building a proposal for RAI (Responsible AI) guardrails. The request is broad and includes several directions:\n* Evaluation framework\n* Chatbot for risk calculation\n* RAI guardrails implementation\n* Open source tooling for building AI security\n* Datasets for testing chatbots|\n|*Origin:*|Volunteered (inside-out): John Doe|\n|*Initial engagement team*|Jane Smith, John Doe|\n|*Business Domain*:*|Sample Industry|\n|*Technology Domain*:*|AI, LLM, RAI (Responsible AI), Guardrails, AI Security|\n|*Success Criteria*:*|_TBD_|\n|*Task involvement reason:*|AI expertise required for RAI guardrails proposal|\n|*Task Contribution Format:*|Extra Mile|\n\n*- Mandatory fields"
  }
}
```

## Jira REST API Reference

### Endpoint

```
PUT /rest/api/2/issue/{issueIdOrKey}
```

### Request Body

```json
{
  "fields": {
    "issuetype": {
      "id": "13700"
    },
    "assignee": {
      "name": "user@company.com"
    },
    "components": [
      {
        "id": "108014"
      }
    ],
    "description": "..."
  }
}
```

### Response

- **204 No Content** — Success
- **400 Bad Request** — Invalid field values
- **403 Forbidden** — No permission to edit
- **404 Not Found** — Issue not found

## MCP Tool Specification

### Tool Name

`jira_update_issue`

### Description

Update fields of an existing Jira issue.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `issue_key` | string | yes | Issue key (e.g., "PROJ-123") |
| `fields` | object | yes | Object containing fields to update |

### Supported Fields

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `summary` | string | `"[Client Company] RAI Guardrails"` | Issue title |
| `description` | string | `"..."` | Supports Jira wiki markup |
| `issuetype` | string or object | `"Task"` or `{"id": "13700"}` | By name or ID |
| `assignee` | string | `"user@company.com"` | User email/username |
| `components` | array | `["Tasks: A.I."]` or `[{"id": "108014"}]` | By name or ID |
| `priority` | string | `"Urgent"` | Priority name |
| `labels` | array | `["ai", "rai"]` | String array |
| `fixVersions` | array | `["v1.0"]` | Version names |

### Example Usage

```python
jira_update_issue(
    issue_key="PROJ-123",
    fields={
        "issuetype": "Task",
        "assignee": "user@company.com",
        "components": ["Tasks: A.I."],
        "description": "|*Client*:*|Client Company|..."
    }
)
```

### Expected Response

**Success:**
```json
{
  "success": true,
  "key": "EPMGDVSINT-165",
  "updated_fields": ["issuetype", "assignee", "components", "description"]
}
```

**Error:**
```json
{
  "success": false,
  "error": "Field 'issuetype' cannot be changed for this issue",
  "status_code": 400
}
```

## Implementation Notes

### Field Resolution

The tool should support both human-readable names and IDs:

1. **Issue Type**: Accept `"Task"` and resolve to `{"id": "13700"}`
2. **Components**: Accept `["Tasks: A.I."]` and resolve to `[{"id": "108014"}]`
3. **Assignee**: Accept email and resolve to username if needed

### Error Handling

- Validate issue exists before update
- Return clear error messages for permission issues
- Handle partial updates (some fields succeed, others fail)

### Permissions

Requires edit permission on the issue. Some fields may require additional permissions:
- `issuetype` — May require project admin in some configurations
- `assignee` — Requires "Assign Issues" permission
