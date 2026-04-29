"""
Test script to get your assigned Jira issues and recently modified Confluence pages.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jira_confluence_mcp.client import JiraConfluenceClient
from jira_confluence_mcp.errors import JiraConfluenceError

# Load environment variables
load_dotenv()

# Create client
base_url = os.getenv('JIRA_BASE_URL')
email = os.getenv('JIRA_EMAIL')
api_token = os.getenv('JIRA_API_TOKEN')

client = JiraConfluenceClient(base_url, email, api_token)

print("=" * 80)
print("YOUR ASSIGNED JIRA ISSUES")
print("=" * 80)
print()

try:
    # Search for issues assigned to current user
    jql = "assignee = currentUser() ORDER BY updated DESC"
    result = client.search_jira_issues(jql, max_results=20)

    total = result.get('total', 0)
    print(f"Total issues assigned to you: {total}")
    print()

    if result.get('issues'):
        for issue in result['issues']:
            key = issue.get('key', 'N/A')
            fields = issue.get('fields', {})
            summary = fields.get('summary', 'N/A')
            status = fields.get('status', {}).get('name', 'N/A')
            priority = fields.get('priority', {}).get('name', 'N/A') if fields.get('priority') else 'N/A'
            updated = fields.get('updated', 'N/A')

            print(f"[{key}] {summary}")
            print(f"  Status: {status} | Priority: {priority}")
            print(f"  Updated: {updated}")
            print()
    else:
        print("No issues found assigned to you.")

except JiraConfluenceError as e:
    print(f"❌ Error: {e.message}")
    if e.status_code:
        print(f"   Status Code: {e.status_code}")

print()
print("=" * 80)
print("CONFLUENCE PAGES YOU MODIFIED YESTERDAY")
print("=" * 80)
print()

try:
    # Calculate yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Search for pages modified by current user yesterday
    # CQL: lastModified >= "YYYY-MM-DD" AND contributor = currentUser()
    cql = f'lastModified >= "{yesterday}" AND contributor = currentUser() ORDER BY lastModified DESC'

    result = client.search_confluence(cql, limit=20)

    total = result.get('totalSize', 0)
    print(f"Total pages modified since {yesterday}: {total}")
    print()

    if result.get('results'):
        for page in result['results']:
            page_id = page.get('id', 'N/A')
            title = page.get('title', 'N/A')
            space = page.get('space', {}).get('key', 'N/A') if page.get('space') else 'N/A'

            # Get last modified date if available
            last_modified = page.get('history', {}).get('lastUpdated', {}).get('when', 'N/A') if page.get('history') else 'N/A'

            # Build URL
            base_wiki_url = base_url.rstrip('/') + '/wiki'
            web_ui = page.get('_links', {}).get('webui', '') if page.get('_links') else ''
            url = base_wiki_url + web_ui if web_ui else 'N/A'

            print(f"[{space}] {title}")
            print(f"  ID: {page_id}")
            print(f"  Last Modified: {last_modified}")
            print(f"  URL: {url}")
            print()
    else:
        print(f"No pages found modified since {yesterday}.")

except JiraConfluenceError as e:
    print(f"❌ Error: {e.message}")
    if e.status_code:
        print(f"   Status Code: {e.status_code}")

print("=" * 80)
