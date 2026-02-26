"""
Recommendation engine.
hybrid: TF-IDF content similarity + collaborative filtering + user preferences
llm: Uses LLM to rank and explain recommendations
"""
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.book import Book
from app.models.review import Borrow, UserPreference
from app.core.config import settings


async def get_recommendations(user_id: int, db: AsyncSession, limit: int = 10) -> List[Tuple[Book, float, str]]:
    if settings.RECOMMENDATION_ENGINE == "llm":
        return await _llm_recommendations(user_id, db, limit)
    return await _hybrid_recommendations(user_id, db, limit)


async def _hybrid_recommendations(user_id: int, db: AsyncSession, limit: int) -> List[Tuple[Book, float, str]]:
    # Get user's borrowed books
    borrow_result = await db.execute(
        select(Borrow).where(Borrow.user_id == user_id)
    )
    borrows = borrow_result.scalars().all()
    borrowed_ids = {b.book_id for b in borrows}

    # Get all books the user hasn't borrowed
    books_result = await db.execute(select(Book))
    all_books = books_result.scalars().all()
    candidate_books = [b for b in all_books if b.id not in borrowed_ids]

    if not candidate_books:
        return []

    # Get user preferences
    pref_result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    prefs = pref_result.scalar_one_or_none()
    fav_genres = set((prefs.favorite_genres or "").lower().split(",")) if prefs else set()
    fav_authors = set((prefs.favorite_authors or "").lower().split(",")) if prefs else set()

    # Get books user borrowed (for collaborative content similarity)
    borrowed_books = [b for b in all_books if b.id in borrowed_ids]

    scored = []
    for book in candidate_books:
        score = 0.0
        reason_parts = []

        # Genre preference score
        if book.genre and book.genre.lower() in fav_genres:
            score += 0.4
            reason_parts.append(f"matches your favorite genre ({book.genre})")

        # Author preference score
        if book.author and book.author.lower() in fav_authors:
            score += 0.35
            reason_parts.append(f"by a favorite author ({book.author})")

        # Rating score (normalize 1-5 to 0-0.2)
        if book.avg_rating:
            score += (book.avg_rating / 5.0) * 0.2
            reason_parts.append(f"highly rated ({book.avg_rating:.1f}/5)")

        # TF-IDF similarity to borrowed books
        if borrowed_books and book.description:
            sim = _tfidf_similarity(book, borrowed_books)
            score += sim * 0.15
            if sim > 0.1:
                reason_parts.append("similar to books you've read")

        # Collaborative: same genre as previously borrowed
        borrowed_genres = {b.genre for b in borrowed_books if b.genre}
        if book.genre and book.genre in borrowed_genres:
            score += 0.1
            if "similar genre" not in " ".join(reason_parts):
                reason_parts.append("similar genre to your reading history")

        reason = "; ".join(reason_parts) if reason_parts else "popular in the catalog"
        scored.append((book, round(score, 3), reason))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def _tfidf_similarity(target: Book, candidates: List[Book]) -> float:
    """Simple TF-IDF cosine similarity between target book and list of books."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        texts = [target.description or ""] + [b.description or "" for b in candidates]
        if all(t == "" for t in texts):
            return 0.0

        vectorizer = TfidfVectorizer(max_features=200, stop_words="english")
        tfidf = vectorizer.fit_transform(texts)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:])
        return float(np.max(sims)) if sims.size > 0 else 0.0
    except Exception:
        return 0.0


async def _llm_recommendations(user_id: int, db: AsyncSession, limit: int) -> List[Tuple[Book, float, str]]:
    from app.services.llm import llm_complete

    borrow_result = await db.execute(select(Borrow).where(Borrow.user_id == user_id))
    borrows = borrow_result.scalars().all()
    borrowed_ids = {b.book_id for b in borrows}

    books_result = await db.execute(select(Book))
    all_books = books_result.scalars().all()
    borrowed_books = [b for b in all_books if b.id in borrowed_ids]
    candidates = [b for b in all_books if b.id not in borrowed_ids][:20]  # limit context

    if not candidates:
        return []

    borrowed_titles = [f"{b.title} by {b.author}" for b in borrowed_books[:5]]
    candidate_list = "\n".join([f"{i}. {b.title} by {b.author} (genre: {b.genre})" for i, b in enumerate(candidates)])

    prompt = f"""A user has previously read: {', '.join(borrowed_titles) or 'nothing yet'}
    
Available books to recommend:
{candidate_list}

Pick the top {min(limit, len(candidates))} books for this user and respond ONLY with a comma-separated list of the numbers (e.g., 0,2,5).

Numbers:"""

    result = await llm_complete(prompt)
    try:
        indices = [int(x.strip()) for x in result.split(",") if x.strip().isdigit()]
        recommendations = []
        for idx in indices[:limit]:
            if 0 <= idx < len(candidates):
                recommendations.append((candidates[idx], 0.8, "Recommended by AI based on your reading history"))
        return recommendations
    except Exception:
        return [(b, 0.5, "AI recommendation") for b in candidates[:limit]]
