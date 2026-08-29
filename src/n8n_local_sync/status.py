import typer
from rich.console import Console
from rich.table import Table

from n8n_local_sync.api import N8nClient
from n8n_local_sync.diff import get_local_workflows, get_remote_workflows, evaluate_sync_state
from n8n_local_sync.state import SyncState

def show_status(client: N8nClient, directory_str: str):
    """Show the synchronization status of workflows in a table."""
    local_wfs = get_local_workflows(directory_str)
    remote_wfs = get_remote_workflows(client)
    state = SyncState(directory_str)
    
    local_ids = set(local_wfs.keys())
    remote_ids = set(remote_wfs.keys())
    
    only_local = local_ids - remote_ids
    only_remote = remote_ids - local_ids
    both = local_ids.intersection(remote_ids)
    
    status_counts = {
        "UNCHANGED": 0,
        "LOCAL_MODIFIED": 0,
        "REMOTE_MODIFIED": 0,
        "CONFLICT": 0,
        "LOCAL_ONLY": len(only_local),
        "REMOTE_ONLY": len(only_remote)
    }
    
    workflow_statuses = []
    
    for wf_id in only_local:
        name = local_wfs[wf_id].get("name", "untitled")
        workflow_statuses.append((name, "LOCAL_ONLY"))

    for wf_id in only_remote:
        name = remote_wfs[wf_id].get("name", "untitled")
        workflow_statuses.append((name, "REMOTE_ONLY"))

    for wf_id in both:
        sync_status = evaluate_sync_state(local_wfs[wf_id], remote_wfs[wf_id], state, wf_id)
        status_counts[sync_status] += 1
        name = local_wfs[wf_id].get("name", "untitled")
        workflow_statuses.append((name, sync_status))

    console = Console()
    
    console.print("\n[bold]n8n-local-sync status[/bold]\n")
    console.print(f"n8n URL: [cyan]{client.base_url}[/cyan]")
    console.print(f"Directory: [cyan]{directory_str}[/cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Workflow")
    table.add_column("State")
    
    # Sort for deterministic output
    workflow_statuses.sort(key=lambda x: x[0])
    
    for name, status in workflow_statuses:
        color_map = {
            "UNCHANGED": "green",
            "LOCAL_MODIFIED": "yellow",
            "REMOTE_MODIFIED": "yellow",
            "CONFLICT": "red",
            "LOCAL_ONLY": "cyan",
            "REMOTE_ONLY": "magenta"
        }
        color = color_map.get(status, "white")
        table.add_row(name, f"[{color}]{status}[/{color}]")
        
    console.print(table)
    
    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("State Summary")
    summary_table.add_column("Count", justify="right")
    
    summary_table.add_row("Total Local", str(len(local_ids)))
    summary_table.add_row("Total Remote", str(len(remote_ids)))
    for s_name, count in status_counts.items():
        if count > 0:
            summary_table.add_row(s_name, str(count))
            
    console.print(summary_table)
    console.print()

