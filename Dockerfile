FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY pyproject.toml ./

RUN uv pip install --system --no-cache .

COPY src/ ./src/

RUN chown -R appuser:appgroup /app

USER appuser

CMD ["python", "-m", "src.app"]
