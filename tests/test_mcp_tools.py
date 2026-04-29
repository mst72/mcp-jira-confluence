"""
Test MCP tools programmatically using the Python SDK.

This script demonstrates how to test MCP server tools
without using Claude Desktop or MCP Inspector.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()


async def test_mcp_server():
    """Test the Jira-Confluence MCP server tools."""

    print("=" * 70)
    print("MCP SERVER TOOL TEST")
    print("=" * 70)
    print()

    # Server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "--directory",
            os.getcwd(),
            "jira-confluence-mcp"
        ],
        env={
            "JIRA_BASE_URL": os.getenv("JIRA_BASE_URL"),
            "JIRA_EMAIL": os.getenv("JIRA_EMAIL"),
            "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN"),
        }
    )

    print("Connecting to MCP server...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                await session.initialize()
                print("✅ Connected to MCP server")
                print()

                # List available tools
                print("-" * 70)
                print("AVAILABLE TOOLS")
                print("-" * 70)
                tools_response = await session.list_tools()

                for i, tool in enumerate(tools_response.tools, 1):
                    print(f"{i}. {tool.name}")
                    if tool.description:
                        # Print first line of description
                        desc = tool.description.split('\n')[0]
                        print(f"   {desc}")

                print()
                print(f"Total tools: {len(tools_response.tools)}")
                print()

                # Test 1: Search Jira issues
                print("-" * 70)
                print("TEST 1: Search Jira Issues (assigned to you)")
                print("-" * 70)

                try:
                    result = await session.call_tool(
                        "jira_search",
                        arguments={
                            "jql": "assignee = currentUser() ORDER BY updated DESC",
                            "max_results": 3
                        }
                    )

                    # Parse result
                    content = result.content[0].text if result.content else "{}"
                    data = json.loads(content)

                    if 'error' in data:
                        print(f"❌ Error: {data['error']}")
                    else:
                        print(f"✅ Found {data.get('total', 0)} issues")
                        print()

                        for issue in data.get('issues', [])[:3]:
                            print(f"  [{issue['key']}] {issue['summary']}")
                            print(f"    Status: {issue['status']} | Priority: {issue['priority']}")
                            print()

                except Exception as e:
                    print(f"❌ Tool call failed: {e}")

                # Test 2: Search Confluence pages
                print("-" * 70)
                print("TEST 2: Search Confluence Pages")
                print("-" * 70)

                try:
                    result = await session.call_tool(
                        "confluence_search",
                        arguments={
                            "cql": "type = page ORDER BY lastModified DESC",
                            "limit": 3
                        }
                    )

                    # Parse result
                    content = result.content[0].text if result.content else "{}"
                    data = json.loads(content)

                    if 'error' in data:
                        print(f"❌ Error: {data['error']}")
                    else:
                        print(f"✅ Found {data.get('total', 0)} pages")
                        print()

                        for page in data.get('pages', [])[:3]:
                            print(f"  [{page['space']}] {page['title']}")
                            print(f"    ID: {page['id']}")
                            print()

                except Exception as e:
                    print(f"❌ Tool call failed: {e}")

                print("-" * 70)
                print("TEST COMPLETED")
                print("-" * 70)

    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
