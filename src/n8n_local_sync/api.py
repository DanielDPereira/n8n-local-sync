from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class N8nApiError(Exception):
    """Base exception for n8n API errors."""

class N8nAuthError(N8nApiError):
    """Exception for authentication errors."""

class N8nConnectionError(N8nApiError):
    """Exception for connection errors."""

class N8nClient:
    """Client for interacting with the n8n REST API."""
    
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.Client(
            headers={"X-N8N-API-KEY": self.api_key},
            timeout=timeout
        )

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.status_code == 401 or response.status_code == 403:
            raise N8nAuthError(f"Authentication failed: {response.status_code} {response.text}")
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise N8nApiError(f"API request failed: {e.response.status_code} {e.response.text}") from e
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException, N8nConnectionError)),
        reraise=True
    )
    def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            return self.client.request(method, url, **kwargs)
        except (httpx.RequestError, httpx.TimeoutException) as e:
            raise N8nConnectionError(f"Connection error: {e!s}") from e

    def get_workflows(self) -> list[dict[str, Any]]:
        """Fetch all workflows from the n8n instance with pagination."""
        url = f"{self.base_url}/api/v1/workflows"
        workflows = []
        params = {"limit": 100}
        
        while True:
            response = self._request_with_retry("GET", url, params=params)
            data = self._handle_response(response)
            
            workflows.extend(data.get("data", []))
            
            next_cursor = data.get("nextCursor")
            if not next_cursor:
                break
            params["cursor"] = next_cursor
            
        return workflows

    def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Fetch a single workflow by ID."""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = self._request_with_retry("GET", url)
        return self._handle_response(response)

    def create_workflow(self, workflow_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new workflow."""
        url = f"{self.base_url}/api/v1/workflows"
        response = self._request_with_retry("POST", url, json=workflow_data)
        return self._handle_response(response)

    def update_workflow(self, workflow_id: str, workflow_data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing workflow."""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = self._request_with_retry("PUT", url, json=workflow_data)
        return self._handle_response(response)

    def close(self):
        """Close the underlying HTTP client."""
        self.client.close()

