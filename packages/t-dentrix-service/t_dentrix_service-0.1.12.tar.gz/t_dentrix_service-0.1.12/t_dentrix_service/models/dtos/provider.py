"""Contains Provider model."""


from typing import Self

from t_object import ThoughtfulObject


class Provider(ThoughtfulObject):
    """Provider Data model for easier Data handling."""

    id: int
    active: bool
    blue_cross_number: str | None
    clinician_registration_status_type: dict | None
    color: str | None
    date_of_birth: int | None
    dea_expiration: int | None
    dea_schedule2: bool | None
    dea_schedule3: bool | None
    dea_schedule4: bool | None
    dea_schedule5: bool | None
    e_prescribe_enabled: bool | None
    e_trans_provider_location_registration_status: list | None
    erx_id: str | None
    first_name: str | None
    has_signature: bool | None
    is_icp8214_enabled: bool | None
    is_locum_tenens: bool | None
    is_non_person_entity: bool | None
    is_onboarded_with_dose_spot: bool | None
    is_onboarded_with_veradigm: bool | None
    is_primary_provider: bool | None
    is_scheduling_eligible: bool | None
    last_name: str | None
    medicaid_number: str | None
    middle_name: str | None
    npi: str | None
    organization: dict | None
    prov_id: str | None
    provider_number: str | None
    short_name: str | None
    state_id: str | None
    state_id_expiration: int | None
    tin: str | None
    user: dict | None
    payload: dict | None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generate a Provider model from a Dentrix payload result."""
        return cls(
            id=payload.get("id"),
            active=payload.get("active"),
            blue_cross_number=payload.get("blueCrossNumber"),
            clinician_registration_status_type=payload.get("clinicianRegistrationStatusType"),
            color=payload.get("color"),
            date_of_birth=payload.get("dateOfBirth"),
            dea_expiration=payload.get("deaExpiration"),
            dea_schedule2=payload.get("deaSchedule2"),
            dea_schedule3=payload.get("deaSchedule3"),
            dea_schedule4=payload.get("deaSchedule4"),
            dea_schedule5=payload.get("deaSchedule5"),
            e_prescribe_enabled=payload.get("ePrescribeEnabled"),
            e_trans_provider_location_registration_status=payload.get("eTransProviderLocationRegistrationStatus"),
            erx_id=payload.get("erxId"),
            first_name=payload.get("firstName"),
            has_signature=payload.get("hasSignature"),
            is_icp8214_enabled=payload.get("isIcp8214Enabled"),
            is_locum_tenens=payload.get("isLocumTenens"),
            is_non_person_entity=payload.get("isNonPersonEntity"),
            is_onboarded_with_dose_spot=payload.get("isOnboardedWithDoseSpot"),
            is_onboarded_with_veradigm=payload.get("isOnboardedWithVeradigm"),
            is_primary_provider=payload.get("isPrimaryProvider"),
            is_scheduling_eligible=payload.get("isSchedulingEligible"),
            last_name=payload.get("lastName"),
            medicaid_number=payload.get("medicaidNumber"),
            middle_name=payload.get("middleName"),
            npi=payload.get("npi"),
            organization=payload.get("organization"),
            prov_id=payload.get("provId"),
            provider_number=payload.get("providerNumber"),
            short_name=payload.get("shortName"),
            state_id=payload.get("stateID"),
            state_id_expiration=payload.get("stateIDExpiration"),
            tin=payload.get("tin"),
            user=payload.get("user"),
            payload=payload,
        )
