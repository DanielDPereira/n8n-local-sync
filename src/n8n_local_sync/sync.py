import typer
import json
from pathlib import Path

from n8n_local_sync.api import N8nClient
from n8n_local_sync.diff import get_local_workflows, get_remote_workflows, evaluate_sync_state
from n8n_local_sync.export import slugify, clean_workflow_data
from n8n_local_sync.normalization import get_canonical_hash
from n8n_local_sync.state import SyncState

def sync_workflows(client: N8nClient, directory_str: str, force: bool = False, dry_run: bool = False):
    """
    Safely pull remote workflows to local directory.
    If there are divergences (modified in both places, or modified locally without import),
    it will warn the user and skip overwriting unless --force is used.
    """
    local_wfs = get_local_workflows(directory_str)
    remote_wfs = get_remote_workflows(client)
    state = SyncState(directory_str)
    
    local_ids = set(local_wfs.keys())
    remote_ids = set(remote_wfs.keys())
    
    both = local_ids.intersection(remote_ids)
    only_remote = remote_ids - local_ids
    
    out_path = Path(directory_str)
    if not dry_run:
        out_path.mkdir(parents=True, exist_ok=True)
    
    synced_count = 0
    skipped_count = 0
    
    # 1. New remote workflows
    for wf_id in only_remote:
        wf_data = clean_workflow_data(remote_wfs[wf_id])
        name = wf_data.get("name", "untitled")
        safe_name = slugify(name)
        filename = f"{wf_id}-{safe_name}.json"
        
        if dry_run:
            typer.echo(f"[DRY-RUN] Would create local file for new remote workflow (REMOTE_ONLY): {name}")
        else:
            typer.echo(f"Creating local file for new remote workflow: {name}")
            with open(out_path / filename, "w", encoding="utf-8") as f:
                json.dump(wf_data, f, indent=2, sort_keys=True)
            state.update_workflow_hash(wf_id, get_canonical_hash(wf_data))
        synced_count += 1
            
    # 2. Diverged workflows
    for wf_id in both:
        local_data = local_wfs[wf_id]
        remote_data = remote_wfs[wf_id]
        
        sync_status = evaluate_sync_state(local_data, remote_data, state, wf_id)
        name = local_data.get("name", "untitled")
        
        if sync_status == "UNCHANGED":
            # Just ensure the state hash is recorded
            if not dry_run:
                state.update_workflow_hash(wf_id, get_canonical_hash(local_data))
            continue
            
        elif sync_status == "REMOTE_MODIFIED":
            cleaned_remote = clean_workflow_data(remote_data)
            if dry_run:
                typer.secho(f"[DRY-RUN] Would update local file for '{name}' (REMOTE_MODIFIED).", fg=typer.colors.GREEN)
            else:
                typer.secho(f"Updating local file for '{name}' (ID: {wf_id}).", fg=typer.colors.GREEN)
                safe_name = slugify(name)
                filename = f"{wf_id}-{safe_name}.json"
                with open(out_path / filename, "w", encoding="utf-8") as f:
                    json.dump(cleaned_remote, f, indent=2, sort_keys=True)
                state.update_workflow_hash(wf_id, get_canonical_hash(cleaned_remote))
            synced_count += 1
            
        elif sync_status == "LOCAL_MODIFIED":
            if not force:
                typer.secho(f"Skipping '{name}' (ID: {wf_id}). It is LOCAL_MODIFIED. Use 'n8n-sync push' or --force.", fg=typer.colors.YELLOW)
                skipped_count += 1
            else:
                cleaned_remote = clean_workflow_data(remote_data)
                if dry_run:
                    typer.secho(f"[DRY-RUN] Would overwrite local file for '{name}' with remote (LOCAL_MODIFIED + force).", fg=typer.colors.RED)
                else:
                    typer.secho(f"Overwriting local file for '{name}' (ID: {wf_id}).", fg=typer.colors.RED)
                    safe_name = slugify(name)
                    filename = f"{wf_id}-{safe_name}.json"
                    with open(out_path / filename, "w", encoding="utf-8") as f:
                        json.dump(cleaned_remote, f, indent=2, sort_keys=True)
                    state.update_workflow_hash(wf_id, get_canonical_hash(cleaned_remote))
                synced_count += 1
                
        elif sync_status == "CONFLICT":
            if not force:
                typer.secho(f"Conflict detected for '{name}' (ID: {wf_id}). Skipping pull.", fg=typer.colors.RED)
                typer.secho(f"  -> Use 'n8n-sync diff' to see differences, or run with '--force' to overwrite local.", fg=typer.colors.YELLOW)
                skipped_count += 1
            else:
                cleaned_remote = clean_workflow_data(remote_data)
                if dry_run:
                    typer.secho(f"[DRY-RUN] Would overwrite local file for '{name}' (CONFLICT + force).", fg=typer.colors.RED)
                else:
                    typer.secho(f"Overwriting local file for '{name}' (ID: {wf_id}).", fg=typer.colors.RED)
                    safe_name = slugify(name)
                    filename = f"{wf_id}-{safe_name}.json"
                    with open(out_path / filename, "w", encoding="utf-8") as f:
                        json.dump(cleaned_remote, f, indent=2, sort_keys=True)
                    state.update_workflow_hash(wf_id, get_canonical_hash(cleaned_remote))
                synced_count += 1

    if dry_run:
        typer.secho(f"\n[DRY-RUN] Sync would complete. {synced_count} updated, {skipped_count} skipped.", fg=typer.colors.GREEN)
    else:
        typer.secho(f"\nSync complete. {synced_count} updated locally, {skipped_count} skipped.", fg=typer.colors.GREEN)

