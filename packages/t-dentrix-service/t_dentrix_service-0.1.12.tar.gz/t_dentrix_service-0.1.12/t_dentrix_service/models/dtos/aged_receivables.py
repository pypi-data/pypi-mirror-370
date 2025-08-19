"""Data Transfer Object (DTO) for Aged Balance information within Dentrix."""

from typing import Optional, Any
from t_object import ThoughtfulObject


class Balance(ThoughtfulObject):
    """Model representing a Balance information."""

    amount: Optional[float]
    insurance_portion: Optional[float]
    guarantor_portion: Optional[float]
    write_off: Optional[float]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Balance":
        """Generates Balance from payload (API-style keys)."""
        mapped_payload = {
            "amount": payload.get("amount"),
            "insurance_portion": payload.get("insurancePortion"),
            "guarantor_portion": payload.get("guarantorPortion"),
            "write_off": payload.get("writeOff"),
        }
        return cls(**mapped_payload)


class LastPayment(ThoughtfulObject):
    """Model representing a LastPayment information."""

    dated_as: Optional[int]
    amount: Optional[float]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "LastPayment":
        """Generates LastPayment from payload (API-style keys)."""
        mapped_payload = {"dated_as": payload.get("datedAs"), "amount": payload.get("amount")}
        return cls(**mapped_payload)


class AgedReceivable(ThoughtfulObject):
    """Model representing a AgedReceivable information."""

    id: Optional[int]
    guarantor: Optional[str]
    phone_number: Optional[str]
    billing_statement: Optional[int]
    last_payment: Optional[LastPayment]
    claims_pending: Optional[Any]
    before_30: Optional[Balance]
    before_60: Optional[Balance]
    before_90: Optional[Balance]
    over_90: Optional[Balance]
    charge_balance: Optional[float]
    suspended_credits: Optional[float]
    balance: Optional[Balance]
    has_invalid_histories: Optional[bool]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "AgedReceivable":
        """Generates AgedReceivable from payload."""
        return cls(
            id=payload.get("id"),
            guarantor=payload.get("guarantor"),
            phone_number=payload.get("phoneNumber"),
            billing_statement=payload.get("billingStatement"),
            last_payment=LastPayment.from_payload(payload["lastPayment"]) if payload.get("lastPayment") else None,
            claims_pending=payload.get("claimsPending"),
            before_30=Balance.from_payload(payload["before30"]) if payload.get("before30") else None,
            before_60=Balance.from_payload(payload["before60"]) if payload.get("before60") else None,
            before_90=Balance.from_payload(payload["before90"]) if payload.get("before90") else None,
            over_90=Balance.from_payload(payload["over90"]) if payload.get("over90") else None,
            charge_balance=payload.get("chargeBalance"),
            suspended_credits=payload.get("suspendedCredits"),
            balance=Balance.from_payload(payload["balance"]) if payload.get("balance") else None,
            has_invalid_histories=payload.get("hasInvalidHistories"),
        )
