"""Contains Patient Models."""

from datetime import date
from typing import Any, Self

from t_object import ThoughtfulObject

from t_dentrix_service.models.activity_status import Status
from t_dentrix_service.utils.converters import convert_timestamp_to_date


class Patient(ThoughtfulObject):
    """Patient Data model for easier Data handling."""

    id: int
    first_name: str | None
    last_name: str | None
    preferred_name: str | None
    primary_provider_id: int | None
    name: str | None
    date_of_birth: date | None
    date_of_birth_timestamp: int | None
    chart_number: str | None
    phone_number: str | None
    activity_status: Status | str | None
    is_ortho: bool | None
    preferred_location_id: int | None
    payload: dict | None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generate a Patient model from a Dentrix payload result."""
        return cls(
            id=payload.get("id"),
            first_name=payload.get("firstName"),
            last_name=payload.get("lastName"),
            preferred_name=payload.get("preferredName"),
            primary_provider_id=payload.get("primaryProviderId"),
            name=payload.get("name"),
            date_of_birth=convert_timestamp_to_date(payload.get("dateOfBirth")) if payload.get("dateOfBirth") else None,
            date_of_birth_timestamp=payload.get("dateOfBirth"),
            chart_number=payload.get("chartNumber"),
            phone_number=payload.get("phone"),
            activity_status=payload.get("status"),
            is_ortho=payload.get("isOrtho"),
            preferred_location_id=payload.get("preferredLocation")["id"] if payload.get("preferredLocation") else None,
            payload=payload,
        )


class PatientSearchResult(ThoughtfulObject):
    """Patient Search Result model for handling search response data."""

    id: int
    age: int | None
    display_full_name: str | None
    last_name: str | None
    is_orthodontia_patient: bool | None
    patient_insurance_plans: list[dict[str, Any]] | None
    patient_medical_alerts: list[dict[str, Any]] | None
    status: str | None
    payload: dict | None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generate a PatientSearchResult model from a Dentrix payload result."""
        return cls(
            id=payload.get("id"),
            age=payload.get("age"),
            display_full_name=payload.get("displayFullName"),
            last_name=payload.get("lastName"),
            is_orthodontia_patient=payload.get("isOrthodontiaPatient"),
            patient_insurance_plans=payload.get("patientInsurancePlans"),
            patient_medical_alerts=payload.get("patientMedicalAlerts"),
            status=payload.get("status"),
            payload=payload,
        )


class PatientInfo(ThoughtfulObject):
    """Patient Info Data model for easier Data handling."""

    age: int | None
    billing_type: dict[str, int] | None
    chart_number: str | None
    contact_method: str | None
    created: int | None
    date_of_birth: int | None
    discount_plan: dict[str, int] | None
    discount_plan_expiration_date: int | None
    discount_type: str | None
    display_full_name: str | None
    display_name_by_last: str | None
    emails: list[dict[str, Any]] | None
    emergency_contact: str | None
    ethnicity: str | dict | None
    external_id: str | None
    family_size: int | None
    first_name: str | None
    first_visit_date: int | None
    gender: str | None
    guarantored_patients: list[dict[str, Any]] | None
    has_alerts: bool | None
    has_pending_changes: bool | None
    id: int
    income: int | None
    is_orthodontia_patient: bool | None
    is_self_guarantored: bool | None
    language_type: str | None
    last_missed_appointment_date: int | None
    last_name: str | None
    last_visit_date: int | None
    middle_name: str | None
    name_suffix: str | None
    organization: dict[str, int] | None
    patient_address: dict[str, Any] | None
    patient_connection_notes: list[dict[str, Any]] | None
    patient_forms: list[dict[str, Any]] | None
    patient_insurance_plans: list[dict[str, Any]] | None
    patient_medical_alerts: list[dict[str, Any]] | None
    patient_payment_plans: list[dict[str, Any]] | None
    patient_picture: str | int | None
    patient_sms_thread: int | None
    phones: list[dict[str, Any]] | None
    preferred_days: dict[str, bool] | None
    preferred_location: dict[str, int] | None
    preferred_name: str | None
    preferred_times: dict[str, bool] | None
    primary_email: dict[str, Any] | None
    procedures: list[dict[str, Any]] | None
    races: list[dict[str, Any]] | None
    referred_patients: list[dict[str, Any]] | None
    related_patients: list[dict[str, Any]] | None
    relationships: dict[str, dict[str, int]] | None
    status: str | None
    third_party_external_ids: list[dict[str, str]] | None
    title: str | None
    tooth_codes: list[dict[str, Any]] | None
    total_missed_appointments: int | None
    payload: dict | None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generate a PatientInfo model from a Dentrix payload result."""
        return cls(
            age=payload.get("age"),
            billing_type=payload.get("billingType"),
            chart_number=payload.get("chartNumber"),
            contact_method=payload.get("contactMethod"),
            created=payload.get("created"),
            date_of_birth=payload.get("dateOfBirth"),
            discount_plan=payload.get("discountPlan"),
            discount_plan_expiration_date=payload.get("discountPlanExpirationDate"),
            discount_type=payload.get("discountType"),
            display_full_name=payload.get("displayFullName"),
            display_name_by_last=payload.get("displayNameByLast"),
            emails=payload.get("emails"),
            emergency_contact=payload.get("emergencyContact"),
            ethnicity=payload.get("ethnicity"),
            external_id=payload.get("externalID"),
            family_size=payload.get("familySize"),
            first_name=payload.get("firstName"),
            first_visit_date=payload.get("firstVisitDate"),
            gender=payload.get("gender"),
            guarantored_patients=payload.get("guarantoredPatients"),
            has_alerts=payload.get("hasAlerts"),
            has_pending_changes=payload.get("hasPendingChanges"),
            id=payload.get("id"),
            income=payload.get("income"),
            is_orthodontia_patient=payload.get("isOrthodontiaPatient"),
            is_self_guarantored=payload.get("isSelfGuarantored"),
            language_type=payload.get("languageType"),
            last_missed_appointment_date=payload.get("lastMissedAppointmentDate"),
            last_name=payload.get("lastName"),
            last_visit_date=payload.get("lastVisitDate"),
            middle_name=payload.get("middleName"),
            name_suffix=payload.get("nameSuffix"),
            organization=payload.get("organization"),
            patient_address=payload.get("patientAddress"),
            patient_connection_notes=payload.get("patientConnectionNotes"),
            patient_forms=payload.get("patientForms"),
            patient_insurance_plans=payload.get("patientInsurancePlans"),
            patient_medical_alerts=payload.get("patientMedicalAlerts"),
            patient_payment_plans=payload.get("patientPaymentPlans"),
            patient_picture=payload.get("patientPicture"),
            patient_sms_thread=payload.get("patientSmsThread"),
            phones=payload.get("phones"),
            preferred_days=payload.get("preferredDays"),
            preferred_location=payload.get("preferredLocation"),
            preferred_name=payload.get("preferredName"),
            preferred_times=payload.get("preferredTimes"),
            primary_email=payload.get("primaryEmail"),
            procedures=payload.get("procedures"),
            races=payload.get("races"),
            referred_patients=payload.get("referredPatients"),
            related_patients=payload.get("relatedPatients"),
            relationships=payload.get("relationships"),
            status=payload.get("status"),
            third_party_external_ids=payload.get("thirdPartyExternalIds"),
            title=payload.get("title"),
            tooth_codes=payload.get("toothCodes"),
            total_missed_appointments=payload.get("totalMissedAppointments"),
            payload=payload,
        )
