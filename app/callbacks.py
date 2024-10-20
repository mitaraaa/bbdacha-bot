from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData


class TournamentAction(str, Enum):
    # User selects tournament to view
    select = "select"

    # Admin actions
    view = "view"
    create = "create"
    refetch = "refetch"
    delete = "delete"

    update_year = "update_year"
    update_name = "update_name"
    update_url = "update_url"

    confirm = "confirm"
    cancel = "cancel"
    back = "back"


class NotificationCallback(CallbackData, prefix="notification"):
    action: str
    from_start: bool = False


class TournamentCallback(CallbackData, prefix="tournament"):
    action: str = TournamentAction.select

    tournament_id: Optional[str] = None
    soon_only: bool = False


class TournamentSelectionCallback(CallbackData, prefix="tournament_selection"):
    pass
