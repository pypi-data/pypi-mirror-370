#!/usr/bin/env python
"""Tests for `t_dentrix_service` package."""
from copy import copy
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

import pytest
from requests import Response
from requests.exceptions import HTTPError

from t_dentrix_service import DentrixService
from t_dentrix_service.dentrix_service import AttachmentTypes
from t_dentrix_service.models.dtos.aged_receivables import AgedReceivable
from t_dentrix_service.exceptions import (
    DentrixLocationIdNotFound,
    LocationNameNotFoundError,
    NoBillingStatementsInfoError,
    NoLedgerBalanceError,
    NoResultsError,
    PatientNotFoundError,
)
from t_dentrix_service.models.activity_status import Status
from t_dentrix_service.models.dtos.billing_statement import BillingStatement
from t_dentrix_service.models.dtos.charge import Charge
from t_dentrix_service.models.dtos.document import Document
from t_dentrix_service.models.dtos.ledger_balance import LedgerBalance
from t_dentrix_service.models.dtos.location import Location
from t_dentrix_service.models.dtos.patient import Patient, PatientInfo, PatientSearchResult
from t_dentrix_service.models.dtos.patient_ledger_transaction import PatientLedgerTransaction
from t_dentrix_service.models.dtos.patient_procedure import UnattachedProcedure, UnattachedProcedureMetadata
from t_dentrix_service.models.dtos.payer import Payer
from t_dentrix_service.models.dtos.procedure_code import ProcedureCode
from t_dentrix_service.models.dtos.provider import Provider
from t_dentrix_service.models.dtos.schedules import Schedule
from t_dentrix_service.models.dtos.xray import XrayExam, XrayImage
from t_dentrix_service.utils.converters import convert_timestamp_to_date
from tests.mock_data import MockData
from t_dentrix_service.models.dtos.transaction import Transaction
from t_dentrix_service.models.ownership_types import OwnershipTypes


