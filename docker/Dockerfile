FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_MODULE="app.main:app" \
    WEB_CONCURRENCY=2 \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl ca-certificates netcat-openbsd \
    build-essential libpq-dev pkg-config \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt* /app/
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY . /app

COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
