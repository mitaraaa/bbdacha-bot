from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.callbacks import (
    NotificationCallback,
    TournamentCallback,
    TournamentSelectionCallback,
)
from app.messages.preferences import (
    disable_notifications_message,
    enable_notifications_message,
    send_help_message,
    send_preferences_message,
    send_start_message,
    send_tournament_selection_message,
)
from app.services.tournaments import get_tournament
from app.services.users import (
    add_user,
    get_user,
    update_admin_privileges,
    update_notification_preference,
    update_selected_tournament,
)
from app.settings import settings

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await add_user(message.from_user.id)

        await send_start_message(message)
        return

    await send_help_message(message)


@router.message(Command("help"))
async def help(message: Message):
    await send_help_message(message)


@router.message(Command("preferences"))
async def preferences(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await send_start_message(message)
        return

    await send_preferences_message(message, user.id)


@router.message(Command("op"))
async def get_admin_privileges(message: Message):
    user = await get_user(message.from_user.id)

    if not user or user.is_admin:
        return

    password = message.text.split(" ")[1]

    if password == settings.SECRET_ADMIN_PASSWORD:
        await update_admin_privileges(message.from_user.id, True)
        await message.answer(
            "Теперь у вас есть права администратора\\! Введите /tournaments для управления турнирами"
        )


@router.callback_query(NotificationCallback.filter(F.action == "enable"))
async def enable_notifications(
    callback: CallbackQuery, callback_data: NotificationCallback
):
    await update_notification_preference(callback.from_user.id, True)

    await callback.answer("Уведомления включены")

    if callback_data.from_start:
        await enable_notifications_message(callback.message)
        await send_tournament_selection_message(callback.message)
    else:
        await send_preferences_message(
            callback.message, callback.from_user.id, update=True
        )


@router.callback_query(NotificationCallback.filter(F.action == "disable"))
async def disable_notifications(
    callback: CallbackQuery, callback_data: NotificationCallback
):
    await update_notification_preference(callback.from_user.id, False)

    await callback.answer("Уведомления отключены")

    if callback_data.from_start:
        await disable_notifications_message(callback.message)
        await send_tournament_selection_message(callback.message)
    else:
        await send_preferences_message(
            callback.message, callback.from_user.id, update=True
        )


@router.callback_query(TournamentSelectionCallback.filter())
async def open_tournament_select(callback: CallbackQuery):
    await callback.answer()
    await send_tournament_selection_message(callback.message)


@router.callback_query(TournamentCallback.filter(F.action == "select"))
async def select_tournament(callback: CallbackQuery, callback_data: TournamentCallback):
    tournament = await get_tournament(callback_data.tournament_id)

    await update_selected_tournament(callback.from_user.id, tournament.id)

    await callback.answer()
    await callback.message.edit_text(f"Турнир выбран: {tournament.name}")
