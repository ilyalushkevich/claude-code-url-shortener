# Shortly — URL Shortener

A minimal URL shortener built with FastAPI, PostgreSQL, and TailwindCSS.

## Features

- Shorten any URL with a 6-character random code
- Optional custom short codes (3–20 alphanumeric characters)
- Optional expiry (in days)
- Click tracking
- REST API + web UI
- Link stats page

---

## Local Setup

### Prerequisites

- Python 3.12+
- PostgreSQL running locally

### Steps

```bash
# 1. Clone and enter the project
cd url-shortener

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
touch .env
# Edit .env with your DATABASE_URL, BASE_URL, SECRET_KEY

# 5. Create the database (psql or your preferred client)
createdb urlshortener

# 6. Run migrations (optional — app auto-creates tables on startup)
alembic upgrade head

# 7. Start the server
uvicorn app.main:app --reload
```

Open http://localhost:8000 in your browser.  
API docs: http://localhost:8000/docs

---

## Docker Setup

```bash
# Build and start all services (postgres + app)
docker compose up --build

# To run in the background
docker compose up --build -d
```

Open http://localhost:8000 — the app connects to the `db` container automatically.

To stop:

```bash
docker compose down
```

To wipe the database volume too:

```bash
docker compose down -v
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/shorten` | Create a short link |
| `GET` | `/api/links` | List all links (`?skip=0&limit=20`) |
| `GET` | `/api/links/{code}/stats` | Stats for one link |
| `DELETE` | `/api/links/{code}` | Deactivate a link |
| `GET` | `/{code}` | Redirect to original URL |

### POST /api/shorten

```json
{
  "url": "https://example.com/very/long/path",
  "custom_code": "my-link",
  "expires_in_days": 30
}
```

Response `201`:

```json
{
  "short_url": "http://localhost:8000/my-link",
  "short_code": "my-link",
  "original_url": "https://example.com/very/long/path",
  "expires_at": "2024-02-01T00:00:00Z"
}
```

---

## Project Structure

```
url-shortener/
├── app/
│   ├── main.py          # FastAPI app + lifespan
│   ├── config.py        # Settings (pydantic-settings)
│   ├── database.py      # Async SQLAlchemy engine + session
│   ├── models.py        # ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── crud.py          # Database operations
│   ├── router/
│   │   ├── api.py       # REST API routes (/api/...)
│   │   └── web.py       # Web UI + redirect routes
│   └── templates/
│       ├── base.html
│       ├── index.html
│       └── stats.html
├── alembic/             # Database migrations
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```
