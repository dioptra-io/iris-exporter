FROM python:3.10
WORKDIR /app

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry install --no-root --no-dev && rm -rf /root/.cache/*
COPY iris_exporter iris_exporter
