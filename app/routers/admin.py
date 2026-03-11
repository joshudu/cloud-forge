from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from app.db.session import get_db
from app.auth.dependencies import get_current_user_payload
from app.core.logging import get_logger

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger(__name__)

@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def erase_tenant(
    tenant_id: UUID,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db),
):
    """
    GDPR-compliant tenant erasure.
    Drops the tenant's entire schema and removes them from the registry.
    This is irreversible.
    """
    # Get tenant schema name
    result = await db.execute(
        text("SELECT schema_name, name FROM tenants WHERE id = :id"),
        {"id": str(tenant_id)}
    )
    tenant_row = result.fetchone()

    if not tenant_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    schema_name = tenant_row.schema_name
    tenant_name = tenant_row.name

    # Safety check — never drop the public schema
    if schema_name == "public":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot erase public schema"
        )

    # Drop the entire tenant schema and all its data
    await db.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))

    # Remove tenant from registry
    await db.execute(
        text("DELETE FROM tenants WHERE id = :id"),
        {"id": str(tenant_id)}
    )

    await db.commit()

    logger.info(
        "tenant erased",
        extra={
            "tenant_id": str(tenant_id),
            "tenant_name": tenant_name,
            "schema_name": schema_name,
            "erased_by": payload.get("sub")
        }
    )