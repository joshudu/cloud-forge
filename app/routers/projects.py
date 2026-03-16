from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.auth.dependencies import get_tenant_db, get_current_user_payload
from app.repositories.project_repo import ProjectRepository
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.cache import cache_get, cache_set, cache_invalidate, make_cache_key
from app.core.events import publish_event
from typing import List
import json

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_tenant_db),
):
    schema = payload.get("schema")
    repo = ProjectRepository(db)

    existing = await repo.get_by_name(project_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists"
        )

    project = Project(
        name=project_data.name,
        description=project_data.description,
        created_by=payload.get("sub"),
    )
    created = await repo.create(project)

    # Invalidate cache on create
    await cache_invalidate(f"{schema}:projects:*")

    # Publish event — fire and forget
    await publish_event("project.created", {
        "project_id": str(created.id),
        "tenant_id": payload.get("tenant_id"),
        "name": created.name,
    })

    return created


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_tenant_db),
):
    repo = ProjectRepository(db)
    return await repo.get_active_projects()

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_tenant_db),
):
    repo = ProjectRepository(db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_tenant_db),
):
    repo = ProjectRepository(db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Only update fields that were actually provided
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_tenant_db),
):
    repo = ProjectRepository(db)
    deleted = await repo.delete(project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )