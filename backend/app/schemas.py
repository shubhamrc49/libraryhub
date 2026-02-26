from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ---- Auth ----
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Books ----
class BookCreate(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    total_copies: int = 1


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    total_copies: Optional[int] = None


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str]
    description: Optional[str]
    genre: Optional[str]
    year: Optional[int]
    total_copies: int
    available_copies: int
    file_path: Optional[str]
    cover_path: Optional[str]
    ai_summary: Optional[str]
    review_consensus: Optional[str]
    avg_rating: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Reviews ----
class ReviewCreate(BaseModel):
    rating: int  # 1-5
    text: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    rating: int
    text: Optional[str]
    sentiment: Optional[str]
    created_at: datetime
    username: Optional[str] = None

    class Config:
        from_attributes = True


# ---- Borrows ----
class BorrowOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrowed_at: datetime
    returned_at: Optional[datetime]
    is_returned: bool
    book_title: Optional[str] = None

    class Config:
        from_attributes = True


# ---- Preferences ----
class PreferenceUpdate(BaseModel):
    favorite_genres: Optional[str] = None
    favorite_authors: Optional[str] = None


# ---- Recommendations ----
class RecommendationOut(BaseModel):
    book: BookOut
    score: float
    reason: str
