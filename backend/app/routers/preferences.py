from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.review import UserPreference
from app.models.user import User
from app.schemas import PreferenceUpdate
from app.core.security import get_current_user

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("")
async def get_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        return {"favorite_genres": "", "favorite_authors": ""}
    return {"favorite_genres": pref.favorite_genres or "", "favorite_authors": pref.favorite_authors or ""}


@router.put("")
async def update_preferences(
    data: PreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)
    if data.favorite_genres is not None:
        pref.favorite_genres = data.favorite_genres
    if data.favorite_authors is not None:
        pref.favorite_authors = data.favorite_authors
    await db.commit()
    return {"favorite_genres": pref.favorite_genres, "favorite_authors": pref.favorite_authors}
