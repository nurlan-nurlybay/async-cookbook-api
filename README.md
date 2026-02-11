# Async Cookbook API 🍳

![System Architecture](UML.png)

A high-performance, asynchronous REST API for managing recipes and newsletter subscriptions. Built with **FastAPI**, **Docker**, **PostgreSQL**, **Redis**, and **Celery**.

## 🚀 Features

* **Async API:** Built on FastAPI with `async/await` for high concurrency.
* **Background Tasks:** Celery + Redis worker for sending weekly newsletters without blocking the API.
* **Database:** PostgreSQL with **SQLModel** (SQLAlchemy + Pydantic) for ORM.
* **Validation:** Strict data validation using Pydantic (Email format, min/max lengths).
* **Monitoring:** Full observability stack with **Prometheus** metrics, **Grafana** dashboards, and **Sentry** error tracking.
* **Testing:** Comprehensive `pytest` suite with **45 assertions** covering security, logic, and data integrity.

## 🛠️ Tech Stack

* **Language:** Python 3.12
* **Framework:** FastAPI
* **Database:** PostgreSQL (AsyncPG driver)
* **Queue:** Redis & Celery
* **Containerization:** Docker & Docker Compose

## 📂 Project Structure

```text
├── app/
│   ├── api/            # Route handlers (v1)
│   ├── core/           # Config, Security, DB connection
│   ├── models/         # SQLModel Database Tables
│   ├── schemas/        # Pydantic Request/Response schemas
│   ├── services/       # Business logic (Newsletter, etc.)
│   ├── worker.py       # Celery task definitions
│   └── main.py         # App entry point
├── tests/              # Pytest suites
├── docker-compose.yml  # Infrastructure orchestration
└── requirements.txt    # Python dependencies
```

## ⚡ Quick Start

### 1. Run with Docker (Recommended)

This spins up the API, DB, Redis, Worker, Prometheus, and Grafana automatically.

```bash
docker compose up -d --build
```

- **API Docs:** http://localhost:8000/docs
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090

### 2. Run Tests

The test suite uses an in-memory SQLite database and Mocks, so it runs instantly without needing the heavy Docker stack.

```bash
# Install dependencies
pip install -r requirements.txt

# Run the suite
pytest -v
```

## 🧪 Testing Strategy

The project includes a robust test suite with 45 assertions:

- **test_recipes.py:**
    - **Parameterized Testing:** Validates edge cases (empty names, negative cooking times).
    - **Security:** Verifies 401 Unauthorized vs 403 Forbidden responses.
    - **Cascade Delete:** Ensures deleting a Recipe removes its Ingredients.

- **test_subscribers.py:**
    - **Validation:** Rejects malformed emails (missing @, empty strings) with 422.
    - **Business Logic:** Prevents duplicate subscriptions (409 Conflict).

- **test_worker.py:**
    - **Mocking:** Tests the email service logic without sending real emails.
    - **Ranking Algorithm:** Verifies the worker correctly identifies top-viewed recipes.

## 📊 Monitoring

The application exposes Prometheus metrics at `/metrics`.

- **Custom Metric:** `total_subscribers_added_total` (Counter) tracks growth.
- **Latency:** Tracks HTTP request duration and status codes.

## 🔒 Security

- **Middleware:** Custom middleware to log request timing and catch unhandled exceptions.
- **Authentication:** Admin routes are protected via `X-Admin-Key` header.
- **Validation:** Inputs are sanitized via Pydantic models (e.g., `cooking_time > 0`).
