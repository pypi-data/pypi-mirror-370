"""Data Transfer Object (DTO) for Ledger Balance information within Dentrix."""

from typing import Self

from t_object import ThoughtfulObject


class LedgerBalance(ThoughtfulObject):
    """Model representing a Ledger Balance information."""

    first_month: float | None
    second_month: float | None
    third_month: float | None
    over_three_months: float | None
    insurance_portion: float | None
    write_off_adjustments: float | None
    patient_portion: float | None
    balance: float | None
    unapplied_credits: float | None
    please_pay_amount: float | None
    closeable_payment_plan_state: bool | None
    has_coverage_gap: bool | None
    has_updated_portions: bool | None
    updated_insurance_portion: float | None
    updated_write_off_adjustments: float | None
    updated_patient_portion: float | None
    payload: dict | None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generates LedgerBalance from payload."""
        return cls(
            first_month=payload.get("firstMonth"),
            second_month=payload.get("secondMonth"),
            third_month=payload.get("thirdMonth"),
            over_three_months=payload.get("overThreeMonths"),
            insurance_portion=payload.get("insurancePortion"),
            write_off_adjustments=payload.get("writeOffAdjustments"),
            patient_portion=payload.get("patientPortion"),
            balance=payload.get("balance"),
            unapplied_credits=payload.get("unappliedCredits"),
            please_pay_amount=payload.get("pleasePayAmount"),
            closeable_payment_plan_state=payload.get("closeablePaymentPlanState"),
            has_coverage_gap=payload.get("hasCoverageGap"),
            has_updated_portions=payload.get("hasUpdatedPortions"),
            updated_insurance_portion=payload.get("updatedInsurancePortion"),
            updated_write_off_adjustments=payload.get("updatedWriteOffAdjustments"),
            updated_patient_portion=payload.get("updatedPatientPortion"),
            payload=payload,
        )
