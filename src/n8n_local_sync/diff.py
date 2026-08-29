import json
from pathlib import Path
from typing import Any, Dict

import typer
from deepdiff import DeepDiff

from n8n_local_sync.api import N8nClient
from n8n_local_sync.normalization import normalize_workflow
from n8n_local_sync.state import SyncState, evaluate_sync_state


def get_local_workflows(directory_str: str) -> Dict[str, Dict[str, Any]]:
    """Returns a dict of workflow ID -> workflow data from local files."""
    directory = Path(directory_str)
    if not directory.exists() or not directory.is_dir():
        return {}
    
    workflows = {}
    for file_path in directory.glob("*.json"):
        if file_path.name.startswith("."):
            continue
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
    except Exception as e:
        typer.secho(f"Error fetching remote workflows: {e}", fg=typer.colors.RED)
        return {}
    
    workflows = {}
    for meta in remote_list:
        wf_id = meta.get("id")
        if wf_id:
            try:
                full_wf = client.get_workflow(wf_id)
                # Keep raw data here, normalize later for hashing/diffing
                workflows[wf_id] = full_wf
            except Exception:
                pass
    return workflows



def print_deep_diff(local_data: dict, remote_data: dict):
    """Print a granular diff between normalized local and remote workflows."""
    norm_local = normalize_workflow(local_data)
    norm_remote = normalize_workflow(remote_data)
    
    diff = DeepDiff(norm_local, norm_remote, ignore_order=True)
    
    if "dictionary_item_added" in diff:
        for item in diff["dictionary_item_added"]:
            typer.echo(f"  + Added: {item}")
    if "dictionary_item_removed" in diff:
        for item in diff["dictionary_item_removed"]:
            typer.echo(f"  - Removed: {item}")
    if "values_changed" in diff:
        for item, change in diff["values_changed"].items():
            typer.echo(f"  ~ Changed: {item}")
            typer.echo(f"      Local:  {change['old_value']}")
            typer.echo(f"      Remote: {change['new_value']}")
    if "iterable_item_added" in diff:
        for item, value in diff["iterable_item_added"].items():
            typer.echo(f"  + Added item to list: {item}")
    if "iterable_item_removed" in diff:
        for item, value in diff["iterable_item_removed"].items():
            typer.echo(f"  - Removed item from list: {item}")

def show_diff(client: N8nClient, directory_str: str):
    """Compare local and remote workflows."""
    local_wfs = get_local_workflows(directory_str)
    remote_wfs = get_remote_workflows(client)
    state = SyncState(directory_str)
    
    local_ids = set(local_wfs.keys())
    remote_ids = set(remote_wfs.keys())
    
    only_local = local_ids - remote_ids
    only_remote = remote_ids - local_ids
    both = local_ids.intersection(remote_ids)
    
    diff_found = False
    
    if only_local:
        diff_found = True
        typer.secho("\nWorkflows only in local (LOCAL_ONLY):", fg=typer.colors.CYAN)
        for wf_id in only_local:
            name = local_wfs[wf_id].get("name", "untitled")
            typer.echo(f"  + {name} (ID: {wf_id})")
            
    if only_remote:
        diff_found = True
        typer.secho("\nWorkflows only in remote (REMOTE_ONLY):", fg=typer.colors.MAGENTA)
        for wf_id in only_remote:
            name = remote_wfs[wf_id].get("name", "untitled")
            typer.echo(f"  + {name} (ID: {wf_id})")
            
    modified = []
    for wf_id in both:
        local_data = local_wfs[wf_id]
        remote_data = remote_wfs[wf_id]
        
        sync_status = evaluate_sync_state(local_data, remote_data, state, wf_id)
        
        if sync_status != "UNCHANGED":
            modified.append((wf_id, sync_status))
            
    if modified:
        diff_found = True
        typer.secho("\nWorkflows modified:", fg=typer.colors.YELLOW)
        for wf_id, sync_status in modified:
            name = local_wfs[wf_id].get("name", "untitled")
            color = typer.colors.YELLOW if sync_status != "CONFLICT" else typer.colors.RED
            typer.secho(f"\n[{sync_status}] {name} (ID: {wf_id})", fg=color, bold=True)
            print_deep_diff(local_wfs[wf_id], remote_wfs[wf_id])
            
    if not diff_found:
        typer.secho("\nLocal and remote workflows are completely synced.", fg=typer.colors.GREEN)

