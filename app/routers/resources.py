from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.auth.dependencies import get_tenant_db, get_current_user_payload
from app.repositories.resource_repo import ResourceRepository
from app.repositories.project_repo import ProjectRepository
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse
from typing import List
import json

router = APIRouter(prefix="/resources", tags=["resources"])

@router.post("/", response_model=ResourceResponse)
async def create_resource(
    resource_data: ResourceCreate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_tenant_db),
):
    # Verify project exists
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(resource_data.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    resource = Resource(
        name=resource_data.name,
        resource_type=resource_data.resource_type,
        project_id=resource_data.project_id,
        configuration=json.dumps(resource_data.configuration) if resource_data.configuration else None,
        created_by=payload.get("sub"),
    )

    repo = ResourceRepository(db)
    return await repo.create(resource)

@router.get("/project/{project_id}", response_model=List[ResourceResponse])
async def list_resources_by_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_tenant_db),
):
    repo = ResourceRepository(db)
    return await repo.get_by_project(project_id)

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: UUID,
    db: AsyncSession = Depends(get_tenant_db),
):
    repo = ResourceRepository(db)
    resource = await repo.get_by_id(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return resource

@router.patch("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: UUID,
    resource_data: ResourceUpdate,
    db: AsyncSession = Depends(get_tenant_db),
):
    repo = ResourceRepository(db)
    resource = await repo.get_by_id(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    update_data = resource_data.model_dump(exclude_unset=True)
    if "configuration" in update_data and update_data["configuration"]:
        update_data["configuration"] = json.dumps(update_data["configuration"])

    for field, value in update_data.items():
        setattr(resource, field, value)

    await db.commit()
    await db.refresh(resource)
    return resource