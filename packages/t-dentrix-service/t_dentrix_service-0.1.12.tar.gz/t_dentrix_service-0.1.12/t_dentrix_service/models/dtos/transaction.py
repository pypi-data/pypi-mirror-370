"""Contains Transaction model."""

from typing import Optional, Any
from t_object import ThoughtfulObject

from .location import Location


class Transaction(ThoughtfulObject):
    """Model representing an item within a Transaction."""

    id: Optional[int]
    location: Optional[Location]
    date: Optional[int]
    amount: Optional[float]
    note: Optional[str]
    creation_date: Optional[int]
    ownership: Optional[str]
    expired: Optional[bool]
    is_automatically_posted: Optional[bool]
    is_became_deleted: Optional[bool]
    editable: Optional[bool]
    unlocked: Optional[bool]
    ledger_id: Optional[int]
    description: Optional[str]
    payment_type: Optional[int]
    patient_id: Optional[int]
    patient_name: Optional[str]
    is_voided: Optional[bool]
    paid_at_visit: Optional[bool]
    tags: Optional[list[dict]]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Transaction":
        """Generate a Transaction model from a Dentrix payload result."""
        return cls(
            id=payload.get("id"),
            location=Location.from_payload(payload["location"]) if payload.get("location") else None,
            date=payload.get("date"),
            amount=payload.get("amount"),
            note=payload.get("note"),
            creation_date=payload.get("creationDate"),
            ownership=payload.get("ownership", {}).get("name"),
            expired=payload.get("expired"),
            is_automatically_posted=payload.get("isAutomaticallyPosted"),
            is_became_deleted=payload.get("isBecameDeleted"),
            editable=payload.get("editable"),
            unlocked=payload.get("unlocked"),
            ledger_id=payload.get("ledgerId"),
            description=payload.get("description"),
            payment_type=payload.get("paymentType"),
            patient_id=payload.get("patientId"),
            patient_name=payload.get("patientName"),
            is_voided=payload.get("isVoided"),
            paid_at_visit=payload.get("paidAtVisit"),
            tags=payload.get("tags"),
        )
