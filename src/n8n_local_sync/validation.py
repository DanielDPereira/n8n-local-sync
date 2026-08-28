import json
import logging
from pathlib import Path
from typing import Tuple, List

logger = logging.getLogger(__name__)

def validate_workflow_file(filepath: Path) -> Tuple[bool, List[str]]:
    """
    Validates a single workflow JSON file.
    Returns a tuple (is_valid, list_of_errors).
    """
    errors = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON format: {e}"]
    except Exception as e:
        return False, [f"Could not read file: {e}"]

    if not isinstance(data, dict):
        return False, ["Root of JSON must be an object/dict."]

    if "nodes" not in data:
        errors.append("Missing required field: 'nodes'.")
    elif not isinstance(data["nodes"], list):
        errors.append("'nodes' must be a list.")

    if "connections" not in data:
        errors.append("Missing required field: 'connections'.")
    elif not isinstance(data["connections"], dict):
        errors.append("'connections' must be an object.")

    # Check for possible leaked credentials directly in JSON
    # It's a simple heuristic checking keys that often contain secrets
    suspicious_keys = ["password", "secret", "token", "apikey", "api_key"]
    
    def search_for_secrets(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if any(sus in k.lower() for sus in suspicious_keys):
                    if isinstance(v, str) and len(v) > 0 and v != "={": 
                        # '={' is usually an n8n expression. Raw values are suspicious.
                        if not v.startswith("={{"):
                            errors.append(f"Potential secret found in key: '{k}'")
                search_for_secrets(v)
        elif isinstance(obj, list):
            for item in obj:
                search_for_secrets(item)
                
    search_for_secrets(data)

    is_valid = len(errors) == 0
    return is_valid, errors

def validate_workflows_directory(directory_str: str) -> bool:
    """
    Validates all .json files in the given directory.
    Returns True if all files are valid, False otherwise.
    """
    directory = Path(directory_str)
    if not directory.exists() or not directory.is_dir():
        print(f"Error: Directory '{directory}' does not exist.")
        return False

    all_valid = True
    for file_path in directory.glob("*.json"):
        is_valid, errors = validate_workflow_file(file_path)
        if not is_valid:
            all_valid = False
            print(f"Validation failed for: {file_path.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"Validated: {file_path.name}")

    if all_valid:
        print("All workflows are valid.")
    return all_valid
