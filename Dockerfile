FROM python:3.13-slim

ENV UV_INSTALL_DIR=/root/.local/bin \
    PATH=/root/.local/bin:/app/.venv/bin:$PATH \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

 WORKDIR /app

 RUN apt-get update && \
     apt-get install -y --no-install-recommends \
     build-essential \
     curl \
     python3-dev \
     && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY . .
RUN uv sync --locked --no-dev

EXPOSE 8000
CMD python -m src.storage.setup && uv run src/server.py 
