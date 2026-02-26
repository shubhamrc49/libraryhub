from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.schemas import RecommendationOut, BookOut
from app.core.security import get_current_user
from app.services.recommendations import get_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationOut])
async def recommendations(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = await get_recommendations(current_user.id, db, limit=limit)
    return [
        RecommendationOut(
            book=BookOut.model_validate(book),
            score=score,
            reason=reason,
        )
        for book, score, reason in results
    ]
