import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from n8n_local_sync.api import N8nClient
from n8n_local_sync.import_ import import_workflows
from n8n_local_sync.normalization import get_canonical_hash
from n8n_local_sync.state import SyncState

@pytest.fixture
def temp_dir(tmp_path):
    return str(tmp_path)

@pytest.fixture
def mock_client():
    return Mock(spec=N8nClient)

def test_import_local_only(temp_dir, mock_client):
    local_data = {"name": "new_wf", "nodes": []}
    
    with open(Path(temp_dir) / "new_wf.json", "w") as f:
        json.dump(local_data, f)
        
    mock_client.create_workflow.return_value = {"id": "99", "name": "new_wf", "createdAt": "now", "updatedAt": "now"}
    
    with patch("n8n_local_sync.import_.get_local_workflows", return_value={"temp_id": local_data}), \
         patch("n8n_local_sync.import_.get_remote_workflows", return_value={}):
         
        import_workflows(mock_client, temp_dir)
        
    # Check that file was renamed/created with new ID
    assert (Path(temp_dir) / "99-new-wf.json").exists()
    
    # Check state was updated
    state = SyncState(temp_dir)
    assert "99" in state.state.get("workflows", {})

def test_import_conflict_no_force(temp_dir, mock_client):
    base_data = {"id": "1", "name": "wf1", "nodes": [{"name": "base"}]}
    local_data = {"id": "1", "name": "wf1", "nodes": [{"name": "local"}]}
    remote_data = {"id": "1", "name": "wf1", "nodes": [{"name": "remote"}]}
    
    state = SyncState(temp_dir)
    state.update_workflow_hash("1", get_canonical_hash(base_data))
    
    with patch("n8n_local_sync.import_.get_local_workflows", return_value={"1": local_data}), \
         patch("n8n_local_sync.import_.get_remote_workflows", return_value={"1": remote_data}):
         
        import_workflows(mock_client, temp_dir, force=False)
        
    # Should not call update_workflow
    mock_client.update_workflow.assert_not_called()

def test_import_conflict_with_force(temp_dir, mock_client):
    base_data = {"id": "1", "name": "wf1", "nodes": [{"name": "base"}]}
    local_data = {"id": "1", "name": "wf1", "nodes": [{"name": "local"}]}
    remote_data = {"id": "1", "name": "wf1", "nodes": [{"name": "remote"}]}
    
    state = SyncState(temp_dir)
    state.update_workflow_hash("1", get_canonical_hash(base_data))
    
    mock_client.update_workflow.return_value = local_data
    
    with patch("n8n_local_sync.import_.get_local_workflows", return_value={"1": local_data}), \
         patch("n8n_local_sync.import_.get_remote_workflows", return_value={"1": remote_data}):
         
        import_workflows(mock_client, temp_dir, force=True)
        
    # Should call update_workflow
    mock_client.update_workflow.assert_called_once()
