import re

import pytz

TIMEZONE = pytz.timezone("Europe/Moscow")


def escape_markdown(text: str | None) -> str:
    if not text:
        return text

    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def is_url(text: str) -> bool:
    return bool(
        re.match(
            r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
            text,
        )
    )


def is_valid_year(year: str) -> bool:
    return bool(re.match(r"^\d{4}$", year))
