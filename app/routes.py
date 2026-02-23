"""CRUD routes for the Bookshelf API."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .database import get_db
from .metrics import BOOKS_TOTAL
from .models import Book, BookCreate, BookResponse, BookUpdate

logger = logging.getLogger("bookshelf")

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookResponse])
def list_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db),
):
    """List all books with pagination."""
    books = db.query(Book).offset(skip).limit(limit).all()
    logger.info("Listed %d books (skip=%d, limit=%d)", len(books), skip, limit)
    return books


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a single book by ID."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return book


@router.post("", response_model=BookResponse, status_code=201)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    """Create a new book."""
    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    BOOKS_TOTAL.inc()
    logger.info("Created book id=%d title=%r", book.id, book.title)
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    """Update an existing book."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    logger.info("Updated book id=%d", book.id)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    db.delete(book)
    db.commit()
    logger.info("Deleted book id=%d", book_id)
    return None
