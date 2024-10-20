from datetime import datetime
from typing import TYPE_CHECKING, Optional

import nanoid
from pydantic import BaseModel
from sqlalchemy import TIMESTAMP, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models import Tournament


class MatchCreate(BaseModel):
    team_a: Optional[str] = None
    team_b: Optional[str] = None

    score_a: Optional[int] = None
    score_b: Optional[int] = None

    best_of: Optional[int] = 3
    type: str = "qualifier"  # qualifier, round robin, rr tiebreakers, playoffs

    stream_link: Optional[str] = None
    stream_link_en: Optional[str] = None

    tournament_id: str

    date: Optional[datetime] = None


class Match(SQLModel, table=True):
    __tablename__ = "matches"

    id: str = Field(primary_key=True, default_factory=nanoid.generate)

    team_a: Optional[str] = None
    team_b: Optional[str] = None

    score_a: Optional[int] = None
    score_b: Optional[int] = None

    best_of: Optional[int]
    type: str = "qualifier"

    stream_link: Optional[str] = None
    stream_link_en: Optional[str] = None

    tournament_id: str = Field(foreign_key="tournaments.id")
    tournament: "Tournament" = Relationship(back_populates="matches")

    date: Optional[datetime] = Field(
        sa_column=Column("date", TIMESTAMP(timezone=True), nullable=True)
    )
