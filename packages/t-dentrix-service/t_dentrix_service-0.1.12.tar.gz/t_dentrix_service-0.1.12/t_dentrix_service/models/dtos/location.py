"""Contains Location model."""

from typing import Self

from t_object import ThoughtfulObject


class Location(ThoughtfulObject):
    """Location Data model for easier Data handling."""

    id: int
    name: str | None
    location_number: str | None
    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    phone_number: str | None
    tax_percentage: float | None
    timezone: str | None
    payload: dict | None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generate a Location model from a Dentrix payload result."""
        address: dict = payload.get("address", {})

        return cls(
            id=payload.get("id"),
            name=payload.get("name"),
            location_number=payload.get("locationNumber"),
            address1=address.get("address1"),
            address2=address.get("address2"),
            city=address.get("city"),
            state=address.get("state"),
            postal_code=address.get("postalCode"),
            phone_number=payload.get("phone").get("number") if payload.get("phone") else None,
            tax_percentage=payload.get("taxPercentage"),
            timezone=payload.get("timezone"),
            payload=payload,
        )
