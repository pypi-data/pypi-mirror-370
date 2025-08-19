"""This module contains the XrayExam and XrayImage classes."""
import json

from t_object import ThoughtfulObject


class XrayExam(ThoughtfulObject):
    """Class to represent an X-ray Exam."""

    date: int
    id: int
    name: str
    procedure_code: str
    payload: dict

    @classmethod
    def from_payload(cls: "XrayExam", exam_json: dict) -> "XrayExam":
        """Create an XrayExam object from a dictionary."""
        return XrayExam(
            date=exam_json["ExamDate"],
            id=exam_json["ExamId"],
            name=exam_json["Name"],
            procedure_code=exam_json["ProcedureCode"],
            payload=exam_json,
        )


class XrayImage(ThoughtfulObject):
    """Class to represent an X-ray Image."""

    format: str
    id: int
    tooth_numbers: list[int | str]
    treatments: str
    url: str
    payload: dict

    @classmethod
    def from_payload(cls: "XrayImage", image_json: dict) -> "XrayImage":
        """Create an XrayImage object from a dictionary."""
        treatments_json = {
            "Rotation": image_json["Rotation"],
            "IsFlipped": image_json["IsFlipped"],
            "IsMirrored": image_json["IsMirrored"],
            "AdditionalRotation": image_json["AdditionalRotation"],
            "IsInverted": image_json["IsInverted"],
            "Gamma": image_json["Gamma"],
            "Contrast": image_json["Contrast"],
        }
        treatments_str = json.dumps(treatments_json)
        treatments = treatments_str.replace(" ", "")
        return XrayImage(
            format=image_json["ImageFormat"],
            id=image_json["ImageId"],
            tooth_numbers=list(image_json["ToothNumbers"]),
            treatments=treatments,
            url=image_json["ImageSrc"],
            payload=image_json,
        )
