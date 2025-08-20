ARG CODENAME=bookworm
ARG PY_VER=3.13
FROM python:${PY_VER}}-slim-${CODENAME}}

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=ghcr.io/astral-sh/uv:0.7.21 /uv /uvx /bin/
COPY pyproject.yaml /gvl/

RUN uv sync

# _THEN_ copy the source code
COPY src/ /app/src/
