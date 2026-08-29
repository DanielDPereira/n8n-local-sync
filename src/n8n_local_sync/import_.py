import json
import logging
from pathlib import Path

import typer

from n8n_local_sync.api import N8nClient
from n8n_local_sync.diff import get_local_workflows, get_remote_workflows
from n8n_local_sync.export import slugify
from n8n_local_sync.normalization import get_canonical_hash
from n8n_local_sync.state import SyncState, evaluate_sync_state
from n8n_local_sync.validation import validate_workflow_file

logger = logging.getLogger(__name__)

def import_workflows(client: N8nClient, directory_str: str, force: bool = False, dry_run: bool = False):
    """
    Safely push local workflows to the remote n8n instance.
    Uses state tracking to prevent overwriting remote modifications unless --force is used.
    """
    directory = Path(directory_str)
    if not directory.exists() or not directory.is_dir():
        typer.secho(f"Error: Directory '{directory}' does not exist.", fg=typer.colors.RED, err=True)
        return

    local_wfs = get_local_workflows(directory_str)
    remote_wfs = get_remote_workflows(client)
    state = SyncState(directory_str)

    local_ids = set(local_wfs.keys())
    remote_ids = set(remote_wfs.keys())

    both = local_ids.intersection(remote_ids)
    only_local = local_ids - remote_ids

    imported_count = 0
    skipped_count = 0

    # Whitelist allowed keys for n8n API POST/PUT
    allowed_keys = {"name", "nodes", "connections", "settings", "staticData", "pinData"}

    # 1. New local workflows (LOCAL_ONLY)
    for wf_id in only_local:
        wf_data = local_wfs[wf_id]
        wf_name = wf_data.get("name", "untitled")
        
        # We must validate before pushing
        # Find the original file
        file_path = None
        for p in directory.glob(f"{wf_id}-*.json"):
            file_path = p
            break
        
        if file_path:
            is_valid, errors = validate_workflow_file(file_path)
            if not is_valid:
                typer.secho(f"Skipping invalid workflow '{wf_name}': {errors}", fg=typer.colors.YELLOW)
                skipped_count += 1
                continue
                
        clean_data = {k: v for k, v in wf_data.items() if k in allowed_keys}
        
        if dry_run:
            typer.secho(f"[DRY-RUN] Would create new workflow '{wf_name}' (LOCAL_ONLY)...", fg=typer.colors.GREEN)
            imported_count += 1
        else:
            typer.secho(f"Creating new workflow '{wf_name}'...", fg=typer.colors.GREEN)
            try:
                new_wf = client.create_workflow(clean_data)
                new_id = new_wf.get("id")
                typer.secho(f"Created with new ID: {new_id}", fg=typer.colors.GREEN)
                
                # Update local file with new ID
                wf_data["id"] = new_id
                wf_data["createdAt"] = new_wf.get("createdAt")
                wf_data["updatedAt"] = new_wf.get("updatedAt")
                
                safe_name = slugify(wf_name)
                new_filename = f"{new_id}-{safe_name}.json"
                
                # Delete old file, create new
                if file_path and file_path.exists():
                    file_path.unlink()
                
                with open(directory / new_filename, "w", encoding="utf-8") as f:
                    json.dump(wf_data, f, indent=2, sort_keys=True)
                    
                state.update_workflow_hash(new_id, get_canonical_hash(new_wf))
                if wf_id in state.state.get("workflows", {}):
                    state.remove_workflow(wf_id)
                imported_count += 1
            except Exception as e:
                typer.secho(f"Failed to create '{wf_name}': {e}", fg=typer.colors.RED, err=True)

    # 2. Diverged workflows
    for wf_id in both:
        local_data = local_wfs[wf_id]
        remote_data = remote_wfs[wf_id]
        wf_name = local_data.get("name", "untitled")
        
        sync_status = evaluate_sync_state(local_data, remote_data, state, wf_id)
        
        if sync_status == "UNCHANGED":
            if not dry_run:
                state.update_workflow_hash(wf_id, get_canonical_hash(remote_data))
            continue
            
        elif sync_status == "LOCAL_MODIFIED":
            # Safe to push
            file_path = None
            for p in directory.glob(f"{wf_id}-*.json"):
                file_path = p
                break
            
            if file_path:
                is_valid, errors = validate_workflow_file(file_path)
                if not is_valid:
                    if not force:
                        typer.secho(f"Skipping invalid workflow '{wf_name}' (LOCAL_MODIFIED): {errors}", fg=typer.colors.YELLOW)
                        typer.secho("  -> Use '--force' to push anyway.", fg=typer.colors.YELLOW)
                        skipped_count += 1
                        continue
                    else:
                        typer.secho(f"Warning: Pushing invalid workflow '{wf_name}' due to --force: {errors}", fg=typer.colors.RED)
            
            clean_data = {k: v for k, v in local_data.items() if k in allowed_keys}
            
            if dry_run:
                typer.secho(f"[DRY-RUN] Would update remote workflow '{wf_name}' (ID: {wf_id}) (LOCAL_MODIFIED).", fg=typer.colors.GREEN)
                imported_count += 1
            else:
                typer.secho(f"Updating remote workflow '{wf_name}' (ID: {wf_id})...", fg=typer.colors.GREEN)
                try:
                    updated_wf = client.update_workflow(wf_id, clean_data)
                    state.update_workflow_hash(wf_id, get_canonical_hash(updated_wf))
                    imported_count += 1
                except Exception as e:
                    typer.secho(f"Failed to update '{wf_name}': {e}", fg=typer.colors.RED, err=True)
                    
        elif sync_status == "REMOTE_MODIFIED":
            if not force:
                typer.secho(f"Skipping '{wf_name}' (ID: {wf_id}). It is REMOTE_MODIFIED. Use 'n8n-sync pull' or --force.", fg=typer.colors.YELLOW)
                skipped_count += 1
            else:
                clean_data = {k: v for k, v in local_data.items() if k in allowed_keys}
                if dry_run:
                    typer.secho(f"[DRY-RUN] Would overwrite remote workflow '{wf_name}' (REMOTE_MODIFIED + force).", fg=typer.colors.RED)
                    imported_count += 1
                else:
                    typer.secho(f"Overwriting remote workflow '{wf_name}' (ID: {wf_id})...", fg=typer.colors.RED)
                    try:
                        updated_wf = client.update_workflow(wf_id, clean_data)
                        state.update_workflow_hash(wf_id, get_canonical_hash(updated_wf))
                        imported_count += 1
                    except Exception as e:
                        typer.secho(f"Failed to update '{wf_name}': {e}", fg=typer.colors.RED, err=True)

        elif sync_status == "CONFLICT":
            if not force:
                typer.secho(f"Conflict detected for '{wf_name}' (ID: {wf_id}). Skipping push.", fg=typer.colors.RED)
                typer.secho("  -> Use 'n8n-sync diff' to see differences, or run with '--force' to overwrite remote.", fg=typer.colors.YELLOW)
                skipped_count += 1
            else:
                clean_data = {k: v for k, v in local_data.items() if k in allowed_keys}
                if dry_run:
                    typer.secho(f"[DRY-RUN] Would overwrite remote workflow '{wf_name}' (CONFLICT + force).", fg=typer.colors.RED)
                    imported_count += 1
                else:
                    typer.secho(f"Overwriting remote workflow '{wf_name}' (ID: {wf_id})...", fg=typer.colors.RED)
                    try:
                        updated_wf = client.update_workflow(wf_id, clean_data)
                        state.update_workflow_hash(wf_id, get_canonical_hash(updated_wf))
                        imported_count += 1
                    except Exception as e:
                        typer.secho(f"Failed to update '{wf_name}': {e}", fg=typer.colors.RED, err=True)

    if dry_run:
        typer.secho(f"\n[DRY-RUN] Push would complete. {imported_count} updated remote, {skipped_count} skipped.", fg=typer.colors.GREEN)
    else:
        typer.secho(f"\nPush complete. {imported_count} updated remote, {skipped_count} skipped.", fg=typer.colors.GREEN)
