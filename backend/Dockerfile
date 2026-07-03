# === Build stage ===
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml .

# Install dependencies into a virtual environment
RUN uv venv .venv && \
    uv pip install --python .venv/bin/python -e .

# === Runtime stage ===
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv .venv

# Copy application code
COPY app/ app/
COPY alembic.ini .

# Create uploads directory
RUN mkdir -p uploads

# Set PATH to use the venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000

# Run migrations then start the server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2