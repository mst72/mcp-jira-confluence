"""
MCP Server for Atlassian Jira and Confluence REST API integration.

This package provides a Model Context Protocol (MCP) server that enables
Claude Desktop to interact with Jira issues and Confluence pages.
"""

from jira_confluence_mcp.client import JiraConfluenceClient
from jira_confluence_mcp.server import main

__version__ = "0.1.0"
__all__ = ["JiraConfluenceClient", "main"]
