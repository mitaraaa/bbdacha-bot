import re
from datetime import datetime, timedelta

import pandas as pd
from pandas import DataFrame
from sqlmodel import extract, select

from app.database import get_session
from app.models import Match
from app.models.match import MatchCreate
from app.models.tournament import Tournament
from app.utils import TIMEZONE


async def add_match(data: MatchCreate) -> Match:
    async with get_session() as session:
        match = Match(**data.model_dump())
        session.add(match)

        await session.commit()
        await session.refresh(match)

        return match


async def add_matches(data: list[MatchCreate]) -> None:
    async with get_session() as session:
        matches = [Match(**match.model_dump()) for match in data]
        session.add_all(matches)

        await session.commit()


async def get_matches(tournament_id: str) -> list[Match]:
    async with get_session() as session:
        stmt = (
            select(Match)
            .where(Match.tournament_id == tournament_id)
            .order_by(Match.date)
        )

        matches = (await session.scalars(stmt)).all()

        return matches


async def get_matches_by_date(tournament_id: str, date: datetime) -> list[Match]:
    async with get_session() as session:
        stmt = (
            select(Match)
            .where(Match.tournament_id == tournament_id)
            .where(
                extract("year", Match.date) == date.year,
                extract("month", Match.date) == date.month,
                extract("day", Match.date) == date.day,
            )
            .order_by(Match.date)
        )

        matches = (await session.scalars(stmt)).all()

        return matches


async def get_today_matches(tournament_id: str) -> list[Match]:
    return await get_matches_by_date(tournament_id, datetime.now(TIMEZONE))


async def get_upcoming_matches(tournament_id: str, hours: int) -> list[Match]:
    async with get_session() as session:
        now = datetime.now(TIMEZONE)
        stmt = (
            select(Match)
            .where(Match.tournament_id == tournament_id)
            .where(Match.date >= now)
            .where(Match.date <= now + timedelta(hours=hours))
            .order_by(Match.date)
        )

        matches = (await session.scalars(stmt)).all()

        return matches


def get_schedule(url: str) -> DataFrame:
    schedule = (
        pd.read_html(url, attrs={"class": "waffle"}, skiprows=1)[0]
        .drop(["1"], axis=1)
        .dropna(axis=0, how="all")
    )

    schedule = schedule.replace({pd.NA: None, "": None, float("nan"): None})

    return schedule


def build_schedule(
    tournament_id: str, schedule: DataFrame, year: int
) -> list[MatchCreate]:
    schedule_items = []

    current_year = year
    prev_month = None

    def parse_date(date_str: str, year: int) -> datetime:
        return pd.to_datetime(f"{date_str} {year}", format="%B %d %Y", errors="coerce")

    for idx, row in schedule.iterrows():
        match_date = parse_date(row["Date"], current_year)

        if prev_month is not None and match_date.month < prev_month:
            current_year += 1

        prev_month = match_date.month
        schedule.loc[idx, "Date"] = parse_date(row["Date"], current_year)

    schedule["Time - MSK"] = schedule["Time - MSK"].apply(
        lambda t: t
        if pd.notna(t) and pd.Series(t).str.match(r"^\d{2}:\d{2}$").any()
        else None
    )

    for idx, row in schedule.iterrows():
        if pd.isna(row["Time - MSK"]):
            continue

        schedule.loc[idx, "Time - MSK"] = pd.to_datetime(
            f"{row['Date'].strftime('%Y-%m-%d')} {row['Time - MSK']}",
            format="%Y-%m-%d %H:%M",
            errors="coerce",
        ).tz_localize(TIMEZONE)

    for _, row in schedule.iterrows():
        best_of = re.search(r"\d+", row["Format"] or "")

        schedule_items.append(
            MatchCreate(
                team_a=row["Team A"],
                team_b=row["Team B"],
                score_a=row["Score"],
                score_b=row["Score.2"],
                type=row["Stage"],
                date=row["Time - MSK"],
                stream_link=row.get("Stream link - RU", None),
                stream_link_en=row.get("Stream link - EN", None),
                best_of=int(best_of.group(0)) if best_of else None,
                tournament_id=tournament_id,
            )
        )

    return schedule_items


async def load_matches_from_url(tournament_id: str) -> None:
    async with get_session() as session:
        stmt = select(Tournament).where(Tournament.id == tournament_id)
        tournament = await session.scalar(stmt)

        if not tournament.table_url:
            return

        schedule = get_schedule(tournament.table_url)
        schedule_items = build_schedule(tournament_id, schedule, tournament.year)

        stmt = select(Match).where(Match.tournament_id == tournament_id)
        existing_matches = (await session.scalars(stmt)).all()

        for match in existing_matches:
            await session.delete(match)
        await session.commit()

        await add_matches(schedule_items)
