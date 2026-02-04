"""
CRUD操作包
"""
from app.crud.crud_book import create_book, get_book, get_books, delete_book
from app.crud.crud_series import create_persona, create_book_series, get_book_series, update_series_status

__all__ = [
    "create_book",
    "get_book",
    "get_books",
    "delete_book",
    "create_persona",
    "create_book_series",
    "get_book_series",
    "update_series_status"
]
