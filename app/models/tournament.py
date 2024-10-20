from typing import TYPE_CHECKING, Optional

import nanoid
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models import Match


class TournamentCreate(BaseModel):
    name: str
    year: int
    table_url: Optional[str] = None


class Tournament(SQLModel, table=True):
    __tablename__ = "tournaments"

    id: str = Field(primary_key=True, default_factory=nanoid.generate)

    name: str
    year: int

    table_url: Optional[str] = None

    matches: list["Match"] = Relationship(back_populates="tournament")
