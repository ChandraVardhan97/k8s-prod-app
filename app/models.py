"""SQLAlchemy models and Pydantic schemas for the Bookshelf API."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


# ---------------------------------------------------------------------------
# SQLAlchemy ORM Model
# ---------------------------------------------------------------------------


class Book(Base):
    """A book in the bookshelf."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    genre: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Pydantic Schemas (request / response validation)
# ---------------------------------------------------------------------------


class BookCreate(BaseModel):
    """Schema for creating a new book."""

    title: str = Field(..., min_length=1, max_length=255, examples=["The Pragmatic Programmer"])
    author: str = Field(..., min_length=1, max_length=255, examples=["David Thomas, Andrew Hunt"])
    year: int = Field(..., ge=1000, le=2100, examples=[1999])
    genre: str = Field(..., min_length=1, max_length=100, examples=["Technology"])


class BookUpdate(BaseModel):
    """Schema for updating an existing book (all fields optional)."""

    title: str | None = Field(None, min_length=1, max_length=255)
    author: str | None = Field(None, min_length=1, max_length=255)
    year: int | None = Field(None, ge=1000, le=2100)
    genre: str | None = Field(None, min_length=1, max_length=100)


class BookResponse(BaseModel):
    """Schema for book responses."""

    id: int
    title: str
    author: str
    year: int
    genre: str
    created_at: datetime

    model_config = {"from_attributes": True}
