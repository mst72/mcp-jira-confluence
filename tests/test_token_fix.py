"""
Test script to verify the token limit fix for jira_get_issue.
"""

import os
import json
from jira_confluence_mcp.client import JiraConfluenceClient


def estimate_tokens(text: str) -> int:
    """Rough token estimation: 1 token ≈ 4 characters."""
    return len(text) // 4


def test_issue_with_default_fields():
    """Test getting issue with default fields (should be safe)."""
    print("\n" + "="*80)
    print("TEST 1: Get issue PROJ-1157 with DEFAULT fields")
    print("="*80)

    base_url = os.getenv('JIRA_BASE_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')

    if not all([base_url, email, api_token]):
        print("❌ Missing environment variables")
        return False

    client = JiraConfluenceClient(base_url, email, api_token)

    try:
        result = client.get_jira_issue("PROJ-1157")
        result_json = json.dumps(result, indent=2)
        token_count = estimate_tokens(result_json)

        print(f"✅ Success!")
        print(f"   Response size: {len(result_json):,} characters")
        print(f"   Estimated tokens: {token_count:,}")
        print(f"   Token limit: 25,000")
        print(f"   Status: {'✅ SAFE' if token_count < 25000 else '❌ TOO LARGE'}")

        # Show what fields were returned
        if 'fields' in result:
            fields = list(result['fields'].keys())
            print(f"   Fields returned: {len(fields)}")
            print(f"   Sample fields: {', '.join(fields[:5])}...")

        return token_count < 25000

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_issue_with_specific_fields():
    """Test getting issue with specific fields."""
    print("\n" + "="*80)
    print("TEST 2: Get issue PROJ-1157 with SPECIFIC fields")
    print("="*80)

    base_url = os.getenv('JIRA_BASE_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')

    client = JiraConfluenceClient(base_url, email, api_token)

    try:
        result = client.get_jira_issue(
            "PROJ-1157",
            fields=["key", "summary", "status", "assignee"]
        )
        result_json = json.dumps(result, indent=2)
        token_count = estimate_tokens(result_json)

        print(f"✅ Success!")
        print(f"   Response size: {len(result_json):,} characters")
        print(f"   Estimated tokens: {token_count:,}")
        print(f"   Status: {'✅ SAFE' if token_count < 25000 else '❌ TOO LARGE'}")

        return token_count < 25000

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_comments():
    """Test getting comments separately."""
    print("\n" + "="*80)
    print("TEST 3: Get comments for PROJ-1157")
    print("="*80)

    base_url = os.getenv('JIRA_BASE_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')

    client = JiraConfluenceClient(base_url, email, api_token)

    try:
        result = client.get_jira_comments("PROJ-1157", max_results=10, offset=0)
        result_json = json.dumps(result, indent=2)
        token_count = estimate_tokens(result_json)

        print(f"✅ Success!")
        print(f"   Total comments: {result.get('total', 0)}")
        print(f"   Comments in response: {len(result.get('comments', []))}")
        print(f"   Response size: {len(result_json):,} characters")
        print(f"   Estimated tokens: {token_count:,}")
        print(f"   Status: {'✅ SAFE' if token_count < 25000 else '❌ TOO LARGE'}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("TESTING TOKEN LIMIT FIX FOR JIRA_GET_ISSUE")
    print("="*80)

    results = []

    # Test 1: Default fields
    results.append(("Default fields", test_issue_with_default_fields()))

    # Test 2: Specific fields
    results.append(("Specific fields", test_issue_with_specific_fields()))

    # Test 3: Comments
    results.append(("Get comments", test_get_comments()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)
    print("\n" + ("="*80))
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*80 + "\n")

    return all_passed


if __name__ == "__main__":
    main()
