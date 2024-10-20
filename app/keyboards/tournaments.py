from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize

from app.callbacks import TournamentCallback
from app.services.tournaments import get_tournaments


async def tournaments_selection(action: str = "select"):
    tournaments = await get_tournaments()

    kb = InlineKeyboardBuilder()

    buttons = [
        InlineKeyboardButton(
            text=tournament.name,
            callback_data=TournamentCallback(
                tournament_id=tournament.id,
                action=action,
            ).pack(),
        )
        for tournament in tournaments
    ]

    if action == "view":
        buttons.append(
            InlineKeyboardButton(
                text=emojize(":plus: Добавить турнир"),
                callback_data=TournamentCallback(
                    action="create",
                ).pack(),
            )
        )

    kb.row(*buttons, width=1)

    return kb.as_markup()


async def tournament_settings(tournament_id: str):
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(
            text=emojize(":pencil: Изменить название"),
            callback_data=TournamentCallback(
                tournament_id=tournament_id,
                action="update_name",
            ).pack(),
        ),
        InlineKeyboardButton(
            text=emojize(":pencil: Изменить год"),
            callback_data=TournamentCallback(
                tournament_id=tournament_id,
                action="update_year",
            ).pack(),
        ),
        width=2,
    )

    kb.row(
        InlineKeyboardButton(
            text=emojize(":link: Редактировать ссылку"),
            callback_data=TournamentCallback(
                tournament_id=tournament_id,
                action="update_url",
            ).pack(),
        ),
    )

    kb.row(
        InlineKeyboardButton(
            text=emojize(":counterclockwise_arrows_button: Обновить матчи"),
            callback_data=TournamentCallback(
                tournament_id=tournament_id,
                action="refetch",
            ).pack(),
        ),
        InlineKeyboardButton(
            text=emojize(":wastebasket: Удалить"),
            callback_data=TournamentCallback(
                tournament_id=tournament_id,
                action="delete",
            ).pack(),
        ),
        width=2,
    )

    return kb.as_markup()


def confirm_creation():
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(
            text=emojize(":cross_mark: Нет"),
            callback_data=TournamentCallback(
                action="cancel",
            ).pack(),
        ),
        InlineKeyboardButton(
            text=emojize(":check_mark: Да"),
            callback_data=TournamentCallback(
                action="confirm",
            ).pack(),
        ),
    )

    return kb.as_markup()


def back_button():
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(
            text=emojize(":BACK_arrow: Назад"),
            callback_data=TournamentCallback(
                action="back",
            ).pack(),
        ),
    )

    return kb.as_markup()
