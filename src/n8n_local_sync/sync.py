import typer
import json
from pathlib import Path

from n8n_local_sync.api import N8nClient
from n8n_local_sync.diff import get_local_workflows, get_remote_workflows
from n8n_local_sync.export import slugify

def sync_workflows(client: N8nClient, directory_str: str, force: bool = False):
    """
    Safely pull remote workflows to local directory.
    If there are divergences (modified in both places, or modified locally without import),
    it will warn the user and skip overwriting unless --force is used.
    """
    local_wfs = get_local_workflows(directory_str)
    remote_wfs = get_remote_workflows(client)
    
    local_ids = set(local_wfs.keys())
    remote_ids = set(remote_wfs.keys())
    
    both = local_ids.intersection(remote_ids)
    only_remote = remote_ids - local_ids
    
    out_path = Path(directory_str)
    out_path.mkdir(parents=True, exist_ok=True)
    
    synced_count = 0
    
    # 1. New remote workflows
    for wf_id in only_remote:
        wf_data = remote_wfs[wf_id]
        name = wf_data.get("name", "untitled")
        safe_name = slugify(name)
        filename = f"{wf_id}-{safe_name}.json"
        
        typer.echo(f"Creating local file for new remote workflow: {name}")
        with open(out_path / filename, "w", encoding="utf-8") as f:
            json.dump(wf_data, f, indent=2, sort_keys=True)
        synced_count += 1
            
    # 2. Diverged workflows
    for wf_id in both:
        local_data = local_wfs[wf_id]
        remote_data = remote_wfs[wf_id]
        
        if local_data != remote_data:
            name = remote_data.get("name", "untitled")
            if not force:
                typer.secho(f"Conflict detected for '{name}' (ID: {wf_id}). Skipping pull.", fg=typer.colors.YELLOW)
                typer.secho(f"  -> Use 'n8n-sync diff' to see differences, or run 'n8n-sync sync --force' to overwrite local changes.", fg=typer.colors.YELLOW)
            else:
                typer.secho(f"Overwriting local file for '{name}' (ID: {wf_id}).", fg=typer.colors.RED)
                safe_name = slugify(name)
                filename = f"{wf_id}-{safe_name}.json"
                with open(out_path / filename, "w", encoding="utf-8") as f:
                    json.dump(remote_data, f, indent=2, sort_keys=True)
                synced_count += 1
                
    typer.secho(f"\nSync complete. {synced_count} workflows updated locally.", fg=typer.colors.GREEN)
