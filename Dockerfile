FROM python:3.12.4-slim-bookworm AS base

LABEL maintainer="georgiy@kuzora.ru"

ARG APP_PATH=/app \
    SOURCE_PATH=$APP_PATH/src \
    CONFIG_DIR_PATH= $SOURCE_PATH/config

WORKDIR $APP_PATH

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    pipx \
    && rm -rf /var/lib/apt/lists/* \
    && pipx install poetry==$POETRY_VERSION

COPY ./pyproject.toml ./poetry.lock ./

RUN poetry install --only main --all-extras --compile --no-root

ENV PYTHONPATH=$SOURCE_PATH \
    CONFIG_PATH=$CONFIG_DIR_PATH/config-local.yml \
    SECRETS_PATH=$CONFIG_DIR_PATH/secrets

COPY src .

EXPOSE 8000

ENTRYPOINT ["poetry", "run"]
CMD ["uvicorn", "app.service:app", "--host", "0.0.0.0", "--port", "8000"]
