# LibraryHub

**Intelligent Library Management System** — Full Stack Edition

A full-featured library system with authentication, book management (upload/borrow/return), user reviews, AI-powered summaries and sentiment analysis, and personalized recommendations.

## Features

- 🔐 **Auth** — JWT-based registration & login
- 📚 **Books** — Browse, search, filter by genre; upload PDF/EPUB files and cover images
- 📖 **Borrow/Return** — Track copies, borrow history
- ⭐ **Reviews** — 1-5 star ratings with text reviews; AI sentiment analysis per review
- 🤖 **AI Summaries** — Auto-generated book summaries and reader consensus (background tasks)
- 🎯 **Recommendations** — Hybrid engine: TF-IDF content similarity + collaborative filtering + user genre/author preferences
- 🔄 **Pluggable LLM** — Mock (default), Ollama, or OpenAI — change via one env var
- 🗄️ **Pluggable Storage** — Local filesystem (default) or AWS S3 — change via one env var

## Quick Start

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

Sign up, browse books, borrow, leave reviews, and get recommendations.

## Configuration

Copy `backend/.env.example` to `backend/.env` and adjust:

| Variable | Default | Description |
|---|---|---|
| `DB_URL` | postgres://... | PostgreSQL connection URL |
| `SECRET_KEY` | changeme | JWT signing key |
| `LLM_PROVIDER` | `mock` | `mock` \| `ollama` \| `openai` |
| `STORAGE_BACKEND` | `local` | `local` \| `s3` |
| `RECOMMENDATION_ENGINE` | `hybrid` | `hybrid` \| `llm` |

### LLM Providers

| Provider | Setup |
|---|---|
| `mock` | No config needed — simple hardcoded responses |
| `ollama` | Set `OLLAMA_BASE_URL`; run `docker compose exec ollama ollama pull llama3.2` |
| `openai` | Set `OPENAI_API_KEY` and optionally `OPENAI_MODEL` (default: `gpt-4o-mini`) |

### Storage Backends

| Backend | Setup |
|---|---|
| `local` | Files stored in `LOCAL_STORAGE_PATH` (default `./uploads`) |
| `s3` | Set `AWS_BUCKET` and `AWS_REGION`; uses boto3 with default credential chain |

## Run Without Docker

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # edit DB_URL etc.
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Architecture

### Backend (FastAPI + SQLAlchemy async)

```
backend/app/
  main.py              # App entry, CORS, lifespan
  db.py                # Async SQLAlchemy engine
  schemas.py           # Pydantic request/response models
  core/
    config.py          # Settings via pydantic-settings
    security.py        # JWT, password hashing
  models/
    user.py, book.py, review.py  # ORM models
  routers/
    auth, books, borrows, reviews, recommendations, preferences
  services/
    llm.py             # Pluggable LLM (mock/ollama/openai)
    storage.py         # Pluggable storage (local/s3)
    recommendations.py # Hybrid + LLM recommendation engines
```

### Frontend (Next.js 14 + Tailwind)

```
frontend/src/
  app/
    page.tsx              # Book catalog
    books/[id]/page.tsx   # Book detail + reviews
    books/add/page.tsx    # Add book form
    borrow/page.tsx       # My borrow history
    recommendations/      # Personalized picks
    profile/              # User preferences
    auth/login|register/
  lib/
    api.ts                # Axios client + all API calls
    auth.ts               # Zustand auth store
```

### Database Schema

- `users` — id, email, username, hashed_password, is_admin
- `books` — id, title, author, isbn, description, genre, year, copies, file_path, ai_summary, review_consensus, avg_rating
- `reviews` — id, user_id, book_id, rating, text, sentiment
- `borrows` — id, user_id, book_id, borrowed_at, returned_at, is_returned
- `user_preferences` — user_id, favorite_genres, favorite_authors

### Recommendation Algorithm (hybrid mode)

Scores each unread book by:
1. **Genre preference** (+0.4) — matches user's saved favorite genres
2. **Author preference** (+0.35) — matches user's saved favorite authors
3. **Rating** (+0.2 max) — normalized avg_rating/5
4. **TF-IDF similarity** (+0.15 max) — cosine similarity between book description and descriptions of books the user has already read
5. **Collaborative genre** (+0.1) — book's genre matches genres in user's borrow history

## Code Quality

```bash
# Backend
cd backend && ruff check . && ruff format .

# Frontend
cd frontend && npm run lint && npm test
```
