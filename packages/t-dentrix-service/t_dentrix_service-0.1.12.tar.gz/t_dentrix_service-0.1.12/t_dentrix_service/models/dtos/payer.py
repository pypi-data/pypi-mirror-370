"""Model representing information about a payer."""

from typing import Self

from t_object import ThoughtfulObject


class Payer(ThoughtfulObject):
    """Model representing information about a payer."""

    carrier_id: str
    carrier_name: str
    payer_id: str

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generate a Payer model from a Dentrix payload result."""
        return cls(
            carrier_id=str(payload["carrier_id"]),
            carrier_name=payload.get("name"),
            payer_id=str(payload.get("payorId")),
        )
