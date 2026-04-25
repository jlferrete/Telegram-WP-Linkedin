FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY pyproject.toml README.md ./
COPY app ./app
COPY migrations ./migrations

RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir .

RUN mkdir -p /data && chown -R app:app /app /data

USER app

ENTRYPOINT ["python", "-m", "app.main"]
CMD ["run-once", "--db-path", "/data/app.db"]
