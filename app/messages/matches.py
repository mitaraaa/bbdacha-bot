from aiogram.types import LinkPreviewOptions, Message
from emoji import emojize

from app.models.match import Match
from app.utils import TIMEZONE, escape_markdown


def build_string(match: Match):
    team_a = escape_markdown(match.team_a) or "TBD"
    team_b = escape_markdown(match.team_b) or "TBD"
    score_a = f" {match.score_a}" if match.score_a is not None else ""
    score_b = f"{match.score_b} " if match.score_b is not None else ""
    best_of = escape_markdown(
        f" (bo{match.best_of})" if match.best_of and match.best_of > 1 else ""
    )
    time = match.date.astimezone(TIMEZONE).strftime("%H:%M") if match.date else "TBD"

    return f"{time}: *{team_a}* {score_a} vs {score_b} *{team_b}*{best_of}"


def build_links():
    return emojize(
        ":television: Смотреть игры можно тут:\n\n"
        "TWITCH\n"
        "[BetBoom\\_ru](https://bit.ly/3ythdfx)\n"
        "[BetBoom\\_ru2](https://bit.ly/3M7Friu)\n\n"
        "YOUTUBE\n"
        "[YouTube](https://bit.ly/4eXR1db)"
    )


async def send_matches(message: Message, matches: list[Match] | None):
    if not matches:
        await message.answer(emojize("Сегодня матчей нет :sleeping_face:"))
        return

    matches_list = "\n".join([build_string(match) for match in matches])
    text = f":tear-off_calendar: Сегодняшние матчи:\n{matches_list}"

    await message.answer(emojize(text))
    await message.answer(
        build_links(), link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


async def send_upcoming_matches(message: Message, matches: list[Match] | None):
    if not matches:
        await message.answer(emojize("В ближайшее время матчей нет :sleeping_face:"))
        return

    matches = [
        match for match in matches if any([match.team_a, match.team_b, match.date])
    ]

    matches_list = "\n".join([build_string(match) for match in matches])
    text = f":tear-off_calendar: Расписание на ближайшие 3 часа:\n{matches_list}"

    await message.answer(emojize(text))
    await message.answer(
        build_links(), link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


async def send_tommorow_matches(message: Message, matches: list[Match] | None):
    if not matches:
        await message.answer(emojize("Завтра матчей нет :sleeping_face:"))
        return

    matches_list = "\n".join([build_string(match) for match in matches])
    text = f":tear-off_calendar: Матчи на завтра:\n{matches_list}"

    await message.answer(emojize(text))
    await message.answer(
        build_links(), link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
