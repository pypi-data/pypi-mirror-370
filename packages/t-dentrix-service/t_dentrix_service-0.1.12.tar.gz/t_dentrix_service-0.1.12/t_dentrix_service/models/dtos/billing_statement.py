"""Data Transfer Object (DTO) for Billing Statement information within Dentrix."""

from datetime import date
from typing import Self

from t_object.base_object import BaseModel

from t_dentrix_service.utils.converters import convert_timestamp_to_date


class StatementHeader(BaseModel):
    """Model representing a Statement Header information."""

    id: int
    balance: float
    corrupted: bool | None
    name: str
    should_print: bool | None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generates StatementHeader from payload."""
        return cls(
            id=payload.get("id"),
            balance=payload.get("balance"),
            name=payload.get("name"),
            should_print=payload.get("shouldPrint"),
            corrupted=payload.get("corrupted"),
        )


class BillingStatement(BaseModel):
    """Model representing a Billing Statement information."""

    id: int
    generated_date: date | None = None
    printed_date: date | None = None
    location_id: int | None = None
    timezone: str | None = None
    show_creditcard_info: bool | None = None
    show_abreviation: bool | None = None
    minimum_balance: float | None = None
    pending_charges: bool | None = None
    due_date: date | None = None
    message: str | None = None
    statement_headers: list[StatementHeader] = []

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generates BillingStatement from payload."""
        return cls(
            id=payload["id"],
            generated_date=(
                convert_timestamp_to_date(payload.get("generatedDate")) if payload.get("generatedDate") else None
            ),
            printed_date=(
                convert_timestamp_to_date(payload.get("printedDate")) if payload.get("printedDate") else None
            ),
            location_id=payload.get("location"),
            timezone=payload.get("timeZone").get("displayName") if isinstance(payload.get("timeZone"), dict) else None,
            message=payload.get("message"),
            show_creditcard_info=payload.get("showCreditCardInfo"),
            show_abreviation=payload.get("showAbbreviation"),
            minimum_balance=payload.get("minimumBalance"),
            pending_charges=payload.get("pendingCharges"),
            due_date=convert_timestamp_to_date(payload.get("dueDate")) if payload.get("dueDate") else None,
            statement_headers=[
                StatementHeader.from_payload(header_info) for header_info in payload.get("statementHeaders", [])
            ],
        )
