import json
import logging
import re
from pathlib import Path
from typing import Any, Dict

from n8n_local_sync.api import N8nClient

logger = logging.getLogger(__name__)

def slugify(text: str) -> str:
    """Convert text into a safe filename."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text

def clean_workflow_data(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove ephemeral fields from workflow data so that
    Git diffs remain clean.
    """
    # Remove fields that change on every export or aren't needed for logic
    fields_to_remove = ["createdAt", "updatedAt", "versionId"]
    for field in fields_to_remove:
        workflow.pop(field, None)
    
    return workflow

def export_workflows(client: N8nClient, output_dir: str, dry_run: bool = False, tag: str = None):
    """
    Fetch all workflows from n8n and save them to the output directory.
    If 'tag' is provided, only workflows containing that tag (by name) will be exported.
    """
    out_path = Path(output_dir)
    
    if not dry_run:
        out_path.mkdir(parents=True, exist_ok=True)

    print("Fetching workflows from n8n...")
    workflows = client.get_workflows()
    
    if not workflows:
        print("No workflows found.")
        return

    exported_count = 0
    for wf_meta in workflows:
        wf_id = wf_meta.get("id")
        wf_name = wf_meta.get("name", "untitled")
        
        if tag:
            # Check tags. It can be a list of dicts: [{'name': 'production', 'id': 'xxx'}] or a list of strings
            wf_tags = wf_meta.get("tags", [])
            tag_names = []
            for t in wf_tags:
                if isinstance(t, dict):
                    tag_names.append(t.get("name", ""))
                elif isinstance(t, str):
                    tag_names.append(t)
            
            if tag not in tag_names:
                continue
        
        if dry_run:
            print(f"[DRY-RUN] Would export workflow '{wf_name}' (ID: {wf_id}).")
            exported_count += 1
            continue
            
        # We need to fetch the full workflow data
        print(f"Exporting workflow '{wf_name}' (ID: {wf_id})...")
        full_wf = client.get_workflow(wf_id)
        
        cleaned_wf = clean_workflow_data(full_wf)
        
        safe_name = slugify(wf_name)
        filename = f"{wf_id}-{safe_name}.json"
        filepath = out_path / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cleaned_wf, f, indent=2, sort_keys=True)
            
        exported_count += 1
            
    if dry_run:
        print(f"[DRY-RUN] Would export {exported_count} workflows successfully.")
    else:
        print(f"Exported {exported_count} workflows successfully.")
