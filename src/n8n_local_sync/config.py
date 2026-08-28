import os
import yaml
from pathlib import Path

CONFIG_FILENAME = ".n8n-sync.yaml"
DEFAULT_WORKFLOWS_DIR = "n8n/workflows"

def init_project():
    """Initializes the current directory as an n8n-local-sync project."""
    config_path = Path(CONFIG_FILENAME)
    workflows_path = Path(DEFAULT_WORKFLOWS_DIR)

    if config_path.exists():
        raise FileExistsError(f"Configuration file '{CONFIG_FILENAME}' already exists in this directory.")

    # Create workflows directory
    workflows_path.mkdir(parents=True, exist_ok=True)

    # Generate initial configuration
    initial_config = {
        "version": 1,
        "n8n": {
            "url": "http://localhost:5678"
        },
        "workflows": {
            "directory": f"./{DEFAULT_WORKFLOWS_DIR}"
        },
        "sync": {
            "strategy": "official-api"
        }
    }

    with open(config_path, "w") as f:
        yaml.dump(initial_config, f, sort_keys=False, default_flow_style=False)

    print(f"Created configuration file: {CONFIG_FILENAME}")
    print(f"Created workflows directory: {DEFAULT_WORKFLOWS_DIR}")
    print("\nNext steps:")
    print("1. Update the .n8n-sync.yaml with your n8n instance URL if it's not localhost.")
    print("2. Set the N8N_API_KEY environment variable (e.g. in a .env file).")
    print("3. Run 'n8n-sync export' to pull existing workflows from your instance.")
