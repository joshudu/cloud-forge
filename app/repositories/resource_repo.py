from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.repositories.base import BaseRepository
from app.models.resource import Resource, ResourceType

class ResourceRepository(BaseRepository[Resource]):
    def __init__(self, db: AsyncSession):
        super().__init__(Resource, db)

    async def get_by_project(self, project_id: UUID) -> List[Resource]:
        result = await self.db.execute(
            select(Resource).where(
                Resource.project_id == project_id,
                Resource.is_active == True
            )
        )
        return result.scalars().all()

    async def get_by_type(self, resource_type: ResourceType) -> List[Resource]:
        result = await self.db.execute(
            select(Resource).where(Resource.resource_type == resource_type)
        )
        return result.scalars().all()