import asyncio
import getpass

from db.basedb import get_session
from db.models.user import User
from sqlalchemy import select


async def create_superuser() -> None:
    superuser_name = input("Enter superuser login: ")
    superuser_password = getpass.getpass("Enter superuser password: ")

    async for session in get_session():
        query = select(User).filter_by(login=superuser_name)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            print("Superuser already exists!")
            return

        superuser = User(login=superuser_name, is_superuser=True)
        superuser.set_password(superuser_password)

        session.add(superuser)
        await session.commit()
        print("Superuser created successfully!")


if __name__ == "__main__":
    asyncio.run(create_superuser())
