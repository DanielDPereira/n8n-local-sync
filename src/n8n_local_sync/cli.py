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
    typer.secho("Not implemented yet.", fg=typer.colors.YELLOW)

@app.command()
def export():
    """Export workflows from n8n into the local repository."""
    typer.secho("Not implemented yet.", fg=typer.colors.YELLOW)

@app.command()
def import_workflows():
    """Import workflows from the local repository into n8n."""
    typer.secho("Not implemented yet.", fg=typer.colors.YELLOW)

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
    typer.secho("Not implemented yet.", fg=typer.colors.YELLOW)

if __name__ == "__main__":
    app()
