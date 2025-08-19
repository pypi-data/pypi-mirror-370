"""Contains the ProcedureCode model for Dentrix API."""

from typing import Self

from t_object import ThoughtfulObject


class ProcedureCode(ThoughtfulObject):
    """ProcedureCode model for easier Data handling."""

    id: int
    abbreviated_description: str | None
    active: bool | None
    ada_code: str | None
    amount: float | None
    bill_to_insurance: bool | None
    category: str | None
    category_description: str | None
    charting_symbol: str | None
    code_extension: str | None
    description: str | None
    favorite_name: str | None
    has_prosthesis: bool | None
    is_aoc_shown: bool | None
    is_clinical_note_required: bool | None
    is_favorite: bool | None
    is_ortho_flag_complete: bool | None
    is_treatment_info_required: bool | None
    is_tx_plan_template: bool | None
    ortho: bool | None
    predetermined: bool | None
    treatment_area: str | None
    treatment_area_flag: str | None
    visible: bool | None
    payload: dict | None

    @classmethod
    def from_payload(cls, payload: dict) -> Self:
        """Generate a ProcedureCode model from a Dentrix payload result."""
        return cls(
            id=payload.get("id"),
            abbreviated_description=payload.get("abbreviatedDescription"),
            active=payload.get("active"),
            ada_code=payload.get("adaCode"),
            amount=payload.get("amount"),
            bill_to_insurance=payload.get("billToInsurance"),
            category=payload.get("category"),
            category_description=payload.get("categoryDescription"),
            charting_symbol=payload.get("chartingSymbol"),
            code_extension=payload.get("codeExtension"),
            description=payload.get("description"),
            favorite_name=payload.get("favoriteName"),
            has_prosthesis=payload.get("hasProsthesis"),
            is_aoc_shown=payload.get("isAocShown"),
            is_clinical_note_required=payload.get("isClinicalNoteRequired"),
            is_favorite=payload.get("isFavorite"),
            is_ortho_flag_complete=payload.get("isOrthoFlagComplete"),
            is_treatment_info_required=payload.get("isTreatmentInfoRequired"),
            is_tx_plan_template=payload.get("isTxPlanTemplate"),
            ortho=payload.get("ortho"),
            predetermined=payload.get("predetermined"),
            treatment_area=payload.get("treatmentArea"),
            treatment_area_flag=payload.get("treatmentAreaFlag"),
            visible=payload.get("visible"),
            payload=payload,
        )
