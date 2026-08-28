import os
import yaml
from pathlib import Path
from typing import Optional
from n8n_local_sync.models import ProjectConfig

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

def load_config() -> ProjectConfig:
    """Load configuration from the local .n8n-sync.yaml file."""
    config_path = Path(CONFIG_FILENAME)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file '{CONFIG_FILENAME}' not found. Run 'n8n-sync init' first.")
    
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    
    return ProjectConfig(**data)

def get_api_key() -> str:
    """Retrieve the n8n API key from environment variables."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    api_key = os.environ.get("N8N_API_KEY")
    if not api_key:
        raise ValueError("N8N_API_KEY environment variable is not set. Please set it in a .env file or export it.")
    return api_key

def get_base_url(config: ProjectConfig) -> str:
    """
    Retrieve the n8n base URL.
    Prioritizes N8N_BASE_URL env var, then falls back to config file.
    """
    env_url = os.environ.get("N8N_BASE_URL")
    if env_url:
        return env_url
    return config.n8n.url
