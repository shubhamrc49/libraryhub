import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import os

from app.db import get_db
from app.models.book import Book
from app.models.user import User
from app.schemas import BookOut, BookCreate, BookUpdate
from app.core.security import get_current_user
from app.services import storage, llm
from app.core.config import settings

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookOut])
async def list_books(
    search: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    q = select(Book)
    if search:
        q = q.where(
            Book.title.ilike(f"%{search}%") | Book.author.ilike(f"%{search}%")
        )
    if genre:
        q = q.where(Book.genre.ilike(f"%{genre}%"))
    q = q.offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    return book


@router.post("", response_model=BookOut, status_code=201)
async def create_book(
    title: str = Form(...),
    author: str = Form(...),
    isbn: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    total_copies: int = Form(1),
    file: Optional[UploadFile] = File(None),
    cover: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = None
    cover_path = None

    if file:
        file_path = await storage.save_file(file, "books")
    if cover:
        cover_path = await storage.save_file(cover, "covers")

    book = Book(
        title=title,
        author=author,
        isbn=isbn,
        description=description,
        genre=genre,
        year=year,
        total_copies=total_copies,
        available_copies=total_copies,
        file_path=file_path,
        cover_path=cover_path,
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)

    # Background: generate AI summary
    asyncio.create_task(_generate_summary(book.id, title, author, description or ""))

    return book


@router.put("/{book_id}", response_model=BookOut)
async def update_book(
    book_id: int,
    data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)

    await db.commit()
    await db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(403, "Admins only")
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    await db.delete(book)
    await db.commit()


@router.get("/{book_id}/download")
async def download_book(book_id: int, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    book = await db.get(Book, book_id)
    if not book or not book.file_path:
        raise HTTPException(404, "File not found")
    if settings.STORAGE_BACKEND == "s3":
        url = storage.get_file_url(book.file_path)
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url)
    local_path = os.path.join(settings.LOCAL_STORAGE_PATH, book.file_path)
    if not os.path.exists(local_path):
        raise HTTPException(404, "File not found on disk")
    return FileResponse(local_path, filename=os.path.basename(book.file_path))


async def _generate_summary(book_id: int, title: str, author: str, description: str):
    """Background task to generate AI summary for newly added book."""
    from app.db import AsyncSessionLocal
    try:
        summary = await llm.generate_book_summary(title, author, description)
        async with AsyncSessionLocal() as db:
            book = await db.get(Book, book_id)
            if book:
                book.ai_summary = summary
                await db.commit()
    except Exception:
        pass
