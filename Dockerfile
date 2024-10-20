FROM python:3.12-alpine3.19 as python-base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV UV_CACHE_DIR=/opt/uv-cache/

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN mkdir /fissure-bot
WORKDIR /fissure-bot

COPY pyproject.toml .

RUN --mount=type=cache,target=/opt/uv-cache/ \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv pip install --system --python 3.12 -r pyproject.toml

COPY alembic.ini .
COPY .env .

COPY ./app ./app
COPY ./migrations ./migrations