# MCP Confluence: Add Labels Support

## Problem

The current MCP Jira-Confluence tool does not support adding/removing labels on Confluence pages. This is needed to:
- Categorize pages (e.g., `decision` label for ADRs)
- Enable CQL queries like `label = "decision" and space = currentSpace()`
- Automate page organization workflows

## Proposed API

### 1. `confluence_add_labels`

Add one or more labels to a Confluence page.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `page_id` | string | yes | Confluence page ID |
| `labels` | string[] | yes | List of label names to add |

**Example:**
```python
confluence_add_labels("5651235408", ["decision", "adk", "architecture"])
```

**Returns:**
```json
{
  "success": true,
  "page_id": "5651235408",
  "labels": ["decision", "adk", "architecture"]
}
```

### 2. `confluence_remove_labels`

Remove one or more labels from a Confluence page.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `page_id` | string | yes | Confluence page ID |
| `labels` | string[] | yes | List of label names to remove |

**Example:**
```python
confluence_remove_labels("5651235408", ["draft"])
```

### 3. `confluence_get_labels`

Get all labels for a Confluence page.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `page_id` | string | yes | Confluence page ID |

**Returns:**
```json
{
  "page_id": "5651235408",
  "labels": [
    {"name": "decision", "id": "123"},
    {"name": "architecture", "id": "456"}
  ]
}
```

## Confluence REST API Reference

### Add Labels
```
POST /wiki/rest/api/content/{id}/label
Content-Type: application/json

[
  {"name": "label1"},
  {"name": "label2"}
]
```

### Get Labels
```
GET /wiki/rest/api/content/{id}/label
```

### Remove Label
```
DELETE /wiki/rest/api/content/{id}/label/{label}
```

## Implementation Notes

### Python (FastMCP)

```python
@mcp.tool()
async def confluence_add_labels(page_id: str, labels: list[str]) -> dict:
    """
    Add labels to a Confluence page.

    Args:
        page_id: Confluence page ID (e.g., "5651235408")
        labels: List of label names to add (e.g., ["decision", "architecture"])

    Returns:
        Success status with added labels
    """
    url = f"{base_url}/wiki/rest/api/content/{page_id}/label"
    payload = [{"name": label} for label in labels]

    response = await client.post(url, json=payload)
    response.raise_for_status()

    return {
        "success": True,
        "page_id": page_id,
        "labels": labels
    }


@mcp.tool()
async def confluence_get_labels(page_id: str) -> dict:
    """
    Get all labels for a Confluence page.

    Args:
        page_id: Confluence page ID

    Returns:
        List of labels on the page
    """
    url = f"{base_url}/wiki/rest/api/content/{page_id}/label"

    response = await client.get(url)
    response.raise_for_status()

    data = response.json()
    return {
        "page_id": page_id,
        "labels": data.get("results", [])
    }


@mcp.tool()
async def confluence_remove_labels(page_id: str, labels: list[str]) -> dict:
    """
    Remove labels from a Confluence page.

    Args:
        page_id: Confluence page ID
        labels: List of label names to remove

    Returns:
        Success status
    """
    for label in labels:
        url = f"{base_url}/wiki/rest/api/content/{page_id}/label/{label}"
        response = await client.delete(url)
        # 404 is OK - label might not exist
        if response.status_code not in [200, 204, 404]:
            response.raise_for_status()

    return {
        "success": True,
        "page_id": page_id,
        "removed": labels
    }
```

## Testing

```bash
# Add labels
mcp call confluence_add_labels '{"page_id": "5651235408", "labels": ["decision"]}'

# Get labels
mcp call confluence_get_labels '{"page_id": "5651235408"}'

# Remove labels
mcp call confluence_remove_labels '{"page_id": "5651235408", "labels": ["draft"]}'
```

## Priority

**Medium** - Manual workaround exists (add labels via UI), but automation improves workflow efficiency.
