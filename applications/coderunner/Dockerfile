FROM python:3.13-alpine

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system dependencies
# bubblewrap: for sandboxing
# shadow: for useradd/groupadd
# build-base, libffi-dev: for building python extensions if needed
RUN apk add --no-cache \
    bubblewrap \
    shadow \
    build-base \
    libffi-dev

WORKDIR /app

# Ensure the sandbox group exists (runtime requirement config)
RUN groupadd -r sandbox_group || true

# Copy dependency files first to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies specifically for the project
# --frozen: Sync exactly from uv.lock
# --no-dev: Do not install development dependencies
# --no-install-project: Only install dependencies, not the app itself (yet)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application
COPY . .

# Place the virtual environment on the path
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

# Run with explicit path to venv python to ensure dependencies are found
CMD ["/app/.venv/bin/python", "main.py"]
