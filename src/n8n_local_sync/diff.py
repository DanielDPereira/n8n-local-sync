import json
from pathlib import Path
from typing import Dict, Any, List

from n8n_local_sync.api import N8nClient
from n8n_local_sync.export import clean_workflow_data
import typer

def get_local_workflows(directory_str: str) -> Dict[str, Dict[str, Any]]:
    """Returns a dict of workflow ID -> workflow data from local files."""
    directory = Path(directory_str)
    if not directory.exists() or not directory.is_dir():
        return {}
    
    workflows = {}
    for file_path in directory.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                wf_id = data.get("id")
                if wf_id:
                    workflows[wf_id] = data
        except Exception:
            pass
    return workflows

def get_remote_workflows(client: N8nClient) -> Dict[str, Dict[str, Any]]:
    """Returns a dict of workflow ID -> workflow data from n8n API."""
    try:
        remote_list = client.get_workflows()
    except Exception:
        return {}
    
    workflows = {}
    for meta in remote_list:
        wf_id = meta.get("id")
        if wf_id:
            try:
                full_wf = client.get_workflow(wf_id)
                workflows[wf_id] = clean_workflow_data(full_wf)
            except Exception:
                pass
    return workflows

def show_diff(client: N8nClient, directory_str: str):
    """Compare local and remote workflows."""
    local_wfs = get_local_workflows(directory_str)
    remote_wfs = get_remote_workflows(client)
    
    local_ids = set(local_wfs.keys())
    remote_ids = set(remote_wfs.keys())
    
    only_local = local_ids - remote_ids
    only_remote = remote_ids - local_ids
    both = local_ids.intersection(remote_ids)
    
    diff_found = False
    
    if only_local:
        diff_found = True
        typer.secho("\nWorkflows only in local (need to be imported):", fg=typer.colors.CYAN)
        for wf_id in only_local:
            name = local_wfs[wf_id].get("name", "untitled")
            typer.echo(f"  + {name} (ID: {wf_id})")
            
    if only_remote:
        diff_found = True
        typer.secho("\nWorkflows only in remote (need to be exported):", fg=typer.colors.MAGENTA)
        for wf_id in only_remote:
            name = remote_wfs[wf_id].get("name", "untitled")
            typer.echo(f"  + {name} (ID: {wf_id})")
            
    modified = []
    for wf_id in both:
        local_data = local_wfs[wf_id]
        remote_data = remote_wfs[wf_id]
        
        # Deep compare dicts after normalization
        # Note: Since they are dicts, simple == works well for JSON-like structures
        if local_data != remote_data:
            modified.append(wf_id)
            
    if modified:
        diff_found = True
        typer.secho("\nWorkflows modified (diverged):", fg=typer.colors.YELLOW)
        for wf_id in modified:
            name = local_wfs[wf_id].get("name", "untitled")
            typer.echo(f"  ~ {name} (ID: {wf_id})")
            
    if not diff_found:
        typer.secho("\nLocal and remote workflows are completely synced.", fg=typer.colors.GREEN)
