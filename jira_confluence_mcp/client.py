"""
Jira and Confluence REST API client.
"""

import requests
from typing import Dict, Any, Optional, List
from requests.auth import HTTPBasicAuth

from jira_confluence_mcp.errors import handle_api_error, JiraConfluenceError
from jira_confluence_mcp.formatters import plain_text_to_adf, plain_text_to_storage


class JiraConfluenceClient:
    """
    Client for interacting with Atlassian Jira and Confluence REST APIs.

    Supports:
    - Jira Cloud REST API v3 (default, uses ADF format)
    - Jira Cloud/Server REST API v2 (uses plain text/wiki markup)
    - Confluence Cloud REST API v1
    - Basic Authentication with API tokens
    """

    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        api_version: str = "3",
        confluence_path: str = "/wiki"
    ):
        """
        Initialize the Jira/Confluence client.

        Args:
            base_url: Base URL of Atlassian instance (e.g., https://your-domain.atlassian.net)
            email: Account email address
            api_token: API token from Atlassian account settings
            api_version: Jira API version - "2" for Server/older Cloud, "3" for Cloud (default)
            confluence_path: Path prefix for Confluence API - "/wiki" for Cloud, "" for Server/DC
        """
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.api_version = api_version
        self.jira_api_path = f"/rest/api/{api_version}"
        self.confluence_api_path = f"{confluence_path}/rest/api"
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(email, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Atlassian-Token': 'no-check',  # Required for some on-premise servers
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json: JSON body data
            timeout: Request timeout in seconds

        Returns:
            JSON response data

        Raises:
            JiraConfluenceError: On API error
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=timeout
            )

            if not response.ok:
                handle_api_error(response)

            # Handle empty responses
            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

        except requests.exceptions.Timeout:
            raise JiraConfluenceError(f"Request timeout after {timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise JiraConfluenceError(f"Failed to connect to {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise JiraConfluenceError(f"Request failed: {str(e)}")

    # ===== JIRA METHODS =====

    def search_jira_issues(
        self,
        jql: str,
        max_results: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for Jira issues using JQL (Jira Query Language).

        Args:
            jql: JQL query string (e.g., "project = PROJ AND status = Open")
            max_results: Maximum number of results to return (1-100)
            offset: Starting index for pagination

        Returns:
            Search results with issues and metadata

        Example:
            results = client.search_jira_issues("project = TEST", max_results=10)
        """
        fields = [
            'summary', 'status', 'assignee', 'reporter',
            'priority', 'created', 'updated', 'description',
            'issuetype', 'project'
        ]

        if self.api_version == "2":
            # API v2: GET request with query parameters
            params = {
                'jql': jql,
                'maxResults': max_results,
                'startAt': offset,
                'fields': ','.join(fields)
            }
            return self._request('GET', f'{self.jira_api_path}/search', params=params)
        else:
            # API v3: POST request to /search/jql endpoint
            # https://developer.atlassian.com/changelog/#CHANGE-2046
            payload = {
                'jql': jql,
                'fields': fields
            }

            if max_results and max_results != 50:
                payload['maxResults'] = max_results

            result = self._request('POST', f'{self.jira_api_path}/search/jql', json=payload)

            # Add total field for compatibility (new API doesn't have it)
            if 'total' not in result:
                result['total'] = len(result.get('issues', []))

            return result

    def get_jira_issue(
        self,
        issue_key: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a Jira issue with optional field filtering.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            fields: Optional list of fields to return. If None, returns essential fields only.
                   Use ["*all"] to get all fields (may be very large for issues with extensive history).

        Returns:
            Issue data with specified fields

        Default fields (when fields=None):
            key, summary, description, status, priority, assignee, reporter,
            created, updated, resolutiondate, issuetype, parent, subtasks,
            issuelinks, labels, fixVersions, components

        Example:
            # Get essential fields only (recommended for large issues)
            issue = client.get_jira_issue("PROJ-1157")

            # Get specific fields
            issue = client.get_jira_issue("PROJ-1157", fields=["key", "summary", "status"])

            # Get all fields (use with caution - may exceed token limits)
            issue = client.get_jira_issue("PROJ-1157", fields=["*all"])
        """
        # Default essential fields to reduce response size
        if fields is None:
            fields = [
                "key",
                "summary",
                "description",
                "status",
                "priority",
                "assignee",
                "reporter",
                "created",
                "updated",
                "resolutiondate",
                "issuetype",
                "parent",
                "subtasks",
                "issuelinks",
                "labels",
                "fixVersions",
                "components"
            ]

        # Build query parameters
        params = {}
        if fields != ["*all"]:
            params["fields"] = ",".join(fields)

        return self._request('GET', f'{self.jira_api_path}/issue/{issue_key}', params=params)

    def create_jira_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: str = "",
        fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Jira issue.

        Args:
            project_key: Project key (e.g., "PROJ")
            summary: Issue title/summary
            issue_type: Issue type (Task, Bug, Story, Epic, Subtask)
            description: Issue description in plain text (auto-converted to ADF for v3)
            fields: Optional extra fields (parent, components, labels, priority, etc.)
                   Uses the same auto-conversion as update_jira_issue.

        Returns:
            Created issue data with key and ID

        Example:
            issue = client.create_jira_issue(
                "TEST",
                "Fix login button",
                "Bug",
                "The login button doesn't work on mobile",
                fields={"parent": {"key": "PROJ-100"}, "components": ["UI"]}
            )
        """
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type}
            }
        }

        if description:
            if self.api_version == "2":
                # API v2: plain text or wiki markup
                payload["fields"]["description"] = description
            else:
                # API v3: Atlassian Document Format (ADF)
                payload["fields"]["description"] = plain_text_to_adf(description)

        if fields:
            normalized = self._normalize_issue_fields(fields)
            payload["fields"].update(normalized)

        return self._request('POST', f'{self.jira_api_path}/issue', json=payload)

    def update_jira_issue(
        self,
        issue_key: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update fields of a Jira issue.

        Supports user-friendly field values that are automatically normalized:
        - issuetype: "Task" → {"name": "Task"}
        - assignee: "user@email.com" → {"name": "user@email.com"}
        - components: ["A", "B"] → [{"name": "A"}, {"name": "B"}]
        - priority: "High" → {"name": "High"}
        - description: plain text → ADF (v3) or wiki markup (v2)

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            fields: Dictionary of fields to update

        Returns:
            Dict with success status and updated fields list

        Example:
            client.update_jira_issue("TEST-42", {
                "summary": "Updated title",
                "issuetype": "Task",
                "assignee": "user@email.com",
                "components": ["Component A"]
            })
        """
        normalized_fields = self._normalize_issue_fields(fields)
        payload = {"fields": normalized_fields}
        self._request('PUT', f'{self.jira_api_path}/issue/{issue_key}', json=payload)

        return {
            "success": True,
            "key": issue_key,
            "updated_fields": list(fields.keys())
        }

    def _normalize_issue_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize user-friendly field values to Jira API format.

        Args:
            fields: Raw fields dict from user input

        Returns:
            Normalized fields dict ready for Jira API
        """
        normalized = {}

        for field_name, value in fields.items():
            if value is None:
                normalized[field_name] = None
                continue

            # Fields that accept name-based objects
            if field_name == "issuetype":
                normalized[field_name] = self._normalize_name_field(value)

            elif field_name == "priority":
                normalized[field_name] = self._normalize_name_field(value)

            elif field_name == "assignee":
                normalized[field_name] = self._normalize_user_field(value)

            elif field_name == "reporter":
                normalized[field_name] = self._normalize_user_field(value)

            elif field_name == "components":
                normalized[field_name] = self._normalize_array_field(value)

            elif field_name == "fixVersions":
                normalized[field_name] = self._normalize_array_field(value)

            elif field_name == "labels":
                # Labels are just strings, ensure it's a list
                if isinstance(value, str):
                    normalized[field_name] = [value]
                else:
                    normalized[field_name] = value

            elif field_name == "description":
                normalized[field_name] = self._normalize_description(value)

            else:
                # Pass through as-is (summary, custom fields, etc.)
                normalized[field_name] = value

        return normalized

    def _normalize_name_field(self, value: Any) -> Dict[str, Any]:
        """
        Normalize a field that accepts {name: ...} or {id: ...}.

        Args:
            value: String name, or dict with name/id

        Returns:
            Normalized dict with name or id
        """
        if isinstance(value, str):
            return {"name": value}
        elif isinstance(value, dict):
            return value
        return {"name": str(value)}

    def _normalize_user_field(self, value: Any) -> Dict[str, Any]:
        """
        Normalize a user field (assignee, reporter).

        For API v2 (Server/DC): uses "name" field
        For API v3 (Cloud): uses "accountId" field

        Args:
            value: Username/email string, or dict with name/accountId

        Returns:
            Normalized user dict
        """
        if isinstance(value, dict):
            return value

        # For API v2 (Server/Data Center), use "name"
        if self.api_version == "2":
            return {"name": value}
        else:
            # For API v3 (Cloud), if it looks like an accountId use it directly
            # otherwise, it's likely an email and we'd need to resolve it
            # For simplicity, we pass it as-is and let the user provide accountId for Cloud
            if value.startswith("5") or value.startswith("6"):  # accountIds typically start with these
                return {"accountId": value}
            else:
                # This may fail on Cloud - user should provide accountId
                return {"accountId": value}

    def _normalize_array_field(self, value: Any) -> List[Dict[str, Any]]:
        """
        Normalize array fields (components, fixVersions).

        Args:
            value: List of strings/dicts, or single string/dict

        Returns:
            List of normalized dicts with name or id
        """
        if not isinstance(value, list):
            value = [value]

        result = []
        for item in value:
            if isinstance(item, str):
                result.append({"name": item})
            elif isinstance(item, dict):
                result.append(item)
            else:
                result.append({"name": str(item)})

        return result

    def _normalize_description(self, value: Any) -> Any:
        """
        Normalize description field based on API version.

        Args:
            value: Plain text string or ADF/wiki markup

        Returns:
            Formatted description (ADF for v3, plain text for v2)
        """
        if isinstance(value, dict):
            # Already in ADF format
            return value

        if self.api_version == "2":
            # API v2: plain text or wiki markup
            return value
        else:
            # API v3: convert to ADF
            return plain_text_to_adf(value)

    def add_jira_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """
        Add a comment to a Jira issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            comment: Comment text in plain text (auto-converted to ADF for v3)

        Returns:
            Created comment data

        Example:
            client.add_jira_comment("TEST-42", "Working on this now")
        """
        if self.api_version == "2":
            # API v2: plain text or wiki markup
            payload = {"body": comment}
        else:
            # API v3: Atlassian Document Format (ADF)
            payload = {"body": plain_text_to_adf(comment)}

        return self._request('POST', f'{self.jira_api_path}/issue/{issue_key}/comment', json=payload)

    def get_jira_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get available status transitions for a Jira issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")

        Returns:
            List of available transitions with IDs and names

        Example:
            transitions = client.get_jira_transitions("TEST-42")
            # Returns: [{"id": "11", "name": "To Do"}, {"id": "21", "name": "In Progress"}, ...]
        """
        result = self._request('GET', f'{self.jira_api_path}/issue/{issue_key}/transitions')
        return result.get('transitions', [])

    def transition_jira_issue(self, issue_key: str, transition_id: str) -> Dict[str, Any]:
        """
        Change the status of a Jira issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            transition_id: Transition ID (get from get_jira_transitions)

        Returns:
            Empty dict on success

        Example:
            # First get available transitions
            transitions = client.get_jira_transitions("TEST-42")
            # Then apply transition
            client.transition_jira_issue("TEST-42", transitions[0]['id'])
        """
        payload = {"transition": {"id": transition_id}}
        return self._request('POST', f'{self.jira_api_path}/issue/{issue_key}/transitions', json=payload)

    def get_jira_comments(
        self,
        issue_key: str,
        max_results: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get comments for a Jira issue with pagination.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            max_results: Maximum comments to return (1-50, default 10)
            offset: Starting index for pagination (default 0)

        Returns:
            Comments data with pagination info including:
            - comments: List of comment objects
            - maxResults: Number of results returned
            - total: Total number of comments
            - startAt: Starting index

        Example:
            # Get first 10 comments
            comments = client.get_jira_comments("PROJ-1157")

            # Get next 10 comments
            comments = client.get_jira_comments("PROJ-1157", max_results=10, offset=10)

            # Get up to 50 comments
            comments = client.get_jira_comments("PROJ-1157", max_results=50)
        """
        params = {
            "maxResults": min(max(1, max_results), 50),  # Clamp between 1 and 50
            "startAt": max(0, offset)  # Ensure non-negative
        }

        return self._request('GET', f'{self.jira_api_path}/issue/{issue_key}/comment', params=params)

    # ===== CONFLUENCE METHODS =====

    def search_confluence(
        self,
        cql: str,
        limit: int = 25,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for Confluence pages using CQL (Confluence Query Language).

        Args:
            cql: CQL query string (e.g., "space = DOCS AND type = page")
            limit: Maximum number of results to return (1-100)
            offset: Starting index for pagination

        Returns:
            Search results with pages and metadata

        Example:
            results = client.search_confluence("space = DOCS", limit=10)
        """
        params = {
            'cql': cql,
            'limit': limit,
            'start': offset,
            'expand': 'space,history.lastUpdated,version'
        }

        return self._request('GET', f'{self.confluence_api_path}/content/search', params=params)

    def get_confluence_page(self, page_id: str) -> Dict[str, Any]:
        """
        Get a Confluence page with its content.

        Args:
            page_id: Page ID

        Returns:
            Complete page data including content and metadata

        Example:
            page = client.get_confluence_page("123456")
        """
        params = {'expand': 'body.storage,version,space'}
        return self._request('GET', f'{self.confluence_api_path}/content/{page_id}', params=params)

    def create_confluence_page(
        self,
        space_key: str,
        title: str,
        body: str,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Confluence page.

        Args:
            space_key: Space key (e.g., "DOCS")
            title: Page title
            body: Page content in plain text or HTML (auto-converted to storage format)
            parent_id: Parent page ID (optional)

        Returns:
            Created page data with ID

        Example:
            page = client.create_confluence_page(
                "DOCS",
                "API Documentation",
                "# Overview\\n\\nThis is the API documentation."
            )
        """
        # Convert plain text to storage format if needed
        if not body.strip().startswith('<'):
            body_storage = plain_text_to_storage(body)
        else:
            body_storage = body

        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": body_storage,
                    "representation": "storage"
                }
            }
        }

        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]

        return self._request('POST', f'{self.confluence_api_path}/content', json=payload)

    def update_confluence_page(
        self,
        page_id: str,
        title: str,
        body: str,
        version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update an existing Confluence page.

        Auto-fetches current version if not provided.

        Args:
            page_id: Page ID to update
            title: New page title
            body: New page content in plain text or HTML (auto-converted to storage format)
            version: Current version number (auto-fetched if not provided)

        Returns:
            Updated page data

        Example:
            page = client.update_confluence_page(
                "123456",
                "Updated API Documentation",
                "# New Overview\\n\\nUpdated content."
            )
        """
        # Auto-fetch version if not provided
        if version is None:
            current_page = self.get_confluence_page(page_id)
            version = current_page.get('version', {}).get('number', 1)

        # Convert plain text to storage format if needed
        if not body.strip().startswith('<'):
            body_storage = plain_text_to_storage(body)
        else:
            body_storage = body

        payload = {
            "version": {"number": version + 1},
            "title": title,
            "type": "page",
            "body": {
                "storage": {
                    "value": body_storage,
                    "representation": "storage"
                }
            }
        }

        return self._request('PUT', f'{self.confluence_api_path}/content/{page_id}', json=payload)

    def get_confluence_labels(self, page_id: str) -> Dict[str, Any]:
        """
        Get all labels for a Confluence page.

        Args:
            page_id: Confluence page ID

        Returns:
            Dict with page_id and list of labels

        Example:
            labels = client.get_confluence_labels("123456")
        """
        result = self._request('GET', f'{self.confluence_api_path}/content/{page_id}/label')
        return {
            "page_id": page_id,
            "labels": result.get("results", [])
        }

    def add_confluence_labels(self, page_id: str, labels: List[str]) -> Dict[str, Any]:
        """
        Add labels to a Confluence page.

        Args:
            page_id: Confluence page ID
            labels: List of label names to add

        Returns:
            Dict with success status and added labels

        Example:
            client.add_confluence_labels("123456", ["decision", "architecture"])
        """
        payload = [{"name": label} for label in labels]
        self._request('POST', f'{self.confluence_api_path}/content/{page_id}/label', json=payload)

        return {
            "success": True,
            "page_id": page_id,
            "labels": labels
        }

    def remove_confluence_labels(self, page_id: str, labels: List[str]) -> Dict[str, Any]:
        """
        Remove labels from a Confluence page.

        Args:
            page_id: Confluence page ID
            labels: List of label names to remove

        Returns:
            Dict with success status and removed labels

        Example:
            client.remove_confluence_labels("123456", ["draft"])
        """
        for label in labels:
            try:
                self._request('DELETE', f'{self.confluence_api_path}/content/{page_id}/label/{label}')
            except JiraConfluenceError as e:
                # Ignore 404 - label might not exist
                if "404" not in str(e):
                    raise

        return {
            "success": True,
            "page_id": page_id,
            "removed": labels
        }
