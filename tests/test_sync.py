import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from n8n_local_sync.api import N8nClient
from n8n_local_sync.normalization import get_canonical_hash
from n8n_local_sync.state import SyncState
from n8n_local_sync.sync import sync_workflows


@pytest.fixture
def temp_dir(tmp_path):
    return str(tmp_path)

@pytest.fixture
def mock_client():
    client = Mock(spec=N8nClient)
    return client

def test_sync_remote_only(temp_dir, mock_client):
    remote_workflows = {
        "1": {"id": "1", "name": "wf1", "nodes": []}
    }
    
    with patch("n8n_local_sync.sync.get_remote_workflows", return_value=remote_workflows), patch("n8n_local_sync.sync.get_local_workflows", return_value={}):
        sync_workflows(mock_client, temp_dir)
            
    assert (Path(temp_dir) / "1-wf1.json").exists()
    state = SyncState(temp_dir)
    assert state.get_last_synced_hash("1") == get_canonical_hash(remote_workflows["1"])

def test_sync_local_modified(temp_dir, mock_client):
    local_data = {"id": "1", "name": "wf1", "nodes": [{"name": "node1"}]}
    remote_data = {"id": "1", "name": "wf1", "nodes": []}
    
    with open(Path(temp_dir) / "1-wf1.json", "w") as f:
        json.dump(local_data, f)
        
    state = SyncState(temp_dir)
    state.update_workflow_hash("1", get_canonical_hash(remote_data))
    
    with patch("n8n_local_sync.sync.get_remote_workflows", return_value={"1": remote_data}), patch("n8n_local_sync.sync.get_local_workflows", return_value={"1": local_data}):
        # Without force, should not overwrite
        sync_workflows(mock_client, temp_dir, force=False)
        with open(Path(temp_dir) / "1-wf1.json", "r") as f:
            assert json.load(f) == local_data
            
        # With force, should overwrite
        sync_workflows(mock_client, temp_dir, force=True)
        with open(Path(temp_dir) / "1-wf1.json", "r") as f:
            assert json.load(f) == remote_data

def test_sync_conflict(temp_dir, mock_client):
    base_data = {"id": "1", "name": "wf1", "nodes": [{"name": "base"}]}
    local_data = {"id": "1", "name": "wf1", "nodes": [{"name": "local"}]}
    remote_data = {"id": "1", "name": "wf1", "nodes": [{"name": "remote"}]}
    
    with open(Path(temp_dir) / "1-wf1.json", "w") as f:
        json.dump(local_data, f)
        
    state = SyncState(temp_dir)
    state.update_workflow_hash("1", get_canonical_hash(base_data))
    
    with patch("n8n_local_sync.sync.get_remote_workflows", return_value={"1": remote_data}), patch("n8n_local_sync.sync.get_local_workflows", return_value={"1": local_data}):
        # Without force, should not overwrite
        sync_workflows(mock_client, temp_dir, force=False)
        with open(Path(temp_dir) / "1-wf1.json", "r") as f:
            assert json.load(f) == local_data
