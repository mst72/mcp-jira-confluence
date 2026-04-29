#!/bin/bash

# Test Jira-Confluence MCP Server with MCP Inspector
# Usage: ./test_with_inspector.sh

echo "Starting MCP Inspector for Jira-Confluence server..."
echo ""
echo "This will open a web interface for testing your MCP server."
echo "Press Ctrl+C to stop."
echo ""

# Load environment variables
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token-here"

# Run MCP Inspector
npx @modelcontextprotocol/inspector uv run --directory "$(pwd)" jira-confluence-mcp
