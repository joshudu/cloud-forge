from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TenantCreate(BaseModel):
    name: str

class TenantResponse(BaseModel):
    id: UUID
    name: str
    schema_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}