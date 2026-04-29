"""
Entry point for running the MCP server as a module.

Usage:
    python -m jira_confluence_mcp
    or
    uv run python -m jira_confluence_mcp
"""

from jira_confluence_mcp.server import main

if __name__ == "__main__":
    main()
