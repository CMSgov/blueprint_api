# syntax=docker/dockerfile:1
FROM python:3.11.0a7-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY . /code/
COPY pyproject.toml /code/

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev