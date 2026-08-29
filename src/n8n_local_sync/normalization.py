import hashlib
import json
from typing import Any


def normalize_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    """
    Remove volatile metadata from workflow data so that
    hashes and Git diffs remain deterministic.
    """
    normalized = workflow.copy()

    # Remove fields that change on every export or aren't needed for logical comparison
    fields_to_remove = ["createdAt", "updatedAt", "versionId"]
    for field in fields_to_remove:
        normalized.pop(field, None)

    # Normalize node order based on node 'name' (which must be unique per workflow)
    if "nodes" in normalized and isinstance(normalized["nodes"], list):
        normalized["nodes"] = sorted(
            [normalize_node(n) for n in normalized["nodes"]],
            key=lambda x: x.get("name", "")
        )

    # Normalize connections (keys are node names)
    if "connections" in normalized and isinstance(normalized["connections"], dict):
        normalized["connections"] = dict(sorted(normalized["connections"].items()))
        # Sort targets within connections
        for source_node, connections in normalized["connections"].items():
            if isinstance(connections, dict):
                for targets in connections.values():
                    if isinstance(targets, list):
                        # targets is a list of lists: [[{"node": "Next", "type": "main", "index": 0}]]
                        for i, target_group in enumerate(targets):
                            if isinstance(target_group, list):
                                targets[i] = sorted(
                                    target_group,
                                    key=lambda x: (x.get("node", ""), x.get("type", ""), x.get("index", 0))
                                )
                normalized["connections"][source_node] = dict(sorted(connections.items()))

    return normalized

def normalize_node(node: dict[str, Any]) -> dict[str, Any]:
    """Normalize a single node."""
    normalized = node.copy()
    if "position" in normalized:
        # Round positions to avoid trivial UI changes causing diffs
        # Not removing entirely because layout matters for n8n GUI
        # Keep as is, position changes DO matter for UI, but could be rounded to ints
        if isinstance(normalized["position"], list) and len(normalized["position"]) == 2:
            normalized["position"] = [round(float(p)) for p in normalized["position"]]
    return normalized

def get_canonical_hash(workflow: dict[str, Any]) -> str:
    """
    Return a SHA-256 hash of the normalized workflow.
    Ensures deterministic JSON encoding.
    """
    normalized = normalize_workflow(workflow)
    canonical_json = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
