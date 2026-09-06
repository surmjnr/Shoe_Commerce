# Sole House Shoe Store

A single-seller shoe commerce platform built as a Django REST API and React/TypeScript storefront. The database is the source of truth for prices, inventory, order totals, payment status, and administration.

## Stack

- Django 5 + Django REST Framework
- PostgreSQL 16
- React 18 + TypeScript + Vite
- TanStack Query for server state
- Zustand with localStorage persistence for the guest cart
- React Hook Form + Zod for checkout validation
- Celery + Redis for asynchronous notifications
- Docker Compose for local services

## Implemented

- Public product listing, server-side search, product details, categories, brands, images, sizes, and stock
- Guest cart with size-aware items and quantity limits
- Guest checkout with Pay on Delivery and Mobile Money selections
- Transactional backend order creation with row locking, server-side totals, delivery fees, and stock decrementing
- Order confirmation and phone-protected order tracking
- Admin JWT authentication, dashboard statistics, product management, image management, order status transitions, payment confirmation, and store settings APIs
- Mock payment and WhatsApp providers for local development, with provider abstractions for real integrations
- OpenAPI and Swagger endpoints
- Django Admin as a backup administration interface

The custom React admin dashboard and production payment/WhatsApp credentials remain follow-up work. The backend APIs required for those areas are present.

## Quick start with Docker

Prerequisites: Docker Desktop with Compose.

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open:

- Storefront: http://localhost:5173
- API: http://localhost:8000/api/v1/
- Swagger: http://localhost:8000/api/docs/
- Django Admin: http://localhost:8000/admin/

Create an administrator in another terminal:

```powershell
docker compose exec backend python manage.py createsuperuser
```

The default Compose database, Redis, and mock providers are intended for development only. Replace secrets and provider settings before deployment.

## Local development

### Backend

Use Python 3.12 or newer, PostgreSQL, and Redis. From `backend/`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements/development.txt
python manage.py migrate
python manage.py setup_store
python manage.py runserver
```

Run backend checks and tests with:

```powershell
python manage.py check
pytest
ruff check .
```

### Frontend

Use Node.js 20 or newer. From `frontend/`:

```powershell
npm install --legacy-peer-deps
npm run dev
```

Build and test:

```powershell
npm run build
npm test -- --run
npm run lint
```

`VITE_API_BASE_URL` defaults to `http://localhost:8000/api/v1` and can be overridden in `.env`.

## Main API routes

Public routes include:

- `GET /api/v1/products/`
- `GET /api/v1/products/{slug}/`
- `GET /api/v1/categories/`
- `GET /api/v1/settings/`
- `POST /api/v1/orders/`
- `POST /api/v1/orders/track/`
- `POST /api/v1/payments/initialize/`
- `POST /api/v1/payments/webhook/`

Administrator routes require a JWT and are grouped under `/api/v1/admin/` for products, orders, dashboard statistics, settings, and authentication.

## Configuration

Copy `.env.example` to `.env`. Never commit `.env`, payment credentials, WhatsApp tokens, database passwords, or Django secrets. The default development configuration uses local media storage, the mock payment provider, and the mock WhatsApp provider.

## Important operational notes

- Checkout revalidates every product, variant, price, and stock quantity on the server.
- Stock changes happen inside a database transaction with row-level locks.
- WhatsApp notification failure does not roll back a successful order; notifications are retried by Celery.
- Payment webhooks must be connected to a real provider and signature verification configured before production use.
- Run `python manage.py makemigrations` and commit generated migration files before deploying the database to a new environment. The current source tree still needs those generated migration files added in the deployment workflow.
