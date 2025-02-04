from functools import lru_cache
from uuid import UUID

from db.models.role import Role, UserRole
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class RoleService:
    """
    Service class for managing role-related database operations.
    """

    async def get_by_name(self, session: AsyncSession, name: str) -> Role:
        """
        Retrieve a role by its name.

        :param session: Database session for executing queries.
        :param name: The name of the role.
        :return: Role object if found, otherwise None.
        """
        query = select(Role).filter_by(name=name)
        role_result = await session.execute(query)
        return role_result.scalar_one_or_none()

    async def get_user_roles(
        self, session: AsyncSession, user_id: UUID
    ) -> list[UserRole]:
        """
        Retrieve all roles assigned to a user.

        :param session: Database session for executing queries.
        :param user_id: The ID of the user.
        :return: List of UserRole objects associated with the user.
        """
        query = select(UserRole).filter_by(user_id=user_id)
        user_roles = await session.execute(query)
        return user_roles.scalars().all()

    async def assign_role(
        self, session: AsyncSession, user_id: UUID, role_id: UUID
    ) -> UserRole:
        """
        Assign a role to a user.

        :param session: Database session for executing queries.
        :param user_id: The ID of the user.
        :param role_id: The ID of the role.
        :return: The created UserRole object.
        """
        user_role = UserRole(user_id=user_id, role_id=role_id)
        session.add(user_role)
        await session.commit()
        return user_role

    async def revoke_role(
        self, session: AsyncSession, user_id: UUID, role_id: UUID
    ) -> None:
        """
        Revoke a role from a user.

        :param session: Database session for executing queries.
        :param user_id: The ID of the user.
        :param role_id: The ID of the role.
        """
        query = delete(UserRole).filter_by(user_id=user_id, role_id=role_id)
        await session.execute(query)
        await session.commit()


@lru_cache()
def get_role_service() -> RoleService:
    """
    Get an instance of RoleService.
    """
    return RoleService()
