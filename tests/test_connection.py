"""
Test connection to Jira and Confluence APIs.

This script validates your credentials and API access.
"""

import os
import sys
from dotenv import load_dotenv
from jira_confluence_mcp.client import JiraConfluenceClient
from jira_confluence_mcp.errors import JiraConfluenceError


def test_connection():
    """Test Jira and Confluence API connections."""
    print("=" * 60)
    print("Jira/Confluence Connection Test")
    print("=" * 60)
    print()

    # Load environment variables
    load_dotenv()

    # Get credentials
    base_url = os.getenv('JIRA_BASE_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')

    # Validate credentials
    if not all([base_url, email, api_token]):
        print("❌ ERROR: Missing required environment variables!")
        print()
        if not base_url:
            print("  - JIRA_BASE_URL is not set")
        if not email:
            print("  - JIRA_EMAIL is not set")
        if not api_token:
            print("  - JIRA_API_TOKEN is not set")
        print()
        print("Please create a .env file with these variables.")
        print("See .env.example for template.")
        sys.exit(1)

    print(f"Base URL: {base_url}")
    print(f"Email: {email}")
    print(f"API Token: {'*' * 20}")
    print()

    # Create client
    try:
        client = JiraConfluenceClient(base_url, email, api_token)
        print("✅ Client created successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        sys.exit(1)

    # Test Jira connection
    print("-" * 60)
    print("Testing Jira API...")
    print("-" * 60)
    try:
        # Use bounded JQL query (required by new API)
        result = client.search_jira_issues("created > -365d order by created DESC", max_results=1)
        total = result.get('total', 0)
        print(f"✅ Jira connection successful!")
        print(f"   Total issues found: {total}")

        if result.get('issues'):
            issue = result['issues'][0]
            print(f"   Latest issue: {issue.get('key')} - {issue.get('fields', {}).get('summary', 'N/A')}")

    except JiraConfluenceError as e:
        print(f"❌ Jira connection failed!")
        print(f"   Error: {e.message}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print()

    # Test Confluence connection
    print("-" * 60)
    print("Testing Confluence API...")
    print("-" * 60)
    try:
        result = client.search_confluence("type=page", limit=1)
        total = result.get('totalSize', 0)
        print(f"✅ Confluence connection successful!")
        print(f"   Total pages found: {total}")

        if result.get('results'):
            page = result['results'][0]
            print(f"   Latest page: {page.get('title', 'N/A')} (ID: {page.get('id', 'N/A')})")

    except JiraConfluenceError as e:
        print(f"❌ Confluence connection failed!")
        print(f"   Error: {e.message}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print()
    print("=" * 60)
    print("Connection test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_connection()
