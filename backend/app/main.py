from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.db import init_db
from app.core.config import settings
from app.routers import auth, books, borrows, reviews, recommendations, preferences


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    yield


app = FastAPI(title="LibraryHub API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for local storage
if settings.STORAGE_BACKEND == "local":
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    app.mount("/files", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="files")

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(borrows.router)
app.include_router(reviews.router)
app.include_router(recommendations.router)
app.include_router(preferences.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/ollama")
async def health_ollama():
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            return {"status": "ok", "models": resp.json()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
