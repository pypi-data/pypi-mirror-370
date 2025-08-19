"""Tests for the AscendService class."""

from copy import copy
from unittest.mock import patch

from requests import Response

from t_dentrix_service import AscendService
from tests.ascend_mock_data import AscendMockData


class TestAscendService:
    """Smoke tests of the package."""

    def test_initialization(self):
        """Initialization test."""
        assert AscendService()

    @staticmethod
    def _generate_mock_response(status_code: int) -> Response:
        response = Response()
        response.status_code = status_code
        return response

    @staticmethod
    def _generate_ascend_service_instance() -> AscendService:
        """Returns a new copy of the DentrixService object everytime it's called."""
        return copy(AscendService())

    @patch("t_dentrix_service.ascend_service.AscendRequests.get_patient_insurance_plans")
    def test_get_plan_benefit(self, mock_get_patient_insurance_plans):
        """Returns the plan benefit table for a patient."""
        mock_get_patient_insurance_plans.return_value = AscendMockData.PATIENT_INSURANCE_PLANS
        service = self._generate_ascend_service_instance()
        result = service.get_plan_benefit("123")
        assert result == {"subscriberInsurancePlan": {"carrierInsurancePlan": {"inNetworkCoverage": {"id": "123"}}}}

    @patch("t_dentrix_service.ascend_service.AscendRequests.get_patient_insurance_plans")
    def test_get_plan_benefit_not_found(self, mock_get_patient_insurance_plans):
        """Returns an empty dict if plan benefit is not found."""
        mock_get_patient_insurance_plans.return_value = []
        service = self._generate_ascend_service_instance()
        result = service.get_plan_benefit("123")
        assert result == {}

    @patch("t_dentrix_service.ascend_service.AscendRequests.get_patient_insurance_plan_by_id")
    def test_fetch_patient_insurance_plan_by_id(self, mock_get_patient_insurance_plan_by_id):
        """Returns a patient insurance plan by entry ID."""
        mock_get_patient_insurance_plan_by_id.return_value = {"id": 1, "plan": "Plan A"}
        service = self._generate_ascend_service_instance()
        result = service.fetch_patient_insurance_plan_by_id(1)
        assert result == {"id": 1, "plan": "Plan A"}

    @patch("t_dentrix_service.ascend_service.AscendRequests.get_patient_insurance_plan_by_id")
    def test_fetch_patient_insurance_plan_by_id_not_found(self, mock_get_patient_insurance_plan_by_id):
        """Returns an empty dict if patient insurance plan is not found."""
        mock_get_patient_insurance_plan_by_id.return_value = {}
        service = self._generate_ascend_service_instance()
        result = service.fetch_patient_insurance_plan_by_id(1)
        assert result == {}

    @patch("t_dentrix_service.ascend_service.AscendRequests.get_aging_balance")
    def test_get_aging_balance_for_patient_ownership(self, mock_get_aging_balance):
        """Test aging balance retrieval for patient ownership."""
        expected_response = {"balance": 100}
        mock_get_aging_balance.return_value = expected_response

        service = TestAscendService._generate_ascend_service_instance()
        patient_id = "patient123"

        result = service.get_aging_balance_for_patient_ownership(patient_id)

        assert result == expected_response
        mock_get_aging_balance.assert_called_once_with(
            {"patientId": patient_id, "ownership": "PATIENT", "responseFields": "ALL"},
        )

    @patch("t_dentrix_service.ascend_service.AscendRequests.get_aging_balance")
    def test_get_aging_balance_for_guarantor_ownership(self, mock_get_aging_balance):
        """Test aging balance retrieval for guarantor ownership."""
        expected_response = {"balance": 250}
        mock_get_aging_balance.return_value = expected_response

        service = TestAscendService._generate_ascend_service_instance()
        patient_id = "guarantor456"

        result = service.get_aging_balance_for_guarantor_ownership(patient_id)

        assert result == expected_response
        mock_get_aging_balance.assert_called_once_with(
            {"patientId": patient_id, "ownership": "GUARANTOR", "responseFields": "ALL"},
        )
