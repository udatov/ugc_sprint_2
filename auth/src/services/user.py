from functools import lru_cache
from typing import Optional
from uuid import UUID

from db.models.oauth import OauthProvider, UserOauthProvider
from db.models.role import UserRole
from db.models.user import History, User
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class UserService:
    """
    Service class for managing user-related database operations.
    """

    async def get_by_login(self, session: AsyncSession, login: str) -> Optional[User]:
        """
        Retrieve a user by their login field.

        :param session: Database session for executing queries.
        :param login: The login of the user to retrieve.
        :return: The user object if found, otherwise None.
        """
        query = (
            select(User)
            .options(selectinload(User.role).selectinload(UserRole.role))
            .filter_by(login=login)
        )
        user = await session.execute(query)
        return user.scalar_one_or_none()

    async def create_or_update(
        self,
        session: AsyncSession,
        login: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
    ) -> User:
        """
        Create or update a user in the database.

        :param session: Database session for executing queries.
        :param login: The login of the user.
        :param password: The password for the user.
        :param first_name: The first name of the user (optional).
        :param last_name: The last name of the user (optional).
        :return: The created or updated User object.
        """
        existing_user = await self.get_by_login(session, login)

        if existing_user:
            existing_user.first_name = first_name or existing_user.first_name
            existing_user.last_name = last_name or existing_user.last_name
            existing_user.set_password(password)
            user = existing_user
        else:
            user = User(login=login, first_name=first_name, last_name=last_name)
            user.set_password(password)
            session.add(user)

        await session.commit()
        return user

    async def add_to_history(self, session: AsyncSession, user_id: UUID) -> History:
        """
        Add a login history record for a user.

        :param session: Database session for executing queries.
        :param user_id: The ID of the user.
        :return: The created History object.
        """
        history = History(user_id=user_id)
        session.add(history)
        await session.commit()
        return history

    async def get_login_history(
        self, session: AsyncSession, user_id: UUID
    ) -> list[History]:
        """
        Retrieve the login history for a user.

        :param session: Database session for executing queries.
        :param user_id: The ID of the user.
        :return: A list of History objects for the user.
        """
        query = (
            select(History)
            .where(History.user_id == user_id)
            .order_by(desc(History.created_at))
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_oauth(
        self, session: AsyncSession, email: str
    ) -> Optional[UserOauthProvider]:
        """
        Retrieve a user by email field.

        :param session: Database session for executing queries.
        :param email: The email of the user to retrieve.
        :return: The user object if found, otherwise None.
        """
        query = (
            select(UserOauthProvider)
            .options(selectinload(UserOauthProvider.user))
            .filter_by(email=email)
        )
        user = await session.execute(query)
        return user.scalar_one_or_none()

    async def get_oauth_provider_by_name(
        self, session: AsyncSession, name: str
    ) -> Optional[OauthProvider]:
        """
        Retrieve a OAuth provder by name field.

        :param session: Database session for executing queries.
        :param email: The name of the OAuth provider to retrieve.
        :return: The OauthProvider object if found, otherwise None.
        """
        query = select(OauthProvider).filter_by(name=name)
        provider = await session.execute(query)
        return provider.scalar_one_or_none()

    async def oauth_create_or_update(
        self,
        session: AsyncSession,
        user: User,
        oauth_provider: str,
        email: str,
        first_name: str,
        last_name: str,
    ) -> UserOauthProvider:
        """
        Create or update the OAuth user in the database.

        :param session: Database session for executing queries.
        :param user: User object to link oauth account.
        :param oauth_provider: Name of oauth provider.
        :param email: The email of the user.
        :param first_name: The first name of the user.
        :param last_name: The last name of the user.
        :param oauth_provider: The name of the OAuth provider.
        :return: The created or updated UserOauthProvider object.
        """
        oauth_user = await self.get_by_oauth(session, email)
        provider = await self.get_oauth_provider_by_name(session, oauth_provider)

        if oauth_user:
            oauth_user.first_name = first_name or oauth_user.first_name
            oauth_user.last_name = last_name or oauth_user.last_name
            oauth_user.oauthprovider = provider
        else:
            oauth_user = UserOauthProvider(
                email=email,
                first_name=first_name,
                last_name=last_name,
                user=user,
                oauthprovider=provider,
            )
            session.add(oauth_user)

        await session.commit()
        return oauth_user


@lru_cache()
def get_user_service() -> UserService:
    """
    Get an instance of UserService.
    """
    return UserService()