class TestDentrixService:
    """Smoke tests of the package."""

    def test_initialization(self):
        """Initialization test."""
        assert DentrixService({"username": "", "password": ""})

        assert DentrixService(("", ""))

        @dataclass
        class MockCreds:
            username: str
            password: str

        creds_object = MockCreds("", "")

        assert DentrixService(creds_object)

    def test_proxy_initialization(self):
        """Tests Dentrix Service initialization with proxy credentials."""
        assert DentrixService(dentrix_credentials=("", ""), proxy_credentials={"username": "", "password": ""})
        assert DentrixService(dentrix_credentials=("", ""), proxy_credentials=("", ""))

        @dataclass
        class MockCreds:
            username: str
            password: str

        creds_object = MockCreds("", "")

        assert DentrixService(dentrix_credentials=("", ""), proxy_credentials=creds_object)

    def _generate_mock_response(self, status_code: int) -> Response:
        response = Response()
        response.status_code = status_code
        return response

    def _generate_dentrix_service_instance(self) -> DentrixService:
        """Returns a new copy of the DentrixService object everytime it's called."""
        return copy(DentrixService({"username": "", "password": ""}))

    @patch("t_dentrix_service.DentrixService._get_locations_info")
    def test_get_location_id_by_name(self, mock_loc_info: MagicMock):
        """Tests the get_location_id_by_name method."""
        mock_loc_info.return_value = MockData.LOCATIONS_INFO
        test_ds = self._generate_dentrix_service_instance()

        assert test_ds.get_location_id_by_name("99 - Placeholder Dental Center") == 9000000003333
        assert test_ds.get_location_id_by_name("Placeholder Dental Center") == 9000000003333
        assert test_ds.get_location_id_by_name("Placeholder Dental") == 9000000003333
        assert test_ds.get_location_id_by_name("PLACEHOLDER DENTAL CENTER") == 9000000003333
        assert test_ds.get_location_id_by_name("placeholder dental center") == 9000000003333

    @patch("t_dentrix_service.DentrixService._get_locations_info")
    @patch("t_dentrix_service.DentrixService._change_location")
    def test_change_location(self, mock_location_change: MagicMock, mock_loc_info: MagicMock):
        """Tests the change_location method."""
        mock_loc_info.return_value = MockData.LOCATIONS_INFO
        mock_location_change.return_value = None
        test_ds = self._generate_dentrix_service_instance()

        test_ds.change_location(9000000003333)
        test_ds.change_location("9000000003333")

        with pytest.raises(LocationNameNotFoundError):
            test_ds.change_location("Incorrect Mock Dental Center", by_name=True)

        with patch(
            "t_dentrix_service.DentrixService._change_location",
            side_effect=HTTPError(response=self._generate_mock_response(500)),
        ), pytest.raises(DentrixLocationIdNotFound):
            test_ds.change_location(123)

    @patch("t_dentrix_service.DentrixService._update_patient_info")
    def test_updates_chart_number_correctly(self, mock_update_patient_info: MagicMock):
        """Tests the update_chart_number method."""
        test_ds = self._generate_dentrix_service_instance()
        patient_info = {"id": 123}
        chart_number = "456"

        test_ds.update_chart_number(patient_info, chart_number)

        mock_update_patient_info.assert_called_once_with({"id": 123, "chartNumber": "456"})

    @patch("t_dentrix_service.DentrixService._get_problem_data")
    def test_gets_unattached_procedures_correctly(self, mock_get_problem_data: MagicMock):
        """Tests the get_unattached_procedures method."""
        mock_get_problem_data.return_value = MockData.UNATTACHED_PROCEDURE_PAYLOAD
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_unattached_procedures()

        expected = [UnattachedProcedure.from_payload(item) for item in MockData.UNATTACHED_PROCEDURE_PAYLOAD]

        assert result == expected
        mock_get_problem_data.assert_called_once_with({"goalType": "UNATTACHED_PROCEDURE"})

    @patch("t_dentrix_service.DentrixService._get_problem_data")
    def test_gets_unsent_claims_correctly(self, mock_get_problem_data: MagicMock):
        """Tests the get_unsent_claims method."""
        mock_get_problem_data.return_value = MockData.UNSENT_CLAIMS_PAYLOAD
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_unsent_claims()

        expected = [UnattachedProcedureMetadata.from_payload(item) for item in MockData.UNSENT_CLAIMS_PAYLOAD]
        assert result == expected
        mock_get_problem_data.assert_called_once_with({"goalType": "UNSENT_CLAIMS"})

    @patch("t_dentrix_service.DentrixService._get_problem_data")
    def test_gets_overdue_claim_info_correctly(self, mock_get_problem_data: MagicMock):
        """Tests the get_overdue_claim_info method."""
        mock_get_problem_data.return_value = [{"claimId": 1}]
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_overdue_claim_info(1)

        assert result == {"claimId": 1}
        mock_get_problem_data.assert_called_once_with({"goalType": "OVERDUE_CLAIMS", "claimId": 1})

    @patch("t_dentrix_service.DentrixService._get_solution_data")
    def test_gets_patient_procedures_correctly(self, mock_get_solution_data: MagicMock):
        """Tests the get_patient_procedures method."""
        mock_get_solution_data.return_value = [{"procedure": "test"}]
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_patient_procedures("entity_id", "2023-01-01", "entity_type")

        assert result == {"procedure": "test"}
        mock_get_solution_data.assert_called_once_with(
            {"problemType": "UNATTACHED_PROCEDURE"},
            "entity_id",
            "entity_type",
            "2023-01-01",
        )

    @patch("t_dentrix_service.DentrixService._get_solution_data")
    def test_gets_patient_unsent_claim_correctly(self, mock_get_solution_data: MagicMock):
        """Tests the get_patient_unsent_claim method."""
        mock_get_solution_data.return_value = [{"claim": "test"}]
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_patient_unsent_claim("entity_id", "entity_type", "2023-01-01")

        assert result == {"claim": "test"}
        mock_get_solution_data.assert_called_once_with(
            {"problemType": "UNSENT_CLAIM"},
            "entity_id",
            "entity_type",
            "2023-01-01",
        )

    @patch("t_dentrix_service.DentrixService._get_schedules")
    @patch("t_dentrix_service.DentrixService._get_current_location")
    def test_get_schedules(self, mocked_location: MagicMock, mocked_schedules: MagicMock):
        """Test for get_schedules method returning a Schedule object."""
        TEST_LOC_ID = 9000000003333
        EPOCH_TIMESTAMP = 28800000

        def epoch_check_side_effect(params):
            assert params["isWeekView"] is True
            if params["dates"] == EPOCH_TIMESTAMP and params["locationIds"] == TEST_LOC_ID:
                return MockData.SCHEDULES
            else:
                raise AssertionError("Unexpected arguments received")

        mocked_location.return_value = MockData.SINGULAR_LOCATION_INFO
        mocked_schedules.side_effect = epoch_check_side_effect

        ds = self._generate_dentrix_service_instance()
        result = ds.get_schedules(date(1970, 1, 1))

        assert isinstance(result, Schedule)

    @patch("t_dentrix_service.DentrixService.get_schedules")
    def test_patient_has_schedules(self, mocked_schedules: MagicMock):
        """Test for patient has schedules method."""
        mocked_schedules.return_value = MockData.SCHEDULES

        ds = self._generate_dentrix_service_instance()

        result = ds.patient_has_schedules(301)
        assert result is True

        result = ds.patient_has_schedules(401)
        assert result is False

    @patch("t_dentrix_service.DentrixService._get_insurance_claim")
    @patch("t_dentrix_service.DentrixService._update_claim")
    def test_adds_attachment_to_claim_correctly(self, mock_update_claim, mock_get_insurance_claim):
        """Tests the add_attachment_to_claim method."""
        mock_get_insurance_claim.return_value = {"imageAttachments": [], "claimAttachments": []}
        test_ds = self._generate_dentrix_service_instance()

        test_ds.add_attachment_to_claim(123, AttachmentTypes.XRAY, ["attachment1"])

        mock_get_insurance_claim.assert_called_once_with(123)
        mock_update_claim.assert_called_once_with(123, {"imageAttachments": ["attachment1"], "claimAttachments": []})

    @patch("t_dentrix_service.DentrixService._search_patient")
    def test_search_patient(self, mocked_search: MagicMock):
        """Test for search patient process."""
        ds = self._generate_dentrix_service_instance()

        mocked_search.return_value = []
        with pytest.raises(NoResultsError):
            ds.search_patient("John", "Dohn")

        mocked_search.return_value = [MockData.PATIENT]
        with pytest.raises(PatientNotFoundError):
            ds.search_patient("John", "Dohn", strict_search=True)

        result = ds.search_patient(
            first_name="John",
            last_name="Doe",
            date_of_birth=convert_timestamp_to_date(
                MockData.PATIENT["dateOfBirth"],
            ),
        )

        assert result == [Patient.from_payload(MockData.PATIENT)]

        result = ds.search_patient(
            first_name="John",
            last_name="Doe",
            activity_status=Status.ACTIVE,
        )

        assert result == [Patient.from_payload(MockData.PATIENT)]

        result = ds.search_patient(
            first_name="John",
            last_name="Doe",
            activity_status=Status.ACTIVE,
            date_of_birth=convert_timestamp_to_date(
                MockData.PATIENT["dateOfBirth"],
            ),
            strict_search=True,
        )

        assert result == Patient.from_payload(MockData.PATIENT)

    @patch("t_dentrix_service.DentrixService._get_current_location")
    def test_get_current_location(self, mocked_get_location: MagicMock):
        """Test public get current location."""
        mocked_get_location.return_value = MockData.SINGULAR_LOCATION_INFO

        ds = self._generate_dentrix_service_instance()
        result = ds.get_current_location()

        assert result == Location.from_payload(MockData.SINGULAR_LOCATION_INFO)

    @patch("t_dentrix_service.DentrixService._get_locations_info")
    def test_get_locations(self, mocked_get_locations: MagicMock):
        """Test public get locations method."""
        mocked_get_locations.return_value = MockData.LOCATIONS_INFO

        ds = self._generate_dentrix_service_instance()
        result = ds.get_locations()

        assert result == [Location.from_payload(location) for location in MockData.LOCATIONS_INFO]

    @patch("t_dentrix_service.DentrixService.query_aged_receivables")
    @patch("t_dentrix_service.dentrix_service.now_timestamp")
    def test_query_aged_receivables_patients_list_valid(self, mock_now_timestamp, mock_query):
        """Test when receivables and agedReceivables are valid."""
        test_ds = self._generate_dentrix_service_instance()
        mock_now_timestamp.return_value = 1700000000

        mock_query.return_value = {"receivables": {"agedReceivables": MockData.AGED_RECEIVABLES}}

        payload = {"locations": [12345], "period": "ALL"}
        result = test_ds.query_aged_receivables_patients_list(payload)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], AgedReceivable)
        assert result[0].guarantor == "John Doe"
        assert payload["asOfDate"] == 1700000000
        mock_query.assert_called_once_with(payload=payload)

    @patch("t_dentrix_service.DentrixService.query_aged_receivables")
    @patch("t_dentrix_service.dentrix_service.now_timestamp")
    def test_query_aged_receivables_patients_list_none(self, mock_now_timestamp, mock_query):
        """Test when receivables is None or invalid."""
        test_ds = self._generate_dentrix_service_instance()
        mock_now_timestamp.return_value = 1700000000

        mock_query.return_value = {"receivables": None}

        payload = {"locations": [12345], "period": "ALL"}
        result = test_ds.query_aged_receivables_patients_list(payload)

        assert result == []
        assert payload["asOfDate"] == 1700000000
        mock_query.assert_called_once_with(payload=payload)

    @patch("t_dentrix_service.DentrixService._get_apply_credits")
    def test_apply_credits_for_guarantor(self, mock_get_apply_credits: MagicMock):
        """Test apply credits for garantor method."""
        test_ds = self._generate_dentrix_service_instance()
        test_ds.apply_credits_for_guarantor("patient123")

        mock_get_apply_credits.assert_called_once_with("GUARANTOR_VIEW", "patient123")

    @patch("t_dentrix_service.DentrixService._get_apply_credits")
    def test_apply_credits_for_patient(self, mock_get_apply_credits: MagicMock):
        """Test apply credits for patient method."""
        test_ds = self._generate_dentrix_service_instance()
        test_ds.apply_credits_for_patient("patient456")

        mock_get_apply_credits.assert_called_once_with("PATIENT_VIEW", "patient456")

    @patch("t_dentrix_service.DentrixService._query_billing_statements")
    def test_query_billing_statements(self, mock_query_billing_statement: MagicMock):
        """Tests the query_billing_statement process."""
        test_ds = self._generate_dentrix_service_instance()
        mock_query_billing_statement.return_value = MockData.BILLING_STATEMENT

        result = test_ds.query_billing_statements()
        assert result == BillingStatement.from_payload(MockData.BILLING_STATEMENT)

        mock_query_billing_statement.return_value = {}

        with pytest.raises(NoBillingStatementsInfoError):
            test_ds.query_billing_statements()

    @patch("t_dentrix_service.DentrixService._unlock_ledger_for_modification")
    @patch("t_dentrix_service.DentrixService._encrypt_password")
    def test_unlocks_ledger_for_modification_correctly(
        self,
        mock_encrypt_password: MagicMock,
        mock_unlock_ledger: MagicMock,
    ):
        """Tests the unlock_ledger_for_modification method."""
        mock_encrypt_password.return_value = "encrypted_password"
        mock_unlock_ledger.return_value = {"status": "success"}
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.unlock_ledger_for_modification(123)

        mock_encrypt_password.assert_called_once()
        mock_unlock_ledger.assert_called_once_with(
            {
                "entityId": 123,
                "time": "FIFTEEN_MINUTES",
                "userLogin": test_ds.username,
                "userPassword": "encrypted_password",
            },
        )
        assert result == {"status": "success"}

    @patch("t_dentrix_service.DentrixService._get_transaction_charges")
    def test_get_transaction_charges(self, mock_get_transaction_charges: MagicMock):
        """Tests the get_transaction_charges method returns Charge objects."""
        mock_get_transaction_charges.return_value = MockData.CHARGE

        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_transaction_charges("trans_id", "patient_id", 100.0, "type", "GUARANTOR_VIEW")

        mock_get_transaction_charges.assert_called_once_with(
            {
                "amount": 100.0,
                "ledgerView": "GUARANTOR_VIEW",
                "creditId": "trans_id",
                "patientId": "patient_id",
            },
            "type",
        )

        expected = [
            Charge(
                charge_id=8880098974472,
                date=1710802250510,
                patient="Test 1",
                provider="ZJDC",
                code="D5750",
                description="Lab Reline Full Upper Denture",
                charge=567.0,
                other_credits=512.6,
                applied=84.4,
                balance=0.0,
                is_attached_to_payment_plan="NONE",
                exceptions=None,
                patient_procedure_id=8880184209425,
                bill_to_insurance=True,
                guarantor_portion=0,
                location=Location.from_payload({"id": 8800000000714}),
                tooth="",
                surfaces="",
            )
        ]

        assert result == expected

    @patch("t_dentrix_service.DentrixService._update_transaction")
    @patch("t_dentrix_service.DentrixService.unlock_ledger_for_modification")
    def test_updates_transaction_correctly(self, mock_unlock_ledger: MagicMock, mock_update_transaction: MagicMock):
        """Tests the update_transaction method."""
        mock_unlock_ledger.return_value = None
        mock_update_transaction.return_value = {"status": "updated"}
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.update_transaction(123, {"field": "value"})

        mock_unlock_ledger.assert_called_once_with(123)
        mock_update_transaction.assert_called_once_with(123, {"field": "value"}, "adjustment/credit")
        assert result == {"status": "updated"}

    @patch("t_dentrix_service.DentrixService._is_billing_statement_locked")
    def test_is_billing_statement_locked(self, mock_is_locked: MagicMock):
        """Test is billing statement locked process."""
        mock_is_locked.return_value = MockData.IS_BILLING_LOCKED
        ds = self._generate_dentrix_service_instance()

        result = ds.is_billing_statement_locked()
        assert result is False

    @patch("t_dentrix_service.DentrixService._post_appointment_note")
    @patch("t_dentrix_service.DentrixService._change_location")
    def test_posts_appointment_note_correctly(
        self,
        mock_change_location: MagicMock,
        mock_post_appointment_note: MagicMock,
    ):
        """Tests the post_appointment_note method."""
        mock_post_appointment_note.return_value = {"status": "success"}
        test_ds = self._generate_dentrix_service_instance()
        location_id = 123
        request_body = {"note": "Appointment note", "patient_id": 456}

        result = test_ds.post_appointment_note(location_id, request_body)

        mock_change_location.assert_called_once_with(location_id)
        mock_post_appointment_note.assert_called_once_with(request_body)
        assert result == {"status": "success"}

    @patch("t_dentrix_service.DentrixService._post_appointment_note")
    @patch("t_dentrix_service.DentrixService._change_location")
    def test_handles_invalid_location_id(self, mock_change_location: MagicMock, mock_post_appointment_note: MagicMock):
        """Tests the post_appointment_note method with an invalid location id."""
        mock_change_location.side_effect = DentrixLocationIdNotFound("Location not found")
        test_ds = self._generate_dentrix_service_instance()
        location_id = "invalid"
        request_body = {"note": "Appointment note", "patient_id": 456}

        with pytest.raises(DentrixLocationIdNotFound):
            test_ds.post_appointment_note(location_id, request_body)

        mock_change_location.assert_called_once_with(location_id)
        mock_post_appointment_note.assert_not_called()

    @patch("t_dentrix_service.DentrixService._get_all_payers")
    def test_gets_payer_info_correctly(self, mock_get_all_payers: MagicMock):
        """Tests the get_payer_info method."""
        mock_get_all_payers.return_value = MockData.PAYERS
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_payer_info()

        mock_get_all_payers.assert_called_once()
        assert result == [
            Payer(carrier_id="123", carrier_name="Payer1", payer_id="12"),
            Payer(carrier_id="456", carrier_name="Payer2", payer_id="34"),
        ]

    @patch("t_dentrix_service.DentrixService._get_all_payers")
    def test_handles_empty_payer_list(self, mock_get_all_payers: MagicMock):
        """Tests the get_payer_info method when the payer list is empty."""
        mock_get_all_payers.return_value = []
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_payer_info()

        mock_get_all_payers.assert_called_once()
        assert result == []

    @patch("t_dentrix_service.DentrixService._get_ledger_list")
    def test_get_patient_ledger_transactions_guarantor_view(self, mock_get_ledger_list):
        """Test ledger transactions for GUARANTOR_VIEW."""
        mock_get_ledger_list.return_value = MockData.PATIENT_LEDGER_TRANSACTION

        expected_result = [PatientLedgerTransaction.from_payload(item) for item in MockData.PATIENT_LEDGER_TRANSACTION]

        test_ds = self._generate_dentrix_service_instance()
        patient_id = 123
        view = "GUARANTOR_VIEW"

        result = test_ds.get_patient_ledger_transactions(patient_id, view=view)

        expected_params = {
            "autoScrollToRecentTransactions": True,
            "range": "ALL_HISTORY_DATE_RANGE",
            "sorting": "BY_STATEMENT",
            "view": "GUARANTOR_VIEW",
            "showHistory": False,
            "showTime": False,
            "showDeleted": True,
            "showXfers": True,
            "resetHistory": False,
            "isSinceLastZeroBalanceEnabled": True,
            "filteredDateRange": "All history",
        }

        assert result == expected_result
        mock_get_ledger_list.assert_called_once_with(patient_id, expected_params)

    @patch("t_dentrix_service.DentrixService._get_ledger_list")
    def test_get_patient_ledger_transactions_patient_view(self, mock_get_ledger_list):
        """Test ledger transactions for PATIENT_VIEW."""
        mock_get_ledger_list.return_value = MockData.PATIENT_LEDGER_TRANSACTION

        expected_result = [PatientLedgerTransaction.from_payload(item) for item in MockData.PATIENT_LEDGER_TRANSACTION]

        test_ds = self._generate_dentrix_service_instance()
        patient_id = 123
        view = "PATIENT_VIEW"

        result = test_ds.get_patient_ledger_transactions(patient_id, view=view)

        expected_params = {
            "autoScrollToRecentTransactions": True,
            "range": "ALL_HISTORY_DATE_RANGE",
            "sorting": "BY_STATEMENT",
            "view": "PATIENT_VIEW",
            "showHistory": False,
            "showTime": False,
            "showDeleted": True,
            "showXfers": True,
            "resetHistory": False,
            "isSinceLastZeroBalanceEnabled": True,
            "filteredDateRange": "All history",
        }

        assert result == expected_result
        mock_get_ledger_list.assert_called_once_with(patient_id, expected_params)

    @patch("t_dentrix_service.dentrix_service.DentrixService._get_ledger_information_by_view")
    def test_get_ledger_information_by_patient_success(self, mock_get_ledger_info: MagicMock):
        """Test get_ledger_information_by_patient_refactored method with valid data."""
        test_ds = TestDentrixService()._generate_dentrix_service_instance()
        patient_id = "patient789"
        mock_payload = MockData.LEDGER_INFO

        mock_get_ledger_info.return_value = MockData.LEDGER_INFO

        result = test_ds.get_ledger_information_by_patient(patient_id)

        assert result == LedgerBalance.from_payload(mock_payload)
        mock_get_ledger_info.assert_called_once_with(patient_id, {"view": "PATIENT"})

    @patch("t_dentrix_service.dentrix_service.DentrixService._get_ledger_information_by_view")
    def test_get_ledger_information_by_patient_failure(self, mock_get_ledger_info: MagicMock):
        """Test get_ledger_information_by_patient_refactored raises exception when no data is returned."""
        test_ds = TestDentrixService()._generate_dentrix_service_instance()
        patient_id = "patient789"
        mock_get_ledger_info.return_value = {}

        with pytest.raises(NoLedgerBalanceError, match="No Ledger Balance Info found on Dentrix"):
            test_ds.get_ledger_information_by_patient(patient_id)

        mock_get_ledger_info.assert_called_once_with(patient_id, {"view": "PATIENT"})

    @patch("t_dentrix_service.dentrix_service.DentrixService._get_ledger_information_by_view")
    def test_get_ledger_information_by_guarantor_success(self, mock_get_ledger_info: MagicMock):
        """Test get_ledger_information_by_patient_refactored method with valid data."""
        test_ds = TestDentrixService()._generate_dentrix_service_instance()
        patient_id = "patient789"
        mock_payload = MockData.LEDGER_INFO

        mock_get_ledger_info.return_value = mock_payload

        result = test_ds.get_ledger_information_by_guarantor(patient_id)

        assert result == LedgerBalance.from_payload(mock_payload)
        mock_get_ledger_info.assert_called_once_with(patient_id, {"view": "GUARANTOR"})

    @patch("t_dentrix_service.dentrix_service.DentrixService._get_ledger_information_by_view")
    def test_get_ledger_information_by_guarantor_failure(self, mock_get_ledger_info: MagicMock):
        """Test get_ledger_information_by_patient_refactored raises exception when no data is returned."""
        test_ds = TestDentrixService()._generate_dentrix_service_instance()
        patient_id = "patient789"
        mock_get_ledger_info.return_value = {}

        with pytest.raises(NoLedgerBalanceError, match="No Ledger Balance Info found on Dentrix"):
            test_ds.get_ledger_information_by_guarantor(patient_id)

        mock_get_ledger_info.assert_called_once_with(patient_id, {"view": "GUARANTOR"})

    @patch("t_dentrix_service.DentrixService._get_providers_from_location")
    def test_gets_providers_from_location_correctly(self, mock_get_providers: MagicMock):
        """Tests the get_providers_from_location method."""
        mock_get_providers.return_value = MockData.PROVIDERS
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_providers_from_location(123)

        assert result == [Provider.from_payload(provider) for provider in MockData.PROVIDERS]
        mock_get_providers.assert_called_once_with(123)

    @patch("t_dentrix_service.DentrixService._get_patient_basic_information")
    def test_gets_patient_information_correctly(self, mock_get_patient_info: MagicMock):
        """Tests the get_patient_information method."""
        mock_get_patient_info.return_value = MockData.PATIENT_INFO
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_patient_information(123)

        assert result == PatientInfo.from_payload(MockData.PATIENT_INFO)
        mock_get_patient_info.assert_called_once_with(123)

    @patch("t_dentrix_service.DentrixService._get_patient_basic_information")
    def test_raises_error_when_patient_not_found(self, mock_get_patient_info: MagicMock):
        """Tests the get_patient_information method when patient is not found."""
        mock_get_patient_info.return_value = None
        test_ds = self._generate_dentrix_service_instance()

        with pytest.raises(PatientNotFoundError):
            test_ds.get_patient_information(123)

    @patch("t_dentrix_service.DentrixService._get_xray_exams")
    @patch("t_dentrix_service.DentrixService.gather_claim_imaging_cookies")
    def test_gets_xray_exams_correctly(self, mock_gather_cookies: MagicMock, mock_get_exams: MagicMock):
        """Tests the get_xray_exams method."""
        mock_get_exams.return_value = MockData.XRAY_EXAMS
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_xray_exams("123", "locator")

        assert result == [XrayExam.from_payload(exam) for exam in MockData.XRAY_EXAMS]
        mock_gather_cookies.assert_called_once_with("123", "locator")
        mock_get_exams.assert_called_once_with("123")

    @patch("t_dentrix_service.DentrixService._get_xray_images")
    def test_gets_xray_images_correctly(self, mock_get_images: MagicMock):
        """Tests the get_xray_images method."""
        mock_get_images.return_value = MockData.XRAY_IMAGES
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_xray_images(123)

        assert result == [XrayImage.from_payload(image) for image in MockData.XRAY_IMAGES]
        mock_get_images.assert_called_once_with(123)

    @patch("t_dentrix_service.DentrixService._get_document_list")
    def test_gets_document_list_correctly(self, mock_get_documents: MagicMock):
        """Tests the get_document_list method."""
        mock_get_documents.return_value = MockData.DOCUMENTS
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_document_list(123)

        assert result == [Document.from_payload(doc) for doc in MockData.DOCUMENTS]
        mock_get_documents.assert_called_once_with(123)

    @patch("t_dentrix_service.DentrixService._get_procedure_codes")
    def test_gets_procedure_codes_correctly(self, mock_get_codes: MagicMock):
        """Tests the get_procedure_codes method."""
        mock_get_codes.return_value = MockData.PROCEDURE_CODES
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.get_procedure_codes()

        assert result == [ProcedureCode.from_payload(code) for code in MockData.PROCEDURE_CODES]
        mock_get_codes.assert_called_once()

    @patch("t_dentrix_service.DentrixService._get_guarantor_related_patients")
    def test_get_guarantor_dependents(self, mock_get_related_patients):
        """Test for get_guarantor_related_patients method."""
        mock_get_related_patients.return_value = [
            {"id": 1, "name": "Alice Smith"},
            {"id": 2, "name": "Bob Johnson"},
            {"id": 3, "name": "Charlie"},
        ]

        test_ds = self._generate_dentrix_service_instance()
        result = test_ds.get_guarantor_dependents("123")

        assert len(result) == len(mock_get_related_patients.return_value)
        for patient, expected in zip(result, mock_get_related_patients.return_value):
            assert patient.id == expected["id"]
            assert patient.name == expected["name"]

        mock_get_related_patients.assert_called_once_with("123")

    @patch("t_dentrix_service.DentrixService._get_transaction_payload")
    def test_get_transaction_payload(self, mock_get_payload):
        """Test for get_transaction_payload method."""
        mock_payload = MockData.TRANSACTION
        mock_get_payload.return_value = mock_payload

        service = self._generate_dentrix_service_instance()
        transaction_id = "8930132516338"

        transaction_obj = service.get_transaction_payload(transaction_id)

        assert isinstance(transaction_obj, Transaction)
        assert transaction_obj.id == mock_payload["id"]
        assert transaction_obj.location.id == mock_payload["location"]["id"]
        assert transaction_obj.amount == mock_payload["amount"]
        assert transaction_obj.ownership == OwnershipTypes.PATIENT
        assert transaction_obj.patient_name == mock_payload["patientName"]
        assert transaction_obj.is_voided is False

    @patch("t_dentrix_service.DentrixService._get_patients_information")
    def test_fetch_patients_information(self, mock_get_patients_info):
        """Tests the fetch_patients_information method."""
        mock_get_patients_info.return_value = MockData.PATIENTS_INFO
        test_ds = self._generate_dentrix_service_instance()

        result = test_ds.fetch_patients_information([800000123456])

        assert result == [PatientSearchResult.from_payload(patient) for patient in MockData.PATIENTS_INFO]
        mock_get_patients_info.assert_called_once_with([800000123456])

    @pytest.mark.parametrize(
        "doc_id, patient_id, target_path, expected_path",
        [
            (123, 456, None, Path("123.pdf")),
            (123, 456, Path("custom/path.pdf"), Path("custom/path.pdf")),
        ],
    )
    @patch("t_dentrix_service.DentrixService._download_document")
    @patch("builtins.open", create=True)
    def test_download_document(self, mock_open, mock_download_document, doc_id, patient_id, target_path, expected_path):
        """Tests the download_document method."""
        test_ds = self._generate_dentrix_service_instance()
        mock_download_document.return_value = b"test content"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = test_ds.download_document(doc_id, patient_id, target_path)

        assert result == expected_path
        mock_download_document.assert_called_once_with(doc_id, patient_id)
        mock_open.assert_called_once_with(expected_path, "wb")
        mock_file.write.assert_called_once_with(b"test content")

    @patch("t_dentrix_service.DentrixService._download_document")
    @patch("builtins.open", create=True)
    def test_download_document_error_cases(self, mock_open, mock_download_document):
        """Tests error cases for download_document method."""
        test_ds = self._generate_dentrix_service_instance()

        # Test download failure
        mock_download_document.side_effect = Exception("Download failed")
        with pytest.raises(Exception, match="Download failed"):
            test_ds.download_document(123, 456)

        # Test file write failure
        mock_download_document.side_effect = None
        mock_download_document.return_value = b"test content"
        mock_open.side_effect = PermissionError("Access denied")
        with pytest.raises(PermissionError, match="Access denied"):
            test_ds.download_document(123, 456)
