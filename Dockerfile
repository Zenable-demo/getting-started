# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS builder

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

ARG DEV_MODE=false
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
      extras=""; \
      if [[ "$DEV_MODE" != "true" ]]; then extras="--no-dev"; fi; \
      uv sync --frozen --no-install-project ${extras}

COPY "./src/getting_started" "/app/getting_started"
COPY "./src/main.py" "/app/main.py"

# Install the project with the project included
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
      extras=""; \
      if [[ "$DEV_MODE" != "true" ]]; then extras="--no-dev"; fi; \
      uv sync --frozen ${extras}

ARG TARGETPLATFORM
ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim-bookworm

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

# Python envs
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR "/app"

# Copy the virtual environment from builder
COPY --from=builder --chown=app:app /app /app

# Create app user
RUN groupadd -r app && useradd -r -g app app

# Metadata
ARG NAME="getting_started"
ARG DESCRIPTION="A playground for getting started with Zenable"
ARG TIMESTAMP
ARG COMMIT_HASH
ENV SERVICE="${NAME}"
ENV TIMESTAMP="${TIMESTAMP}"
ENV COMMIT_HASH="${COMMIT_HASH}"
ENV VERSION="${COMMIT_HASH}"

# These align with https://github.com/opencontainers/image-spec/blob/main/annotations.md
LABEL org.opencontainers.image.title="${NAME}"
LABEL org.opencontainers.image.description="${DESCRIPTION}"
LABEL org.opencontainers.image.created="${TIMESTAMP}"
LABEL org.opencontainers.image.vendor="Zenable Inc"
LABEL org.opencontainers.image.url="https://github.com/zenable-demo/getting_started"
LABEL org.opencontainers.image.source="https://github.com/zenable-demo/getting_started/tree/${COMMIT_HASH}"
LABEL org.opencontainers.image.revision="${COMMIT_HASH}"
LABEL org.opencontainers.image.licenses="MIT"

USER app

ENTRYPOINT ["python3", "/app/main.py"]
