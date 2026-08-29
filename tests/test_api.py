import pytest
from unittest.mock import Mock, patch
import httpx
from n8n_local_sync.api import N8nClient, N8nAuthError, N8nApiError, N8nConnectionError

@pytest.fixture
def client():
    return N8nClient(base_url="http://localhost:5678", api_key="test-key", timeout=1.0)

def test_auth_error(client):
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch.object(client.client, "request", return_value=mock_response):
        with pytest.raises(N8nAuthError):
            client.get_workflows()

def test_connection_error_retry(client):
    with patch.object(client.client, "request", side_effect=httpx.TimeoutException("timeout")) as mock_req:
        with pytest.raises(N8nConnectionError):
            client.get_workflows()
        assert mock_req.call_count == 3  # Retry logic works

def test_get_workflows_pagination(client):
    mock_response_1 = Mock()
    mock_response_1.status_code = 200
    mock_response_1.json.return_value = {"data": [{"id": "1"}], "nextCursor": "cursor1"}

    mock_response_2 = Mock()
    mock_response_2.status_code = 200
    mock_response_2.json.return_value = {"data": [{"id": "2"}]}

    with patch.object(client.client, "request", side_effect=[mock_response_1, mock_response_2]) as mock_req:
        workflows = client.get_workflows()
        assert len(workflows) == 2
        assert workflows[0]["id"] == "1"
        assert workflows[1]["id"] == "2"
        assert mock_req.call_count == 2
