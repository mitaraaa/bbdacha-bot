from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize

from app.callbacks import (
    NotificationCallback,
    TournamentSelectionCallback,
)
from app.services.users import get_user


def notifications_keyboard():
    kb = InlineKeyboardBuilder()

    kb.add(
        InlineKeyboardButton(
            text=emojize(":bell_with_slash: Выключить"),
            callback_data=NotificationCallback(
                action="disable", from_start=True
            ).pack(),
        ),
        InlineKeyboardButton(
            text=emojize(":bell: Включить"),
            callback_data=NotificationCallback(action="enable", from_start=True).pack(),
        ),
    )

    return kb.as_markup()


async def preferences_keyboard(user_id: int):
    user = await get_user(user_id)

    kb = InlineKeyboardBuilder()

    notifications_text = (
        ":bell_with_slash: Выкл. уведомления"
        if user.notifications
        else ":bell: Вкл. уведомления"
    )

    kb.add(
        InlineKeyboardButton(
            text=emojize(notifications_text),
            callback_data=NotificationCallback(
                action="disable" if user.notifications else "enable"
            ).pack(),
        ),
        InlineKeyboardButton(
            text=emojize(":game_die: Выбрать турнир"),
            callback_data=TournamentSelectionCallback().pack(),
        ),
    )

    return kb.as_markup()
