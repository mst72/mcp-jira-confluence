"""
Test script to see raw API responses.
"""

import os
import json
from dotenv import load_dotenv
from jira_confluence_mcp.client import JiraConfluenceClient

# Load environment variables
load_dotenv()

# Create client
base_url = os.getenv('JIRA_BASE_URL')
email = os.getenv('JIRA_EMAIL')
api_token = os.getenv('JIRA_API_TOKEN')

client = JiraConfluenceClient(base_url, email, api_token)

print("=" * 80)
print("RAW JIRA API RESPONSE")
print("=" * 80)
print()

# Get just one issue
jql = "assignee = currentUser() ORDER BY updated DESC"
result = client.search_jira_issues(jql, max_results=1)

print(f"Total issues: {result.get('total', 0)}")
print()
print("First issue structure:")
if result.get('issues'):
    print(json.dumps(result['issues'][0], indent=2, default=str))
else:
    print("No issues found")

print()
print("=" * 80)
print("RAW CONFLUENCE API RESPONSE")
print("=" * 80)
print()

# Get just one page
cql = 'contributor = currentUser() ORDER BY lastModified DESC'
result = client.search_confluence(cql, limit=1)

print(f"Total pages: {result.get('totalSize', 0)}")
print()
print("First page structure:")
if result.get('results'):
    print(json.dumps(result['results'][0], indent=2, default=str))
else:
    print("No pages found")
