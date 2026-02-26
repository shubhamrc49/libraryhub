import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db import get_db
from app.models.book import Book
from app.models.review import Review
from app.models.user import User
from app.schemas import ReviewCreate, ReviewOut
from app.core.security import get_current_user
from app.services import llm

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/book/{book_id}", response_model=list[ReviewOut])
async def book_reviews(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(Review.book_id == book_id).order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    out = []
    for r in reviews:
        user = await db.get(User, r.user_id)
        item = ReviewOut.model_validate(r)
        item.username = user.username if user else None
        out.append(item)
    return out


@router.post("/book/{book_id}", response_model=ReviewOut, status_code=201)
async def create_review(
    book_id: int,
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not 1 <= data.rating <= 5:
        raise HTTPException(400, "Rating must be between 1 and 5")

    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")

    # Check duplicate review
    result = await db.execute(
        select(Review).where(Review.user_id == current_user.id, Review.book_id == book_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "You have already reviewed this book")

    review = Review(
        user_id=current_user.id,
        book_id=book_id,
        rating=data.rating,
        text=data.text,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    # Background: analyze sentiment + update avg rating + consensus
    asyncio.create_task(_process_review(review.id, book_id, data.text or ""))

    item = ReviewOut.model_validate(review)
    item.username = current_user.username
    return item


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    if review.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(403, "Not authorized")
    await db.delete(review)
    await db.commit()


async def _process_review(review_id: int, book_id: int, text: str):
    """Background: sentiment analysis, update avg rating, generate consensus."""
    from app.db import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as db:
            # Sentiment
            sentiment = await llm.analyze_review_sentiment(text)
            review = await db.get(Review, review_id)
            if review:
                review.sentiment = sentiment
                await db.commit()

            # Update avg rating
            result = await db.execute(
                select(func.avg(Review.rating)).where(Review.book_id == book_id)
            )
            avg = result.scalar()
            book = await db.get(Book, book_id)
            if book and avg:
                book.avg_rating = round(float(avg), 2)

            # Generate consensus
            reviews_result = await db.execute(
                select(Review).where(Review.book_id == book_id).limit(10)
            )
            reviews = reviews_result.scalars().all()
            review_dicts = [{"rating": r.rating, "text": r.text} for r in reviews]
            consensus = await llm.generate_review_consensus(review_dicts)
            if book:
                book.review_consensus = consensus

            await db.commit()
    except Exception:
        pass
