from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.resource import ResourceType
import json

class ResourceCreate(BaseModel):
    name: str
    resource_type: ResourceType
    project_id: UUID
    configuration: Optional[dict] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Resource name cannot be empty")
        return v.strip()

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    configuration: Optional[dict] = None
    is_active: Optional[bool] = None

class ResourceResponse(BaseModel):
    id: UUID
    name: str
    resource_type: ResourceType
    project_id: UUID
    configuration: Optional[dict]
    is_active: bool
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}