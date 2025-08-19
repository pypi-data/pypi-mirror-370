"""Contains the Document model for Dentrix API."""

from typing import Self

from t_object import ThoughtfulObject


class Document(ThoughtfulObject):
    """Document model for easier Data handling."""

    id: int
    byte_size: int | None
    date: int | None
    name: str | None
    pdf_page_count: int | None
    tags: list | None
    thumb_nail_id: str | None
    type: str | None
    payload: dict | None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generate a Document model from a Dentrix payload result."""
        return cls(
            id=payload.get("id"),
            byte_size=payload.get("byteSize"),
            date=payload.get("date"),
            name=payload.get("name"),
            pdf_page_count=payload.get("pdfPageCount"),
            tags=payload.get("tags"),
            thumb_nail_id=payload.get("thumbNailId"),
            type=payload.get("type"),
            payload=payload,
        )
