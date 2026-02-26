from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.book import Book
from app.models.review import Borrow
from app.models.user import User
from app.schemas import BorrowOut
from app.core.security import get_current_user

router = APIRouter(prefix="/borrows", tags=["borrows"])


@router.post("/{book_id}", response_model=BorrowOut, status_code=201)
async def borrow_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    if book.available_copies <= 0:
        raise HTTPException(400, "No copies available")

    # Check if user already has this borrowed
    result = await db.execute(
        select(Borrow).where(
            Borrow.user_id == current_user.id,
            Borrow.book_id == book_id,
            Borrow.is_returned == False,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "You already have this book borrowed")

    book.available_copies -= 1
    borrow = Borrow(user_id=current_user.id, book_id=book_id)
    db.add(borrow)
    await db.commit()
    await db.refresh(borrow)

    out = BorrowOut.model_validate(borrow)
    out.book_title = book.title
    return out


@router.post("/{borrow_id}/return", response_model=BorrowOut)
async def return_book(
    borrow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = await db.get(Borrow, borrow_id)
    if not borrow:
        raise HTTPException(404, "Borrow record not found")
    if borrow.user_id != current_user.id:
        raise HTTPException(403, "Not your borrow")
    if borrow.is_returned:
        raise HTTPException(400, "Already returned")

    borrow.is_returned = True
    borrow.returned_at = datetime.utcnow()

    book = await db.get(Book, borrow.book_id)
    if book:
        book.available_copies += 1

    await db.commit()
    await db.refresh(borrow)

    out = BorrowOut.model_validate(borrow)
    if book:
        out.book_title = book.title
    return out


@router.get("/me", response_model=list[BorrowOut])
async def my_borrows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Borrow).where(Borrow.user_id == current_user.id).order_by(Borrow.borrowed_at.desc())
    )
    borrows = result.scalars().all()
    out_list = []
    for b in borrows:
        book = await db.get(Book, b.book_id)
        item = BorrowOut.model_validate(b)
        item.book_title = book.title if book else None
        out_list.append(item)
    return out_list
