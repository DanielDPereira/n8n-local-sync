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
def export():
    """Export workflows from n8n into the local repository."""
    from n8n_local_sync.config import load_config, get_api_key
    from n8n_local_sync.api import N8nClient
    from n8n_local_sync.export import export_workflows
    
    try:
        config = load_config()
        api_key = get_api_key()
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    client = N8nClient(base_url=config.n8n.url, api_key=api_key)
    try:
        export_workflows(client, config.workflows.directory)
    except Exception as e:
        typer.secho(f"Error during export: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        client.close()

@app.command()
def import_workflows():
    """Import workflows from the local repository into n8n."""
    from n8n_local_sync.config import load_config, get_api_key
    from n8n_local_sync.api import N8nClient
    from n8n_local_sync.import_ import import_workflows as do_import
    
    try:
        config = load_config()
        api_key = get_api_key()
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    client = N8nClient(base_url=config.n8n.url, api_key=api_key)
    try:
        do_import(client, config.workflows.directory)
    except Exception as e:
        typer.secho(f"Error during import: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        client.close()

@app.command()
def sync():
    """Sync workflows between n8n and the local repository."""
    typer.secho("Not implemented yet.", fg=typer.colors.YELLOW)

@app.command()
def status():
    """Show the status of workflows."""
    typer.secho("Not implemented yet.", fg=typer.colors.YELLOW)

@app.command()
def diff():
    """Show changes between local workflows and n8n."""
    from n8n_local_sync.config import load_config, get_api_key
    from n8n_local_sync.api import N8nClient
    from n8n_local_sync.diff import show_diff
    
    try:
        config = load_config()
        api_key = get_api_key()
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    client = N8nClient(base_url=config.n8n.url, api_key=api_key)
    try:
        show_diff(client, config.workflows.directory)
    except Exception as e:
        typer.secho(f"Error computing diff: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        client.close()

if __name__ == "__main__":
    app()
