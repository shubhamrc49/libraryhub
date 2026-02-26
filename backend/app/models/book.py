from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, DateTime, Integer, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    author: Mapped[str] = mapped_column(String(300))
    isbn: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_copies: Mapped[int] = mapped_column(Integer, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, default=1)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_consensus: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avg_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    reviews: Mapped[List["Review"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    borrows: Mapped[List["Borrow"]] = relationship(back_populates="book", cascade="all, delete-orphan")
