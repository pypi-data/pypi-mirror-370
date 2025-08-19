"""Contains Appointment, Event, MissedAppointment and Schedule models."""

from typing import Optional, List, Union, Any
from t_object import ThoughtfulObject


class Appointment(ThoughtfulObject):
    """Model representing an Appointment item."""

    id: int
    version: Optional[int]
    created: Optional[int]
    startDateTime: int
    endDateTime: Optional[int]
    provider: dict
    operatory: dict
    needsFollowup: Optional[bool]
    ASAP: Optional[bool]
    needsPremedicate: Optional[bool]
    note: Optional[str]
    other: Optional[str]
    status: str
    title: Optional[str]
    reason: Optional[str]
    duration: int
    patient: dict
    patientLite: dict
    patientId: int
    location: dict
    followedUp: Optional[int]
    reminded: Optional[int]
    confirmed: Optional[int]
    insuranceEligibilityVerified: Optional[bool]
    productionAmount: Optional[float]
    secondaryProvider: Optional[dict]
    leftMessage: Optional[int]
    visits: List
    patientProcedures: List[dict]
    procedures: List
    communications: List[dict]
    dueDates: List
    bookedOnline: Optional[bool]
    missedAppointments: List
    pinned: Optional[bool]
    pinnedOn: Optional[int]
    timePattern: Any = None
    labCase: dict | None = None
    data: dict | None = None

    @classmethod
    def from_payload(cls, payload: dict) -> "Appointment":
        """Generate an Appointment model from a Dentrix payload result."""
        return cls(**payload, data=payload)


class Event(ThoughtfulObject):
    """Model representing an Event item."""

    id: int
    startDateTime: int
    endDateTime: int
    organization: dict
    location: dict
    operatory: dict
    recurrence: Optional[dict]
    title: str
    description: Optional[str]
    allDay: bool
    duration: int
    recurring: bool
    groupId: Any
    color: str
    lastModified: int
    provider: dict | None = None

    @classmethod
    def from_payload(cls, payload: dict) -> "Event":
        """Generate an Event model from a Dentrix payload result."""
        return cls(**payload)


class MissedAppointment(ThoughtfulObject):
    """Model representing a MissedAppointment item."""

    id: int
    appointment: dict | None = None
    startDateTime: int
    duration: int
    status: str
    operatory: dict
    provider: dict
    patient: dict
    location: dict
    other: Optional[str]
    procedures: Union[str, List[str]]
    cancelledOn: Optional[int]
    reasonCancelled: Optional[str]
    rescheduledOn: Optional[int]
    note: Optional[str]
    patientLite: dict
    patientId: int

    @classmethod
    def from_payload(cls, payload: dict) -> "MissedAppointment":
        """Generate a MissedAppointment model from a Dentrix payload result."""
        return cls(**payload)


class Schedule(ThoughtfulObject):
    """Model representing a Schedule item."""

    appointments: List[Appointment]
    events: List[Event]
    draftAppointments: List
    missedAppointments: List[MissedAppointment]
    daynotes: List

    @classmethod
    def from_payload(cls, payload: dict) -> "Schedule":
        """Generate a Schedule model from a Dentrix payload result."""
        return cls(
            appointments=[Appointment.from_payload(a) for a in payload.get("appointments", [])],
            events=[Event.from_payload(e) for e in payload.get("events", [])],
            draftAppointments=payload.get("draftAppointments", []),
            missedAppointments=[MissedAppointment.from_payload(m) for m in payload.get("missedAppointments", [])],
            daynotes=payload.get("daynotes", []),
        )
