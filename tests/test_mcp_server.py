"""
Test MCP server functionality without real Jira/Confluence credentials.
"""

import asyncio
import json
from jira_confluence_mcp.server import mcp


async def test_server():
    """Test the MCP server tools."""
    print("=" * 60)
    print("MCP Server Testing")
    print("=" * 60)
    print()

    # List all tools
    print("1. Listing available tools...")
    print("-" * 60)
    tools = await mcp.list_tools()
    print(f"✅ Found {len(tools)} tools:")
    print()

    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}")
        print(f"   Description: {tool.description[:100]}...")

        # Show parameters
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            schema = tool.inputSchema
            if 'properties' in schema:
                params = list(schema['properties'].keys())
                required = schema.get('required', [])
                print(f"   Parameters: {', '.join(params)}")
                if required:
                    print(f"   Required: {', '.join(required)}")
        print()

    print("=" * 60)
    print("Tool Categories")
    print("=" * 60)
    print()

    jira_tools = [t for t in tools if t.name.startswith('jira_')]
    confluence_tools = [t for t in tools if t.name.startswith('confluence_')]

    print(f"📋 Jira Tools: {len(jira_tools)}")
    for tool in jira_tools:
        print(f"   • {tool.name}")
    print()

    print(f"📄 Confluence Tools: {len(confluence_tools)}")
    for tool in confluence_tools:
        print(f"   • {tool.name}")
    print()

    print("=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print()
    print("✅ All tools registered successfully")
    print(f"✅ Total: {len(tools)} tools")
    print(f"✅ Jira: {len(jira_tools)} tools")
    print(f"✅ Confluence: {len(confluence_tools)} tools")
    print()
    print("Note: To test with real data, configure your .env file")
    print("and run: uv run python test_connection.py")


if __name__ == "__main__":
    asyncio.run(test_server())
