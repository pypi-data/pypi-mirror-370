"""Data Transfer Object (DTO) for Charge information within Dentrix."""

from typing import Optional, Any
from t_object import ThoughtfulObject  # ou ajuste o import conforme o projeto
from .location import Location


class Charge(ThoughtfulObject):
    """Model representing a single charge."""

    charge_id: Optional[int]
    date: Optional[int]
    patient: Optional[str]
    provider: Optional[str]
    code: Optional[str]
    description: Optional[str]
    charge: Optional[float]
    other_credits: Optional[float]
    applied: Optional[float]
    balance: Optional[float]
    is_attached_to_payment_plan: Optional[str]
    exceptions: Optional[list]
    patient_procedure_id: Optional[int]
    bill_to_insurance: Optional[bool]
    guarantor_portion: Optional[float]
    location: Optional[Location]
    tooth: Optional[str]
    surfaces: Optional[str]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Charge":
        """Generate a Charge object from payload."""
        return cls(
            charge_id=payload.get("chargeId"),
            date=payload.get("date"),
            patient=payload.get("patient"),
            provider=payload.get("provider"),
            code=payload.get("code"),
            description=payload.get("description"),
            charge=payload.get("charge"),
            other_credits=payload.get("otherCredits"),
            applied=payload.get("applied"),
            balance=payload.get("balance"),
            is_attached_to_payment_plan=payload.get("isAttachedToPaymentPlan"),
            exceptions=payload.get("exceptions"),
            patient_procedure_id=payload.get("patientProcedureId"),
            bill_to_insurance=payload.get("billToInsurance"),
            guarantor_portion=payload.get("guarantorPortion"),
            location=Location.from_payload(payload["location"]) if payload.get("location") else None,
            tooth=payload.get("tooth"),
            surfaces=payload.get("surfaces"),
        )
