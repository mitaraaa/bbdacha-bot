import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.handlers.preferences import router as preferences
from app.handlers.schedule import router as schedule
from app.handlers.tournament import router as tournament
from app.scheduler import scheduled_job, update_all_matches
from app.settings import settings

dp = Dispatcher()

cron_trigger = CronTrigger(
    year="*",
    month="*",
    day="*",
    hour=9,
    minute=0,
    second=0,
    timezone="Europe/Moscow",
)

interval_trigger = IntervalTrigger(hours=1, timezone="Europe/Moscow")


async def main() -> None:
    bot = Bot(
        token=settings.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
    )

    dp.include_routers(preferences, tournament, schedule)
    await bot.set_my_commands(settings.COMMANDS)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    scheduler.add_job(
        scheduled_job,
        trigger=cron_trigger,
        args=(bot,),
        name="send_today_matches",
    )

    scheduler.add_job(
        update_all_matches,
        trigger=interval_trigger,
        name="update_all_matches",
    )

    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
