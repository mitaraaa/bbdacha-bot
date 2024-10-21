from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.callbacks import TournamentCallback
from app.messages.tournament import (
    send_tournament_creation_message,
    send_tournament_view,
    send_tournaments_message,
)
from app.models.tournament import TournamentCreate
from app.services import matches, tournaments
from app.services.tournaments import add_tournament
from app.services.users import get_user
from app.states import CreateTournament, UpdateTournament
from app.utils import escape_markdown, is_url, is_valid_year

router = Router()


@router.message(Command("tournaments"))
async def view_tournaments(message: Message):
    user = await get_user(message.from_user.id)

    if not user or not user.is_admin:
        return

    await send_tournaments_message(message)


@router.callback_query(TournamentCallback.filter(F.action == "view"))
async def view_tournament(callback: CallbackQuery, callback_data: TournamentCallback):
    await callback.answer()
    await send_tournament_view(callback.message, callback_data.tournament_id)


@router.callback_query(TournamentCallback.filter(F.action == "create"))
async def create_tournament(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateTournament.name)

    await callback.answer()
    await send_tournament_creation_message(callback.message, state)


@router.message(CreateTournament.name)
async def process_tournament_creation_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CreateTournament.year)

    await message.delete()

    await send_tournament_creation_message(message, state)


@router.message(CreateTournament.year)
async def process_tournament_creation_year(message: Message, state: FSMContext):
    year = message.text

    if not is_valid_year(year):
        await message.answer("Введите корректный год")
        return

    await state.update_data(year=year)
    await state.set_state(CreateTournament.table_url)

    await message.delete()

    await send_tournament_creation_message(message, state)


@router.message(CreateTournament.table_url)
async def process_tournament_creation_url(message: Message, state: FSMContext):
    url = message.text

    if not is_url(url) and not url == "-":
        await message.answer("Введите корректную ссылку на таблицу")
        return

    if url == "-":
        url = None

    await state.update_data(table_url=message.text)
    await state.set_state(CreateTournament.confirm)

    await message.delete()

    await send_tournament_creation_message(message, state)


@router.callback_query(TournamentCallback.filter(F.action == "confirm"))
async def confirm_tournament_creation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    tournament = await add_tournament(TournamentCreate(**data))

    await callback.answer()
    await callback.message.edit_text(
        f"Турнир {escape_markdown(tournament.name)} успешно создан\\!",
        reply_markup=None,
    )


