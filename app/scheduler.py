from aiogram import Bot
from aiogram.types import LinkPreviewOptions
from emoji import emojize

from app.messages.matches import build_links, build_string
from app.services.matches import get_today_matches, load_matches_from_url
from app.services.tournaments import get_tournaments_with_table_url
from app.services.users import get_notification_users


async def scheduled_job(bot: Bot):
    users = await get_notification_users()

    for user in users:
        if not user.tournament_id:
            continue

        matches = await get_today_matches(user.tournament_id)
        if not matches:
            continue

        matches_list = "\n".join([await build_string(match) for match in matches])
        text = f":tear-off_calendar: Сегодняшние матчи:\n{matches_list}"

        await bot.send_message(user.id, emojize(text))
        await bot.send_message(
            user.id,
            build_links(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )


async def update_all_matches():
    tournaments = await get_tournaments_with_table_url()

    for tournament in tournaments:
        await load_matches_from_url(tournament.id)

    print(f"Matches updated for {len(tournaments)} tournaments")
