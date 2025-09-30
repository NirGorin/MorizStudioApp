FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_MODULE="app.main:app" \
    WEB_CONCURRENCY=2 \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl netcat-openbsd \
    libpq-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt* /app/
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY . /app

COPY docker/entrypoint.sh /entrypoint.sh

EXPOSE 8000

CMD ["/bin/bash", "/entrypoint.sh"]
