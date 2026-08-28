import json
import logging
from pathlib import Path
import httpx

from n8n_local_sync.api import N8nClient
from n8n_local_sync.validation import validate_workflow_file

logger = logging.getLogger(__name__)

def import_workflows(client: N8nClient, directory_str: str):
    """
    Read valid workflows from the local directory and import them into n8n.
    """
    directory = Path(directory_str)
    if not directory.exists() or not directory.is_dir():
        print(f"Error: Directory '{directory}' does not exist.")
        return

    # To decide whether to POST (create) or PUT (update), we should get existing IDs
    try:
        existing_wfs = client.get_workflows()
        existing_ids = {wf.get("id") for wf in existing_wfs if "id" in wf}
    except Exception as e:
        print(f"Failed to fetch existing workflows from n8n: {e}")
        return

    imported_count = 0
    for file_path in directory.glob("*.json"):
        is_valid, errors = validate_workflow_file(file_path)
        if not is_valid:
            print(f"Skipping invalid workflow {file_path.name}: {errors}")
            continue
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                wf_data = json.load(f)
        except Exception as e:
            print(f"Failed to read {file_path.name}: {e}")
            continue

        wf_id = wf_data.get("id")
        wf_name = wf_data.get("name", "untitled")
        
        # n8n API strictly rejects any property that isn't in its schema for POST/PUT.
        # We must whitelist the allowed fields.
        allowed_keys = {"name", "nodes", "connections", "settings", "staticData", "pinData", "tags"}
        clean_data = {k: v for k, v in wf_data.items() if k in allowed_keys}
        
        try:
            if wf_id and wf_id in existing_ids:
                print(f"Updating workflow '{wf_name}' (ID: {wf_id})...")
                client.update_workflow(wf_id, clean_data)
            else:
                print(f"Creating new workflow '{wf_name}'...")
                new_wf = client.create_workflow(clean_data)
                print(f"Created with new ID: {new_wf.get('id')}")
            imported_count += 1
        except httpx.HTTPStatusError as e:
            print(f"Failed to import '{wf_name}': {e.response.text}")
        except Exception as e:
            print(f"Failed to import '{wf_name}': {e}")
            
    print(f"Imported {imported_count} workflows successfully.")
