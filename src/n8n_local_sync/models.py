from pydantic import BaseModel
from typing import Optional

class N8nConfig(BaseModel):
    url: str

class WorkflowsConfig(BaseModel):
    directory: str

class SyncConfig(BaseModel):
    strategy: str

class ProjectConfig(BaseModel):
    version: int
    n8n: N8nConfig
    workflows: WorkflowsConfig
    sync: SyncConfig
