import httpx
from typing import List, Dict, Any, Optional

class N8nClient:
    """Client for interacting with the n8n REST API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.Client(
            headers={"X-N8N-API-KEY": self.api_key},
            timeout=30.0
        )

    def get_workflows(self) -> List[Dict[str, Any]]:
        """Fetch all workflows from the n8n instance."""
        url = f"{self.base_url}/api/v1/workflows"
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Fetch a single workflow by ID."""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow."""
        url = f"{self.base_url}/api/v1/workflows"
        response = self.client.post(url, json=workflow_data)
        response.raise_for_status()
        return response.json()

    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workflow."""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = self.client.put(url, json=workflow_data)
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close the underlying HTTP client."""
        self.client.close()
