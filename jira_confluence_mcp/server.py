"""
MCP Server for Jira and Confluence integration.
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from jira_confluence_mcp.client import JiraConfluenceClient
from jira_confluence_mcp.errors import JiraConfluenceError


# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("Jira-Confluence MCP Server")

# Global client instance
_client: Optional[JiraConfluenceClient] = None


def get_client() -> JiraConfluenceClient:
    """
    Get or create the Jira/Confluence client instance.

    Returns:
        Initialized JiraConfluenceClient

    Raises:
        ValueError: If required environment variables are missing
    """
    global _client

    if _client is None:
        base_url = os.getenv('JIRA_BASE_URL')
        email = os.getenv('JIRA_EMAIL')
        api_token = os.getenv('JIRA_API_TOKEN')
        api_version = os.getenv('JIRA_API_VERSION', '3')  # Default to v3 (Cloud)
        # Confluence path prefix: "/wiki" for Cloud (default), "" for Server/DC
        confluence_path = os.getenv('CONFLUENCE_PATH', '/wiki')

        if not all([base_url, email, api_token]):
            missing = []
            if not base_url:
                missing.append('JIRA_BASE_URL')
            if not email:
                missing.append('JIRA_EMAIL')
            if not api_token:
                missing.append('JIRA_API_TOKEN')

            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please set them in your .env file or environment."
            )

        # Validate API version
        if api_version not in ('2', '3'):
            print(f"Warning: Invalid JIRA_API_VERSION '{api_version}', using '3'", file=sys.stderr)
            api_version = '3'

        _client = JiraConfluenceClient(base_url, email, api_token, api_version, confluence_path)

    return _client


# ===== JIRA TOOLS =====

@mcp.tool()
def jira_search(jql: str, max_results: int = 50, offset: int = 0) -> dict:
    """
    Search for Jira issues using JQL (Jira Query Language).

    Args:
        jql: JQL query string (e.g., "project = PROJ AND status = Open")
        max_results: Maximum number of results to return (1-100, default: 50)
        offset: Starting index for pagination (default: 0)

    Returns:
        Search results with issues and metadata

    Example:
        jira_search("project = TEST AND status = Open", max_results=10)
    """
    try:
        client = get_client()
        result = client.search_jira_issues(jql, max_results, offset)

        # Format results for better readability
        total = result.get('total', 0)
        issues = result.get('issues', [])

        formatted_issues = []
        for issue in issues:
            key = issue.get('key', 'N/A')
            fields = issue.get('fields', {})

            formatted_issues.append({
                'key': key,
                'summary': fields.get('summary', 'N/A'),
                'status': fields.get('status', {}).get('name', 'N/A'),
                'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                'priority': fields.get('priority', {}).get('name', 'N/A') if fields.get('priority') else 'N/A',
                'created': fields.get('created', 'N/A'),
                'updated': fields.get('updated', 'N/A')
            })

        return {
            'total': total,
            'offset': offset,
            'count': len(formatted_issues),
            'issues': formatted_issues
        }

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def jira_get_issue(issue_key: str, fields: Optional[list[str]] = None) -> dict:
    """
    Get detailed information about a Jira issue with optional field filtering.

    By default returns only essential fields to avoid MCP token limits.
    For large issues with extensive comments/attachments, use jira_get_issue_comments separately.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        fields: Optional list of field names to return. Omit for default essential fields.
               Use ["*all"] to get all fields (may exceed token limit for large issues).
               Common fields: key, summary, description, status, priority, assignee,
               reporter, created, updated, issuetype, parent, subtasks, comment, attachment

    Returns:
        Issue data with specified fields. Default fields when omitted:
        key, summary, description, status, priority, assignee, reporter, created,
        updated, resolutiondate, issuetype, parent, subtasks, issuelinks, labels,
        fixVersions, components

    Example:
        # Get essential fields only (recommended for large issues)
        jira_get_issue("PROJ-1157")

        # Get specific fields
        jira_get_issue("PROJ-1157", fields=["key", "summary", "status"])

        # Get all fields (use with caution - may exceed token limits)
        jira_get_issue("PROJ-1157", fields=["*all"])
    """
    try:
        client = get_client()
        return client.get_jira_issue(issue_key, fields=fields)
    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def jira_create_issue(
    project_key: str,
    summary: str,
    issue_type: str = "Task",
    description: str = "",
    fields: Optional[dict] = None,
) -> dict:
    """
    Create a new Jira issue.

    Supports optional extra fields using the same auto-conversion as jira_update_issue:
    - parent: {"key": "PROJ-100"} — required by some projects for epic linking
    - components: ["Component A"] or [{"id": "123"}]
    - labels: ["backend", "bug"]
    - priority: "High" or {"name": "High"}
    - assignee: "user@email.com" or {"accountId": "..."}
    - fixVersions: ["v2.0"] or [{"id": "456"}]
    - Custom fields: {"customfield_11700": ...}

    Args:
        project_key: Project key (e.g., "PROJ")
        summary: Issue title/summary
        issue_type: Issue type - Task, Bug, Story, Epic, or Subtask (default: Task)
        description: Issue description in plain text (automatically converted to ADF)
        fields: Optional extra fields to set on the issue at creation time

    Returns:
        Created issue data with key and ID

    Example:
        jira_create_issue("TEST", "Fix login button", "Bug", "The login button doesn't work")
        jira_create_issue("TEST", "Subtask", "Subtask", fields={"parent": {"key": "TEST-1"}})
    """
    try:
        client = get_client()
        result = client.create_jira_issue(project_key, summary, issue_type, description, fields=fields)

        # Return simplified response
        return {
            'success': True,
            'key': result.get('key'),
            'id': result.get('id'),
            'self': result.get('self')
        }

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def jira_add_comment(issue_key: str, comment: str) -> dict:
    """
    Add a comment to a Jira issue.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        comment: Comment text in plain text (automatically converted to ADF)

    Returns:
        Created comment data

    Example:
        jira_add_comment("TEST-42", "Working on this issue now")
    """
    try:
        client = get_client()
        result = client.add_jira_comment(issue_key, comment)

        return {
            'success': True,
            'id': result.get('id'),
            'created': result.get('created'),
            'author': result.get('author', {}).get('displayName', 'Unknown')
        }

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def jira_get_transitions(issue_key: str) -> dict:
    """
    Get available status transitions for a Jira issue.

    Use this before calling jira_transition to see what status changes are available.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")

    Returns:
        List of available transitions with IDs and names

    Example:
        jira_get_transitions("TEST-42")
    """
    try:
        client = get_client()
        transitions = client.get_jira_transitions(issue_key)

        formatted_transitions = [
            {
                'id': t.get('id'),
                'name': t.get('name'),
                'to_status': t.get('to', {}).get('name', 'Unknown')
            }
            for t in transitions
        ]

        return {
            'issue_key': issue_key,
            'transitions': formatted_transitions
        }

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def jira_transition(issue_key: str, transition_id: str) -> dict:
    """
    Change the status of a Jira issue by applying a transition.

    First use jira_get_transitions to see available transition IDs.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        transition_id: Transition ID from jira_get_transitions

    Returns:
        Success status

    Example:
        # First get transitions
        transitions = jira_get_transitions("TEST-42")
        # Then apply one
        jira_transition("TEST-42", "21")
    """
    try:
        client = get_client()
        client.transition_jira_issue(issue_key, transition_id)

        return {
            'success': True,
            'issue_key': issue_key,
            'message': f'Successfully transitioned issue {issue_key}'
        }

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def jira_get_issue_comments(
    issue_key: str,
    max_results: int = 10,
    offset: int = 0
) -> dict:
    """
    Get comments for a Jira issue with pagination.

    Use this tool to retrieve comments separately from issue details,
    especially useful for large issues to avoid token limits.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        max_results: Maximum comments to return (1-50, default: 10)
        offset: Starting index for pagination (default: 0)

    Returns:
        Comments data with pagination info including:
        - comments: List of comment objects with body, author, created date
        - maxResults: Number of results returned
        - total: Total number of comments on the issue
        - startAt: Starting index of returned comments

    Example:
        # Get first 10 comments
        jira_get_issue_comments("PROJ-1157")

        # Get next 10 comments
        jira_get_issue_comments("PROJ-1157", max_results=10, offset=10)

        # Get up to 50 comments at once
        jira_get_issue_comments("PROJ-1157", max_results=50)
    """
    try:
        client = get_client()
        result = client.get_jira_comments(issue_key, max_results, offset)

        # Format for readability
        comments = result.get('comments', [])
        formatted_comments = []

        for comment in comments:
            formatted_comments.append({
                'id': comment.get('id'),
                'author': comment.get('author', {}).get('displayName', 'Unknown') if comment.get('author') else 'Unknown',
                'created': comment.get('created', 'N/A'),
                'updated': comment.get('updated', 'N/A'),
                'body': comment.get('body', {})
            })

        return {
            'issue_key': issue_key,
            'total': result.get('total', 0),
            'startAt': result.get('startAt', 0),
            'maxResults': result.get('maxResults', 0),
            'count': len(formatted_comments),
            'comments': formatted_comments
        }

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def jira_update_issue(issue_key: str, fields: dict) -> dict:
    """
    Update fields of an existing Jira issue.

    Supports user-friendly field values that are automatically converted:
    - issuetype: "Task" or {"id": "13700"}
    - assignee: "user@email.com" or {"name": "username"}
    - components: ["Component A"] or [{"id": "123"}]
    - priority: "High" or {"name": "High"}
    - labels: ["label1", "label2"]
    - fixVersions: ["v1.0"] or [{"id": "456"}]
    - description: Plain text (auto-converted to ADF for Cloud)

    Args:
        issue_key: Issue key (e.g., "EPMGDVSINT-165")
        fields: Object containing fields to update

    Returns:
        Success status with list of updated fields

    Example:
        # Simple update
        jira_update_issue("PROJ-123", {"summary": "New title"})

        # Complex update with multiple fields
        jira_update_issue("PROJ-123", {
            "issuetype": "Task",
            "assignee": "user@company.com",
            "components": ["Tasks: A.I."],
            "description": "|*Client*:|Company Name|\\n|*Idea*:|Description here|"
        })

        # Update with IDs (if you know them)
        jira_update_issue("PROJ-123", {
            "issuetype": {"id": "13700"},
            "components": [{"id": "108014"}]
        })
    """
    try:
        client = get_client()
        result = client.update_jira_issue(issue_key, fields)
        return result

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


# ===== CONFLUENCE TOOLS =====

@mcp.tool()
def confluence_search(cql: str, limit: int = 25, offset: int = 0) -> dict:
    """
    Search for Confluence pages using CQL (Confluence Query Language).

    Args:
        cql: CQL query string (e.g., "space = DOCS AND type = page")
        limit: Maximum number of results to return (1-100, default: 25)
        offset: Starting index for pagination (default: 0)

    Returns:
        Search results with pages and metadata

    Example:
        confluence_search("space = DOCS AND type = page", limit=10)
    """
    try:
        client = get_client()
        result = client.search_confluence(cql, limit, offset)

        # Format results
        total = result.get('totalSize', 0)
        pages = result.get('results', [])

        formatted_pages = []
        for page in pages:
            formatted_pages.append({
                'id': page.get('id'),
                'title': page.get('title'),
                'type': page.get('type'),
                'space': page.get('space', {}).get('key', 'N/A') if page.get('space') else 'N/A',
                'url': page.get('_links', {}).get('webui', 'N/A') if page.get('_links') else 'N/A'
            })

        return {
            'total': total,
            'offset': offset,
            'count': len(formatted_pages),
            'pages': formatted_pages
        }

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def confluence_get_page(page_id: str) -> dict:
    """
    Get a Confluence page with its content and metadata.

    Args:
        page_id: Confluence page ID

    Returns:
        Complete page data including content, version, and metadata

    Example:
        confluence_get_page("123456")
    """
    try:
        client = get_client()
        return client.get_confluence_page(page_id)
    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def confluence_create_page(
    space_key: str,
    title: str,
    body: str,
    parent_id: str = ""
) -> dict:
    """
    Create a new Confluence page.

    Args:
        space_key: Space key (e.g., "DOCS")
        title: Page title
        body: Page content in plain text or HTML (automatically converted to storage format)
        parent_id: Parent page ID for creating a child page (optional)

    Returns:
        Created page data with ID and URL

    Example:
        confluence_create_page("DOCS", "API Guide", "# Overview\\n\\nThis is the API documentation.")
    """
    try:
        client = get_client()
        parent = parent_id if parent_id else None
        result = client.create_confluence_page(space_key, title, body, parent)

        return {
            'success': True,
            'id': result.get('id'),
            'title': result.get('title'),
            'space': result.get('space', {}).get('key', 'N/A'),
            'url': result.get('_links', {}).get('webui', 'N/A') if result.get('_links') else 'N/A'
        }

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def confluence_update_page(page_id: str, title: str, body: str) -> dict:
    """
    Update an existing Confluence page.

    The current version is automatically fetched, so you don't need to provide it.

    Args:
        page_id: Page ID to update
        title: New page title
        body: New page content in plain text or HTML (automatically converted to storage format)

    Returns:
        Updated page data

    Example:
        confluence_update_page("123456", "Updated API Guide", "# New Overview\\n\\nUpdated content.")
    """
    try:
        client = get_client()
        result = client.update_confluence_page(page_id, title, body)

        return {
            'success': True,
            'id': result.get('id'),
            'title': result.get('title'),
            'version': result.get('version', {}).get('number', 'N/A'),
            'url': result.get('_links', {}).get('webui', 'N/A') if result.get('_links') else 'N/A'
        }

    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def confluence_get_labels(page_id: str) -> dict:
    """
    Get all labels for a Confluence page.

    Args:
        page_id: Confluence page ID

    Returns:
        List of labels on the page with their IDs and names

    Example:
        confluence_get_labels("5651235408")
    """
    try:
        client = get_client()
        return client.get_confluence_labels(page_id)
    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def confluence_add_labels(page_id: str, labels: list[str]) -> dict:
    """
    Add labels to a Confluence page.

    Args:
        page_id: Confluence page ID (e.g., "5651235408")
        labels: List of label names to add (e.g., ["decision", "architecture"])

    Returns:
        Success status with added labels

    Example:
        confluence_add_labels("5651235408", ["decision", "adk", "architecture"])
    """
    try:
        client = get_client()
        return client.add_confluence_labels(page_id, labels)
    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


@mcp.tool()
def confluence_remove_labels(page_id: str, labels: list[str]) -> dict:
    """
    Remove labels from a Confluence page.

    Args:
        page_id: Confluence page ID (e.g., "5651235408")
        labels: List of label names to remove (e.g., ["draft"])

    Returns:
        Success status with removed labels

    Example:
        confluence_remove_labels("5651235408", ["draft"])
    """
    try:
        client = get_client()
        return client.remove_confluence_labels(page_id, labels)
    except JiraConfluenceError as e:
        return e.to_dict()
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


# ===== SERVER ENTRY POINT =====

def main():
    """
    Main entry point for the MCP server.
    """
    try:
        # Validate environment on startup
        client = get_client()
        api_version = os.getenv('JIRA_API_VERSION', '3')
        confluence_path = os.getenv('CONFLUENCE_PATH', '/wiki')
        print("Jira-Confluence MCP Server starting...", file=sys.stderr)
        print(f"Connected to: {os.getenv('JIRA_BASE_URL')}", file=sys.stderr)
        print(f"Jira API version: v{api_version}", file=sys.stderr)
        print(f"Confluence API path: {confluence_path}/rest/api", file=sys.stderr)
        print("Server ready!", file=sys.stderr)

        # Run the MCP server
        mcp.run()

    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fatal Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
