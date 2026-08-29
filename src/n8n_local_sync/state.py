import json
from pathlib import Path
from typing import Any, Dict

STATE_FILENAME = ".n8n-sync-state.json"

class SyncState:
    def __init__(self, directory_str: str):
        self.directory = Path(directory_str)
        self.state_file = self.directory / STATE_FILENAME
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from the state file."""
        if not self.state_file.exists():
            return {"workflows": {}}
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # If state is corrupted, start fresh
            return {"workflows": {}}

    def _save_state(self):
        """Save state to the state file."""
        self.directory.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, sort_keys=True)

    def get_last_synced_hash(self, workflow_id: str) -> str:
        """Get the hash of a workflow when it was last synced."""
        return self.state.get("workflows", {}).get(workflow_id, {}).get("hash", "")

    def update_workflow_hash(self, workflow_id: str, current_hash: str):
        """Update the stored hash for a workflow."""
        if "workflows" not in self.state:
            self.state["workflows"] = {}
        if workflow_id not in self.state["workflows"]:
            self.state["workflows"][workflow_id] = {}
        self.state["workflows"][workflow_id]["hash"] = current_hash
        self._save_state()

    def remove_workflow(self, workflow_id: str):
        """Remove a workflow from the state."""
        if "workflows" in self.state and workflow_id in self.state["workflows"]:
            del self.state["workflows"][workflow_id]
            self._save_state()

def evaluate_sync_state(local_data: dict, remote_data: dict, state: SyncState, wf_id: str) -> str:
    """Evaluate the sync state: UNCHANGED, LOCAL_MODIFIED, REMOTE_MODIFIED, CONFLICT."""
    from n8n_local_sync.normalization import get_canonical_hash
    local_hash = get_canonical_hash(local_data)
    remote_hash = get_canonical_hash(remote_data)
    
    if local_hash == remote_hash:
        return "UNCHANGED"
        
    last_synced_hash = state.get_last_synced_hash(wf_id)
    
    if not last_synced_hash:
        # We don't have history. Default to CONFLICT to be safe.
        return "CONFLICT"
        
    if local_hash == last_synced_hash and remote_hash != last_synced_hash:
        return "REMOTE_MODIFIED"
    elif local_hash != last_synced_hash and remote_hash == last_synced_hash:
        return "LOCAL_MODIFIED"
    else:
        # Both changed from the last synced state
        return "CONFLICT"
