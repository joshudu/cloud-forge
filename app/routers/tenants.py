from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantResponse
import re

router = APIRouter(prefix="/tenants", tags=["tenants"])

RESERVED_SCHEMA_NAMES = {
    "public", "pg_catalog", "information_schema",
    "pg_toast", "cloudforge", "admin", "root"
}

def generate_schema_name(tenant_name: str) -> str:
    safe = re.sub(r'[^a-zA-Z0-9]', '_', tenant_name.lower())
    return f"tenant_{safe}"

@router.post("/", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    if tenant_data.name.lower() in RESERVED_SCHEMA_NAMES:
        raise HTTPException(status_code=400, detail=f"'{tenant_data.name}' is a reserved name")

    schema_name = generate_schema_name(tenant_data.name)
    # rest of your existing code unchanged below...
    # Check if schema already exists
    existing = await db.execute(
        text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"),
        {"schema": schema_name}
    )
    if existing.fetchone():
        raise HTTPException(status_code=400, detail="Tenant already exists")

    # Create the PostgreSQL schema for this tenant
    await db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

    # Register the tenant in the public.tenants table
    tenant = Tenant(name=tenant_data.name, schema_name=schema_name)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    return tenant

@router.get("/", response_model=list[TenantResponse])
async def list_tenants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM tenants"))
    return result.fetchall()