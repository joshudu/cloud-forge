from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.repositories.base import BaseRepository
from app.models.project import Project

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)

    async def get_by_name(self, name: str) -> Optional[Project]:
        result = await self.db.execute(
            select(Project).where(Project.name == name)
        )
        return result.scalar_one_or_none()

    async def get_active_projects(self) -> List[Project]:
        result = await self.db.execute(
            select(Project).where(Project.is_active == True)
        )
        return result.scalars().all()

    async def get_by_user(self, user_id: UUID) -> List[Project]:
        result = await self.db.execute(
            select(Project).where(Project.created_by == user_id)
        )
        return result.scalars().all()