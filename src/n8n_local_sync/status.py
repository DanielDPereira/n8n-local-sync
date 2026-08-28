import typer
from rich.console import Console
from rich.table import Table

from n8n_local_sync.api import N8nClient
from n8n_local_sync.diff import get_local_workflows, get_remote_workflows

def show_status(client: N8nClient, directory_str: str):
    """Show the synchronization status of workflows in a table."""
    local_wfs = get_local_workflows(directory_str)
    remote_wfs = get_remote_workflows(client)
    
    local_ids = set(local_wfs.keys())
    remote_ids = set(remote_wfs.keys())
    
    only_local = local_ids - remote_ids
    only_remote = remote_ids - local_ids
    both = local_ids.intersection(remote_ids)
    
    synced = 0
    modified = 0
    
    for wf_id in both:
        if local_wfs[wf_id] == remote_wfs[wf_id]:
            synced += 1
        else:
            modified += 1

    console = Console()
    
    console.print("\n[bold]n8n-local-sync status[/bold]\n")
    console.print(f"n8n URL: [cyan]{client.base_url}[/cyan]")
    console.print(f"Directory: [cyan]{directory_str}[/cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("State")
    table.add_column("Count", justify="right")
    
    table.add_row("Total Local", str(len(local_ids)))
    table.add_row("Total Remote", str(len(remote_ids)))
    table.add_row("[green]Synchronized[/green]", str(synced))
    table.add_row("[yellow]Modified (diverged)[/yellow]", str(modified))
    table.add_row("[cyan]Only Local[/cyan]", str(len(only_local)))
    table.add_row("[red]Only Remote[/red]", str(len(only_remote)))
    
    console.print(table)
    console.print()
