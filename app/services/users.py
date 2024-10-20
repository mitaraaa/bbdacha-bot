from typing import Optional

from sqlmodel import col, select

from app.database import get_session
from app.models import User
from app.models.tournament import Tournament


async def add_user(user_id: str | int) -> User:
    async with get_session() as session:
        stmt = select(Tournament)
        tournaments = (await session.scalars(stmt)).all()

        user = User(id=str(user_id))

        if len(tournaments) == 1:
            user.tournament_id = tournaments[0].id

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user


async def get_user(user_id: str | int) -> Optional[User]:
    async with get_session() as session:
        user_id = str(user_id)

        stmt = select(User).where(User.id == user_id)
        user = await session.scalar(stmt)

        return user


async def get_notification_users() -> list[User]:
    async with get_session() as session:
        stmt = (
            select(User)
            .where(User.notifications == True)  # noqa
            .where(col(User.tournament_id).is_not(None))
        )
        users = await session.scalars(stmt)

        return users.all()


async def update_selected_tournament(
    user_id: str | int, tournament_id: str | None
) -> None:
    async with get_session() as session:
        user_id = str(user_id)

        stmt = select(User).where(User.id == user_id)
        user = await session.scalar(stmt)

        user.tournament_id = tournament_id

        await session.commit()


async def update_notification_preference(user_id: str | int, enabled: bool) -> None:
    async with get_session() as session:
        user_id = str(user_id)

        stmt = select(User).where(User.id == user_id)
        user = await session.scalar(stmt)

        user.notifications = enabled

        await session.commit()


async def update_admin_privileges(user_id: str | int, is_admin: bool) -> None:
    async with get_session() as session:
        user_id = str(user_id)

        stmt = select(User).where(User.id == user_id)
        user = await session.scalar(stmt)

        user.is_admin = is_admin

        await session.commit()
