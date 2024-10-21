from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from emoji import emojize

from app.keyboards.tournaments import (
    back_button,
    confirm_creation,
    tournament_settings,
    tournaments_selection,
)
from app.services.tournaments import get_tournament
from app.states import CreateTournament
from app.utils import escape_markdown


async def send_tournaments_message(message: Message):
    text = emojize(":game_die: Выберите турнир:")

    await message.answer(text, reply_markup=await tournaments_selection("view"))


async def send_tournament_view(message: Message, tournament_id: str):
    tournament = await get_tournament(tournament_id)

    link = (
        f"[просмотреть]({tournament.table_url})"
        if tournament.table_url
        else "не указана"
    )

    text = (
        f"*{escape_markdown(tournament.name)}*\n\n"
        f"Год: {tournament.year}\n"
        f"Ссылка на таблицу: {link}"
    )

    await message.answer(
        text,
        reply_markup=await tournament_settings(tournament_id),
    )


async def send_tournament_creation_message(message: Message, state: FSMContext):
    data = await state.get_data()
    current = await state.get_state()

    text = emojize(
        ":game_die: Создание нового турнира\n\n"
        f"Название турнира: {escape_markdown(data.get('name', 'введите название' if current == CreateTournament.name else 'не указано'))}\n"
        f"Год: {escape_markdown(data.get('year', 'введите год' if current == CreateTournament.year else 'не указан'))}\n"
        f"Ссылка на таблицу: {escape_markdown(data.get('table_url', 'введите ссылку или \"-\" чтобы оставить пустым' if current == CreateTournament.table_url else 'не указана'))}"
    )

    markup = back_button()
    if current == CreateTournament.confirm:
        text += "\n\nПодтвердить создание?"
        markup = confirm_creation()

    if current == CreateTournament.name:
        bot_message = await message.answer(text, reply_markup=markup)
        await state.update_data(
            bot_message_id=bot_message.message_id, chat_id=bot_message.chat.id
        )

    message_id = data.get("bot_message_id")
    chat_id = data.get("chat_id")
    if message_id:
        await message.bot.edit_message_text(
            text,
            message_id=message_id,
            chat_id=chat_id,
            reply_markup=markup,
        )
