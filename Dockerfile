FROM --platform=linux/amd64 python:3.10-slim-buster

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /usr/local

RUN pip install --upgrade pip && pip install poetry

COPY poetry.lock pyproject.toml /usr/local/

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-ansi --no-interaction

WORKDIR /code

COPY . /code/

RUN python3 manage.py collectstatic --no-input
