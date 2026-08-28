import typer
from n8n_local_sync.config import init_project

app = typer.Typer(help="CLI for syncing local n8n workflows with git")

@app.command()
def init():
    """Initialize a new n8n-sync project in the current directory."""
    try:
        init_project()
        typer.secho("Project initialized successfully.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error initializing project: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command()
def validate():
    """Validate workflows against the local configuration."""
    from n8n_local_sync.config import load_config
    from n8n_local_sync.validation import validate_workflows_directory
    
    try:
        config = load_config()
    except Exception as e:
        typer.secho(f"Error loading config: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    is_valid = validate_workflows_directory(config.workflows.directory)
    if not is_valid:
        raise typer.Exit(code=1)

@app.command()
def export(
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate the export without writing files"),
    tag: str = typer.Option(None, "--tag", help="Filter workflows to export by tag")
):
    """Export workflows from n8n into the local repository."""
    from n8n_local_sync.config import load_config, get_api_key, get_base_url
    from n8n_local_sync.api import N8nClient
    from n8n_local_sync.export import export_workflows
    
    try:
        config = load_config()
        api_key = get_api_key()
        base_url = get_base_url(config)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    client = N8nClient(base_url=base_url, api_key=api_key)
    try:
        export_workflows(client, config.workflows.directory, dry_run=dry_run, tag=tag)
    except Exception as e:
        typer.secho(f"Error during export: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        client.close()

@app.command("import")
def import_workflows(dry_run: bool = typer.Option(False, "--dry-run", help="Simulate the import without modifying n8n")):
    """Import workflows from the local repository into n8n."""
    from n8n_local_sync.config import load_config, get_api_key, get_base_url
    from n8n_local_sync.api import N8nClient
    from n8n_local_sync.import_ import import_workflows as do_import
    
    try:
        config = load_config()
        api_key = get_api_key()
        base_url = get_base_url(config)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    client = N8nClient(base_url=base_url, api_key=api_key)
    try:
        do_import(client, config.workflows.directory, dry_run=dry_run)
    except Exception as e:
        typer.secho(f"Error during import: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        client.close()

@app.command()
def sync(
    force: bool = typer.Option(False, "--force", help="Overwrite local modifications with remote versions"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate the sync without applying changes")
):
    """Sync workflows between n8n and the local repository."""
    from n8n_local_sync.config import load_config, get_api_key, get_base_url
    from n8n_local_sync.api import N8nClient
    from n8n_local_sync.sync import sync_workflows
    
    try:
        config = load_config()
        api_key = get_api_key()
        base_url = get_base_url(config)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    client = N8nClient(base_url=base_url, api_key=api_key)
    try:
        sync_workflows(client, config.workflows.directory, force=force, dry_run=dry_run)
    except Exception as e:
        typer.secho(f"Error during sync: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        client.close()

@app.command()
def status():
    """Show the status of workflows."""
    from n8n_local_sync.config import load_config, get_api_key, get_base_url
    from n8n_local_sync.api import N8nClient
    from n8n_local_sync.status import show_status
    
    try:
        config = load_config()
        api_key = get_api_key()
        base_url = get_base_url(config)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    client = N8nClient(base_url=base_url, api_key=api_key)
    try:
        show_status(client, config.workflows.directory)
    except Exception as e:
        typer.secho(f"Error checking status: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        client.close()

@app.command()
def diff():
    """Show changes between local workflows and n8n."""
    from n8n_local_sync.config import load_config, get_api_key, get_base_url
    from n8n_local_sync.api import N8nClient
    from n8n_local_sync.diff import show_diff
    
    try:
        config = load_config()
        api_key = get_api_key()
        base_url = get_base_url(config)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    client = N8nClient(base_url=base_url, api_key=api_key)
    try:
        show_diff(client, config.workflows.directory)
    except Exception as e:
        typer.secho(f"Error computing diff: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        client.close()

if __name__ == "__main__":
    app()
