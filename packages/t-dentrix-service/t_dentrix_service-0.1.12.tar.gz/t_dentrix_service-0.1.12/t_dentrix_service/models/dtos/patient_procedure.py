"""Contains PatientProcedure, UnattachedProcedureMetadata and UnattachedProcedure models."""

from typing import Optional
from t_object import ThoughtfulObject
from typing import List


class PatientProcedure(ThoughtfulObject):
    """Model representing an item within a Patient procedure."""

    procedureCode: str
    amount: float
    description: Optional[str]

    @classmethod
    def from_payload(cls, payload: dict) -> "PatientProcedure":
        """Generate a PatientProcedure model from a Dentrix payload result."""
        return cls(
            procedureCode=payload["procedureCode"],
            amount=payload["amount"],
            description=payload.get("description"),
        )


class UnattachedProcedureMetadata(ThoughtfulObject):
    """Model representing an item within a unattached procedure metadata."""

    id: int
    entityId: int
    entityType: str
    patientName: str
    serviceDate: int
    patientProcedures: List[PatientProcedure]

    @classmethod
    def from_payload(cls, payload: dict) -> "UnattachedProcedureMetadata":
        """Generate a UnattachedProcedureMetadata model from a Dentrix payload result."""
        return cls(
            id=payload["id"],
            entityId=payload["entityId"],
            entityType=payload["entityType"],
            patientName=payload["patientName"],
            serviceDate=payload["serviceDate"],
            patientProcedures=[PatientProcedure.from_payload(proc) for proc in payload.get("patientProcedures", [])],
        )


class UnattachedProcedure(ThoughtfulObject):
    """Model representing an item within a unattached procedure."""

    description: str
    type: str
    metadata: UnattachedProcedureMetadata

    @classmethod
    def from_payload(cls, payload: dict) -> "UnattachedProcedure":
        """Generate a UnattachedProcedure model from a Dentrix payload result."""
        return cls(
            description=payload.get("description", ""),
            type=payload.get("type", ""),
            metadata=UnattachedProcedureMetadata.from_payload(payload["metadata"]),
        )
