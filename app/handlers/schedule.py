from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.messages.matches import (
    send_matches,
    send_tommorow_matches,
    send_upcoming_matches,
)
from app.messages.preferences import send_start_message
from app.services import matches
from app.services.users import add_user, get_user
from app.utils import TIMEZONE

router = Router()


@router.message(Command("today"))
async def today(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await add_user(message.from_user.id)

        await send_start_message(message)
        return

    matches_list = await matches.get_today_matches(user.tournament_id)
    await send_matches(message, matches_list)


@router.message(Command("soon"))
async def upcoming_matches(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await add_user(message.from_user.id)

        await send_start_message(message)
        return

    matches_list = await matches.get_upcoming_matches(user.tournament_id, 3)
    await send_upcoming_matches(message, matches_list)


@router.message(Command("tomorrow"))
async def tomorrow_matches(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await add_user(message.from_user.id)

        await send_start_message(message)
        return

    matches_list = await matches.get_matches_by_date(
        user.tournament_id, datetime.now(TIMEZONE) + timedelta(days=1)
    )
    await send_tommorow_matches(message, matches_list)
