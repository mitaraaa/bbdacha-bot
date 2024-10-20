from aiogram.types import Message
from emoji import emojize

from app.keyboards.preferences import notifications_keyboard, preferences_keyboard
from app.keyboards.tournaments import tournaments_selection
from app.services.tournaments import get_tournament
from app.services.users import get_user, update_selected_tournament


async def send_start_message(message: Message):
    text = emojize(
        ":waving_hand: Привет\\! Я \\- бот, который поможет тебе следить за расписанием матчей\\. \n"
        "Но прежде всего, хочешь ли ты подписаться на уведомления о матчах?"
    )

    await message.answer(text, reply_markup=notifications_keyboard())


async def send_help_message(message: Message):
    text = emojize(
        ":red_question_mark: Я могу помочь тебе следить за расписанием матчей\\. \n\n"
        "Просто используй команды:\n"
        "/today \\- для просмотра сегодняшних матчей\n"
        "/tomorrow \\- для просмотра матчей на завтра\n"
        "/soon \\- для просмотра предстоящих матчей\n"
        "/preferences \\- для настройки уведомлений и выбора турнира"
    )

    await message.answer(text)


async def enable_notifications_message(message: Message):
    await message.edit_text(
        emojize(
            ":bell: Уведомления включены\\. Теперь ты будешь получать уведомления о матчах\\."
        )
    )


async def disable_notifications_message(message: Message):
    await message.edit_text(
        emojize(
            ":bell_with_slash: Уведомления отключены\\. Ты не будешь получать уведомления о матчах\\."
        )
    )


async def send_preferences_message(
    message: Message, user_id: int, update: bool = False
):
    user = await get_user(user_id)
    tournament = None

    if user.tournament_id:
        tournament = await get_tournament(user.tournament_id)

        if not tournament:
            await update_selected_tournament(user_id, None)

    text = emojize(
        ":gear: Настройки\n\n"
        f"Выбранный турнир: {tournament.name if tournament else "Не выбран"}\n"
        f"Уведомления: {'Включены' if user.notifications else 'Отключены'}"
    )

    if update:
        await message.edit_reply_markup(
            reply_markup=await preferences_keyboard(user_id)
        )
        return

    await message.answer(text, reply_markup=await preferences_keyboard(user_id))


async def send_tournament_selection_message(message: Message):
    text = emojize(":game_die: Выбери турнир, за которым хочешь следить\\. \n\n")

    await message.answer(text, reply_markup=await tournaments_selection())
