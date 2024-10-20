from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    pass


class User(SQLModel, table=True):
    __tablename__ = "user_preferences"

    id: str = Field(primary_key=True)

    is_admin: bool = False

    notifications: bool = Field(default=False)

    tournament_id: Optional[str] = Field(
        sa_column=Column(
            "tournament_id",
            String,
            ForeignKey("tournaments.id", ondelete="SET NULL"),
        )
    )
