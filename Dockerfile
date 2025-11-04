ARG VARIANT=3.13.2-slim-bookworm

# Base stage
FROM python:${VARIANT} AS base

COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /usr/local/bin/uv

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
COPY gunicorn.conf.py pyproject.toml ./

## Dev with mounted volumes and dev deps
FROM base AS dev
COPY requirements-dev.lock ./
RUN uv pip install --system -r requirements-dev.lock
COPY src ./src

# Production stage
FROM base AS prod
COPY pyproject.toml docs/README.md requirements.lock ./
RUN uv pip install --system --no-deps --no-compile -r requirements.lock
COPY src ./src

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
