<div dir="ltr">

# MorizStudioApp

FastAPI backend for multi-studio Pilates/fitness management with JWT auth, SQLAlchemy, Alembic, PostgreSQL, Redis, and AWS integrations. Includes an AI pipeline that generates trainee-specific training recommendations from medical data, stores artifacts in S3, and publishes events for notifications.

## Table of Contents

- [Overview](#overview)
- [Key Features (Current MVP)](#key-features-current-mvp)
- [Roadmap](#roadmap)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
  - [Run with Docker (recommended)](#run-with-docker-recommended)
  - [Run locally without Docker](#run-locally-without-docker)
- [Environment Variables](#environment-variables)
- [Database Migrations (Alembic)](#database-migrations-alembic)
- [Health & Observability](#health--observability)
- [Testing](#testing)
- [API Overview](#api-overview)
- [Architecture & Design Decisions](#architecture--design-decisions)
- [Security Notes](#security-notes)

---

## Overview

MorizStudioApp is a backend service designed for studio owners, trainers, and trainees. Studio owners can create studios and manage members. Trainees submit medical/limitations information, which triggers an AI flow that produces a plain-English summary and structured recommendations (JSON). AI outputs are stored in S3, events are published for downstream notifications (e.g., email).

---

## Key Features (Current MVP)

- **Studios:** Create and manage studio entities and assignments between owners/trainers/trainees.
- **Authentication & Authorization:** JWT (OAuth2 password flow) with roles (owner/admin/trainer/trainee) enforced in routers.
- **Trainee Profile & AI:** Accept medical/limitations data, trigger the AI pipeline (OpenAI) to produce recommendations, and persist pointers to artifacts.
- **AWS Integrations (foundations):** S3 for AI artifacts, SNS topic ARNs are configurable for event publishing, the code is structured to extend into SQS/Lambda/SES when needed.
- **Events Layer:** Centralized event publisher abstraction ready to map to AWS messaging.
- **Redis (optional):** Cache AI summaries (TTL-based) to reduce response times and recomputation.
- **Admin endpoints:** Curated, role-guarded management operations.
- **OpenAPI docs:** Available at `/docs` and `/openapi.json`.
- **Health endpoint:** `/healthz` for runtime checks and Docker healthchecks.

---

## Roadmap

- **Scheduling & Booking:** Class calendar, capacity management, waitlists, cancellations.
- **Payments & Subscriptions:** Stripe/credit-card processing, invoices, and webhooks.
- **AI Enhancements:** Personalization using history/preferences, adaptive recommendations.
- **Event-Driven Notifications:** Full SNS → SQS → Lambda → SES pipeline for robust fan-out.
- **Analytics:** Studio dashboards (churn, occupancy, revenue, retention KPIs).
- **DevOps:** Production-grade Docker/Compose, GitHub Actions CI/CD, Sentry/metrics.

---

## Tech Stack

- **Language/Framework:** Python 3.12, FastAPI, Uvicorn (dev)
- **DB/ORM/Migrations:** PostgreSQL 17, SQLAlchemy 2.x, Alembic
- **Cache:** Redis 7 (optional)
- **Cloud:** AWS S3/SNS (ready for SQS/Lambda/SES)
- **AI:** OpenAI API (default model: `gpt-4o-mini`)
- **Testing:** Pytest, Faker
- **Tooling:** Docker, docker-compose, Adminer

---

## Repository Structure

```text
app/
  core/
    settings.py          # Pydantic-settings based config
  routers/
    admin.py             # Admin endpoints & role guards
    auth.py              # OAuth2/JWT login, token issuance
    studios.py           # CRUD & assignments for studios
    trainee_profile.py   # Accept trainee data, trigger AI flow
    users.py             # Users & roles management
  services/
    ai_service.py        # Prompt building, OpenAI calls, JSON output
    aws_clients.py       # S3/SNS clients & helpers
    events.py            # Centralized event publishing/logging
  database.py            # Engine/SessionLocal/Base
  enums.py               # Domain enums (roles, levels, etc.)
  models.py              # SQLAlchemy models and relations
  schemas.py             # Pydantic v2 schemas
  main.py                # FastAPI app, include_router, /healthz

alembic/
  env.py
  versions/
  script.py.mako

docker/
  Dockerfile
  entrypoint.sh

tests/
  test_admin.py
  test_auth.py
  test_trainers.py
  test_trainer_limitation.py
  utils.py

README.md
docker-compose.yml
requirements.txt
dev-requirements.txt
alembic.ini
.env_example
Quick Start
Run with Docker (recommended)
Create .env from .env_example and fill in values.

Build & start services:

bash
Copy code
docker compose build
docker compose up -d
Access:

API docs: http://localhost:8000/docs

Health: http://localhost:8000/healthz

Adminer: http://localhost:8080 (server: db, credentials from .env)

Exposed ports: API 8000, Postgres 5433 → container 5432, Redis 6379.

Run locally without Docker
bash
Copy code
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
pip install -r dev-requirements.txt

# Ensure Postgres is running locally OR point DATABASE_URL to your instance.
export APP_MODULE=app.main:app
uvicorn ${APP_MODULE} --reload --port 8000
# Docs: http://127.0.0.1:8000/docs
Environment Variables
Minimal .env (see .env_example for full list):

dotenv
Copy code
# Database
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/morizstudioapp

# Auth / JWT
SECRET_KEY=change_me_in_prod
ALGORITHM=HS256

# OpenAI
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=YOUR_OPENAI_API_KEY

# AWS
AWS_REGION=il-central-1
S3_BUCKET=moriz-dev-core
S3_BUCKET_SUMMARIES=moriz-ai-summaries-dev
SNS_TOPIC_EVENTS_ARN=arn:aws:sns:il-central-1:<ACCOUNT_ID>:moriz-events
SNS_TOPIC_STUDIO_EMAILS_ARN=arn:aws:sns:il-central-1:<ACCOUNT_ID>:studio-emails
SNS_TOPIC_AI_SUMMARY_CREATED=arn:aws:sns:il-central-1:<ACCOUNT_ID>:ai-summary-created

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
AI_SUMMARY_CACHE_TTL_SECONDS=86400

# App / Docker
APP_ENV=development
APP_DEBUG=true
PORT=8000
APP_MODULE=app.main:app

# Postgres (docker-compose)
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db_name
Notes

For local development psycopg2-binary is convenient, for production prefer psycopg2 or the psycopg package.

Do not commit real secrets. Use a secret manager or environment-level configuration.

Database Migrations (Alembic)
Create a new revision:

bash
Copy code
alembic revision -m "add trainee profile tables"
Apply migrations:

bash
Copy code
alembic upgrade head
Check current status:

bash
Copy code
alembic current
Health & Observability
Healthcheck: /healthz returns HTTP 200 when healthy (used by Docker healthcheck).

Sentry (planned): sentry-sdk is listed in requirements, configure SENTRY_DSN to enable.

Testing
Run all tests:

bash
Copy code
pytest -q
Fixtures in tests/utils.py prepare an isolated DB and override dependencies. Coverage includes auth flows, admin, and trainer/limitations flows.

API Overview
Swagger UI exposes request/response schemas and try-it-out.

Main routers:

auth – create/login users, issue tokens.

studios – CRUD & assignments for studios.

trainee_profile – accept trainee data, trigger AI processing.

users – manage users and roles.

admin – role-guarded admin operations.

Example: login to obtain an access token

bash
Copy code
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo1234"
# => {"access_token":"...","token_type":"bearer"}
Use the token in Authorization: Bearer <token> for protected endpoints.

Architecture & Design Decisions
Layered design: routers (transport/API), services (domain/integrations), core/settings.py (configuration), models/schemas (data), database (infrastructure). Clear boundaries, easier testing, and future scaling.

Event-driven ready: services/events.py centralizes event publishing so it can be mapped to AWS SNS/SQS/Lambda without touching routers. Today the app can log/publish to SNS, extending to SQS/Lambda is straightforward.

AI as a service: ai_service.py isolates prompt construction, OpenAI calls, and deterministic JSON shaping so models/providers can be swapped with minimal impact.

S3 for AI artifacts: Store summaries/JSON as artifacts and keep lightweight pointers in the DB to decouple storage from compute.

Redis caching: Reduce AI recomputation and latency for repeated reads of trainee summaries.

PostgreSQL as primary DB: Strong relational consistency, migrations via Alembic, and a clear upgrade path to RDS.

Docker dev-parity: Compose includes api, db, redis, and adminer to mirror production-like environments locally.

Security Notes
Keep SECRET_KEY, OPENAI_API_KEY, and AWS credentials out of source control.

Use short-lived JWTs and a strong secret, consider token revocation strategies for production.

Use a least-privilege DB user, enforce TLS for external DB access.

Add CORS and rate limiting (e.g., Nginx/Redis/slowapi) before public exposure.

Author: Nir Gorin — A hands-on backend project demonstrating modern FastAPI practices, AI integration, and AWS-oriented architecture with a clear SaaS roadmap.

</div> ```