@router.callback_query(TournamentCallback.filter(F.action == "cancel"))
async def cancel_tournament_creation(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.answer("Создание турнира отменено")
    await callback.message.delete()


@router.callback_query(TournamentCallback.filter(F.action == "back"))
async def back_to_previous_state(callback: CallbackQuery, state: FSMContext):
    if not await state.get_state():
        return

    current = await state.get_state()

    if current == CreateTournament.name:
        await state.clear()

        await callback.message.delete()
        await callback.answer("Создание турнира отменено")
        return

    if current == CreateTournament.year:
        await state.set_state(CreateTournament.name)
        await state.update_data(year=None)

    if current == CreateTournament.table_url:
        await state.set_state(CreateTournament.year)
        await state.update_data(table_url=None)

    await callback.answer()
    await send_tournament_creation_message(callback.message, state)


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    if not await state.get_state():
        return

    current = await state.get_state()
    await state.clear()

    if current in (
        CreateTournament.name,
        CreateTournament.year,
        CreateTournament.table_url,
        CreateTournament.confirm,
    ):
        await message.delete()
        await message.answer("Создание турнира отменено")
        return

    if current in (
        UpdateTournament.waiting_for_name,
        UpdateTournament.waiting_for_year,
        UpdateTournament.waiting_for_url,
        UpdateTournament.waiting_for_delete,
    ):
        await message.delete()
        await message.answer("Действие отменено")
        return


@router.callback_query(TournamentCallback.filter(F.action == "refetch"))
async def refetch_tournament(
    callback: CallbackQuery, callback_data: TournamentCallback
):
    await callback.bot.send_chat_action(
        callback.message.chat.id, ChatAction.UPLOAD_DOCUMENT
    )

    await matches.load_matches_from_url(callback_data.tournament_id)

    await callback.answer("Турнир обновлен")


@router.callback_query(TournamentCallback.filter(F.action == "update_name"))
async def update_tournament_name(
    callback: CallbackQuery, state: FSMContext, callback_data: TournamentCallback
):
    await state.set_state(UpdateTournament.waiting_for_name)
    await state.update_data(
        tournament_id=callback_data.tournament_id,
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
    )

    await callback.answer()
    await callback.message.answer("Введите новое название турнира:")


@router.message(UpdateTournament.waiting_for_name)
async def process_tournament_name(message: Message, state: FSMContext):
    name = message.text

    data = await state.get_data()
    await state.clear()

    await tournaments.update_tournament_name(data["tournament_id"], name)

    await message.bot.delete_message(data["chat_id"], data["message_id"])

    await message.answer("Название турнира успешно обновлено")
    await send_tournament_view(message, data["tournament_id"])


@router.callback_query(TournamentCallback.filter(F.action == "update_year"))
async def update_tournament_year(
    callback: CallbackQuery, state: FSMContext, callback_data: TournamentCallback
):
    await state.set_state(UpdateTournament.waiting_for_year)
    await state.update_data(
        tournament_id=callback_data.tournament_id,
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
    )

    await callback.answer()
    await callback.message.answer(
        "Введите новый год проведения турнира или /cancel для отмены:"
    )


@router.message(UpdateTournament.waiting_for_year)
async def process_tournament_year(message: Message, state: FSMContext):
    year = message.text

    if not is_valid_year(year):
        await message.answer("Введите корректный год")
        return

    data = await state.get_data()
    await state.clear()

    await tournaments.update_tournament_year(data["tournament_id"], int(year))

    await message.bot.delete_message(data["chat_id"], data["message_id"])

    await message.answer("Год проведения турнира успешно обновлен")
    await send_tournament_view(message, data["tournament_id"])


@router.callback_query(TournamentCallback.filter(F.action == "update_url"))
async def update_tournament_table_url(
    callback: CallbackQuery, state: FSMContext, callback_data: TournamentCallback
):
    await state.set_state(UpdateTournament.waiting_for_url)
    await state.update_data(
        tournament_id=callback_data.tournament_id,
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
    )

    await callback.answer()
    await callback.message.answer(
        "Введите новую ссылку на таблицу \\(должна начинаться с http:// или https://\\) или '-' чтобы удалить ссылку. Введите /cancel для отмены:"
    )


@router.message(UpdateTournament.waiting_for_url)
async def process_tournament_table_url(message: Message, state: FSMContext):
    url = message.text

    if not is_url(url) and not url == "-":
        await message.answer("Введите корректную ссылку на таблицу")
        return

    data = await state.get_data()
    await state.clear()

    if url == "-":
        url = None

    await tournaments.update_tournament_table_url(data["tournament_id"], url)

    await message.bot.delete_message(data["chat_id"], data["message_id"])

    await message.answer("Ссылка на таблицу успешно обновлена")
    await send_tournament_view(message, data["tournament_id"])


@router.callback_query(TournamentCallback.filter(F.action == "delete"))
async def delete_tournament(
    callback: CallbackQuery, state: FSMContext, callback_data: TournamentCallback
):
    await state.set_state(UpdateTournament.waiting_for_delete)
    await state.update_data(
        tournament_id=callback_data.tournament_id,
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
    )

    await callback.answer()
    await callback.message.answer(
        "Вы уверены, что хотите удалить турнир? Введите 'подтверждаю' для удаления"
    )


@router.message(UpdateTournament.waiting_for_delete)
async def process_tournament_deletion(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.text.lower() != "подтверждаю":
        await message.answer("Удаление отменено")

        await state.clear()
        return

    await tournaments.delete_tournament(data["tournament_id"])

    await message.bot.delete_message(data["chat_id"], data["message_id"])
    await message.answer("Турнир успешно удален")

    await state.clear()
