"""
CRUD操作包
"""
from app.crud.crud_book import create_book, get_book, get_books, delete_book
from app.crud.crud_series import create_persona, create_book_series, get_book_series, update_series_status
from app.crud.crud_audience import (
    create_audience_persona,
    get_audience_persona,
    get_audience_personas,
    update_audience_persona,
    delete_audience_persona
)
from app.crud.crud_output import (
    create_output_artifact,
    get_output_artifact,
    get_output_artifacts,
    delete_output_artifact,
    create_diagnostic_report,
    get_diagnostic_report,
    get_reports_by_artifact
)

__all__ = [
    "create_book",
    "get_book",
    "get_books",
    "delete_book",
    "create_persona",
    "create_book_series",
    "get_book_series",
    "update_series_status",
    "create_audience_persona",
    "get_audience_persona",
    "get_audience_personas",
    "update_audience_persona",
    "delete_audience_persona",
    "create_output_artifact",
    "get_output_artifact",
    "get_output_artifacts",
    "delete_output_artifact",
    "create_diagnostic_report",
    "get_diagnostic_report",
    "get_reports_by_artifact"
]
