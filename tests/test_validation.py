import json

import pytest

from n8n_local_sync.validation import validate_workflow_file


@pytest.fixture
def valid_workflow_file(tmp_path):
    data = {
        "nodes": [
            {"id": "1", "name": "Start", "type": "n8n-nodes-base.start"}
        ],
        "connections": {}
    }
    file_path = tmp_path / "valid.json"
    file_path.write_text(json.dumps(data))
    return file_path

@pytest.fixture
def secret_leaked_workflow_file(tmp_path):
    data = {
        "nodes": [
            {
                "id": "2",
                "parameters": {
                    "apiKey": "123456-super-secret-key"
                }
            }
        ],
        "connections": {}
    }
    file_path = tmp_path / "secret.json"
    file_path.write_text(json.dumps(data))
    return file_path

@pytest.fixture
def invalid_structure_file(tmp_path):
    data = {
        "connections": {}
    } # Missing 'nodes'
    file_path = tmp_path / "invalid.json"
    file_path.write_text(json.dumps(data))
    return file_path

def test_valid_workflow(valid_workflow_file):
    is_valid, errors = validate_workflow_file(valid_workflow_file)
    assert is_valid is True
    assert len(errors) == 0

def test_secret_leaked_workflow(secret_leaked_workflow_file):
    is_valid, errors = validate_workflow_file(secret_leaked_workflow_file)
    assert is_valid is False
    assert any("Potential secret found" in e for e in errors)

def test_invalid_structure_file(invalid_structure_file):
    is_valid, errors = validate_workflow_file(invalid_structure_file)
    assert is_valid is False
    assert any("Missing required field" in e for e in errors)
