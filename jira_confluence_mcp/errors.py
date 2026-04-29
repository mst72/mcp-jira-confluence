"""
Error handling for Jira and Confluence API interactions.
"""

import requests
from typing import Optional


class JiraConfluenceError(Exception):
    """Base exception for Jira and Confluence operations."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert error to dictionary format for MCP responses."""
        result = {"error": self.message}
        if self.details:
            result["details"] = self.details
        if self.status_code:
            result["status_code"] = self.status_code
        return result


class AuthenticationError(JiraConfluenceError):
    """Authentication failed (401)."""
    pass


class PermissionError(JiraConfluenceError):
    """Insufficient permissions (403)."""
    pass


class NotFoundError(JiraConfluenceError):
    """Resource not found (404)."""
    pass


class BadRequestError(JiraConfluenceError):
    """Invalid request format (400)."""
    pass


class RateLimitError(JiraConfluenceError):
    """Rate limit exceeded (429)."""
    pass


class ServerError(JiraConfluenceError):
    """Server error (5xx)."""
    pass


def handle_api_error(response: requests.Response) -> None:
    """
    Handle API error responses and raise appropriate exceptions.

    Args:
        response: The HTTP response object

    Raises:
        JiraConfluenceError: Appropriate error based on status code
    """
    try:
        error_data = response.json()
        error_message = error_data.get("errorMessages", [])
        if isinstance(error_message, list) and error_message:
            error_message = "; ".join(error_message)
        elif not error_message:
            error_message = error_data.get("message", response.text)
        details = str(error_data)
    except Exception:
        error_message = response.text or f"HTTP {response.status_code}"
        details = None

    status_code = response.status_code

    if status_code == 401:
        raise AuthenticationError(
            "Authentication failed. Check your email and API token.",
            status_code=status_code,
            details=details
        )
    elif status_code == 403:
        raise PermissionError(
            "Permission denied. You don't have access to this resource.",
            status_code=status_code,
            details=details
        )
    elif status_code == 404:
        raise NotFoundError(
            f"Resource not found: {error_message}",
            status_code=status_code,
            details=details
        )
    elif status_code == 400:
        raise BadRequestError(
            f"Bad request: {error_message}",
            status_code=status_code,
            details=details
        )
    elif status_code == 406:
        raise BadRequestError(
            f"Not Acceptable: Server cannot produce response matching Accept headers. {error_message}",
            status_code=status_code,
            details=details
        )
    elif status_code == 429:
        raise RateLimitError(
            "Rate limit exceeded. Please try again later.",
            status_code=status_code,
            details=details
        )
    elif status_code >= 500:
        raise ServerError(
            f"Server error: {error_message}",
            status_code=status_code,
            details=details
        )
    else:
        raise JiraConfluenceError(
            f"Request failed: {error_message}",
            status_code=status_code,
            details=details
        )
