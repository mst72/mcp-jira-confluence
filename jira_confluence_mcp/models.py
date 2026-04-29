"""
Data models and type definitions for Jira and Confluence operations.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class JiraSearchParams(BaseModel):
    """Parameters for Jira search operation."""
    jql: str = Field(..., description="JQL query string")
    max_results: int = Field(50, description="Maximum number of results to return", ge=1, le=100)
    offset: int = Field(0, description="Offset for pagination", ge=0)


class JiraIssueCreateParams(BaseModel):
    """Parameters for creating a Jira issue."""
    project_key: str = Field(..., description="Project key (e.g., 'PROJ')")
    summary: str = Field(..., description="Issue summary/title")
    issue_type: str = Field("Task", description="Issue type (Task, Bug, Story, etc.)")
    description: str = Field("", description="Issue description in plain text")


class JiraCommentParams(BaseModel):
    """Parameters for adding a comment to Jira issue."""
    issue_key: str = Field(..., description="Issue key (e.g., 'PROJ-123')")
    comment: str = Field(..., description="Comment text")


class JiraTransitionParams(BaseModel):
    """Parameters for transitioning a Jira issue."""
    issue_key: str = Field(..., description="Issue key (e.g., 'PROJ-123')")
    transition_id: str = Field(..., description="Transition ID to apply")


class ConfluenceSearchParams(BaseModel):
    """Parameters for Confluence search operation."""
    cql: str = Field(..., description="CQL query string")
    limit: int = Field(25, description="Maximum number of results to return", ge=1, le=100)
    offset: int = Field(0, description="Offset for pagination", ge=0)


class ConfluencePageCreateParams(BaseModel):
    """Parameters for creating a Confluence page."""
    space_key: str = Field(..., description="Space key (e.g., 'DOCS')")
    title: str = Field(..., description="Page title")
    body: str = Field(..., description="Page content in plain text or HTML")
    parent_id: Optional[str] = Field(None, description="Parent page ID (optional)")


class ConfluencePageUpdateParams(BaseModel):
    """Parameters for updating a Confluence page."""
    page_id: str = Field(..., description="Page ID to update")
    title: str = Field(..., description="New page title")
    body: str = Field(..., description="New page content in plain text or HTML")


class SearchResult(BaseModel):
    """Generic search result wrapper."""
    total: int = Field(..., description="Total number of results")
    results: List[Dict[str, Any]] = Field(..., description="List of results")
    offset: int = Field(0, description="Current offset")
