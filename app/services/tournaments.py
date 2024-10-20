from sqlmodel import col, select

from app.database import get_session
from app.models import Tournament
from app.models.tournament import TournamentCreate


async def add_tournament(data: TournamentCreate) -> Tournament:
    async with get_session() as session:
        tournament = Tournament(**data.model_dump())
        session.add(tournament)

        await session.commit()
        await session.refresh(tournament)

        return tournament


async def get_tournament(tournament_id: str) -> Tournament:
    async with get_session() as session:
        stmt = select(Tournament).where(Tournament.id == tournament_id)
        tournament = await session.scalar(stmt)

        return tournament


async def get_tournaments() -> list[Tournament]:
    async with get_session() as session:
        stmt = select(Tournament)
        tournaments = (await session.scalars(stmt)).all()

        return tournaments


async def get_tournaments_with_table_url() -> list[Tournament]:
    async with get_session() as session:
        stmt = select(Tournament).where(col(Tournament.table_url).is_not(None))
        tournaments = (await session.scalars(stmt)).all()

        return tournaments


async def update_tournament_name(tournament_id: str, name: str) -> Tournament:
    async with get_session() as session:
        stmt = select(Tournament).where(Tournament.id == tournament_id)
        tournament = await session.scalar(stmt)

        tournament.name = name

        await session.commit()
        await session.refresh(tournament)

        return tournament


async def update_tournament_year(tournament_id: str, year: int) -> Tournament:
    async with get_session() as session:
        stmt = select(Tournament).where(Tournament.id == tournament_id)
        tournament = await session.scalar(stmt)

        tournament.year = year

        await session.commit()
        await session.refresh(tournament)

        return tournament


async def update_tournament_table_url(tournament_id: str, table_url: str) -> Tournament:
    async with get_session() as session:
        stmt = select(Tournament).where(Tournament.id == tournament_id)
        tournament = await session.scalar(stmt)

        tournament.table_url = table_url

        await session.commit()
        await session.refresh(tournament)

        return tournament


async def delete_tournament(tournament_id: str) -> Tournament:
    async with get_session() as session:
        stmt = select(Tournament).where(Tournament.id == tournament_id)
        tournament = await session.scalar(stmt)

        await session.delete(tournament)
        await session.commit()

        return tournament
