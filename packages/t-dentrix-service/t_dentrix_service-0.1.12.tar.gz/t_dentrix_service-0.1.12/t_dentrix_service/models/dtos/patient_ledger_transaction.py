"""Contains PatientLedgerTransaction model."""

from datetime import date
from typing import Optional, Self

from t_object import ThoughtfulObject
from t_dentrix_service.utils.converters import convert_timestamp_to_date
from .location import Location


class PatientLedgerTransaction(ThoughtfulObject):
    """Model representing an item within a billing statement."""

    id: Optional[int] = None
    transaction_date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    group_id: Optional[int] = None
    editable: Optional[bool] = None
    note: Optional[str] = None
    location: Optional[Location] = None
    patient: Optional[str] = None
    created_date: Optional[date] = None
    corrections: Optional[list] = []
    deleted: Optional[bool] = None
    user: Optional[dict] = None
    is_cancellation: Optional[bool] = None
    code: Optional[str] = None
    is_automatically_posted: Optional[bool] = None
    balance: Optional[float] = None
    is_attached_to_payment_plan: Optional[str] = None
    xfers: Optional[list] = []
    provider_id: Optional[int] = None
    provider: Optional[str] = None
    procedure_id: Optional[int] = None
    is_attached_to_claim: Optional[bool] = None
    voided: Optional[bool] = None
    parent_code: Optional[str] = None
    has_patient_conditions: Optional[bool] = None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generate a PatientLedgerTransaction model from a Dentrix payload result."""
        return cls(
            id=payload.get("id"),
            transaction_date=convert_timestamp_to_date(payload.get("date")),
            description=payload.get("description"),
            amount=payload.get("amount", 0),
            type=payload.get("type"),
            group_id=payload.get("groupId"),
            editable=payload.get("editable"),
            note=payload.get("note"),
            location=Location.from_payload(payload["location"]) if payload.get("location") else None,
            patient=payload.get("patient"),
            created_date=convert_timestamp_to_date(payload.get("createdDate")) if payload.get("createdDate") else None,
            corrections=payload.get("corrections", []),
            deleted=payload.get("deleted"),
            user=payload.get("user"),
            is_cancellation=payload.get("isCancellation"),
            code=payload.get("code"),
            is_automatically_posted=payload.get("isAutomaticallyPosted"),
            balance=payload.get("balance"),
            is_attached_to_payment_plan=payload.get("isAttachedToPaymentPlan"),
            xfers=payload.get("xfers", []),
            provider_id=payload.get("providerId"),
            provider=payload.get("provider"),
            procedure_id=payload.get("procedureId"),
            is_attached_to_claim=payload.get("isAttachedToClaim"),
            voided=payload.get("voided"),
            parent_code=payload.get("parentCode"),
            has_patient_conditions=payload.get("hasPatientConditions"),
        )
