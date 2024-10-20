from aiogram.types import BotCommand
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: str

    DATABASE_URL: str
    ALEMBIC_DATABASE_URL: str

    COMMANDS: list[BotCommand] = [
        BotCommand(command="/today", description="Матчи на сегодня"),
        BotCommand(command="/tomorrow", description="Матчи на завтра"),
        BotCommand(command="/soon", description="Ближайшие матчи"),
        BotCommand(command="/start", description="Начать диалог"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/preferences", description="Открыть меню настроек"),
    ]

    SECRET_ADMIN_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
