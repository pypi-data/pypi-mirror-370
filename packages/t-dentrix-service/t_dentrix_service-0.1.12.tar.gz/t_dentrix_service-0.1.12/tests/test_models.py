"""Contains test for dtos models."""

from copy import copy

from t_dentrix_service.models.dtos.billing_statement import BillingStatement, StatementHeader
from t_dentrix_service.models.dtos.location import Location
from t_dentrix_service.models.dtos.patient import Patient
from tests.mock_data import MockData


class TestModels:
    """Battery of test for our dtos models."""

    def test_billing_statement_model_initialization_from_nullified_payload(self):
        """Tests if billing statement model can be generated from nullified payload."""
        nullified_billing_statement = self._nullify_payload(MockData.BILLING_STATEMENT, exceptions=["id"])
        assert BillingStatement.from_payload(nullified_billing_statement)

    def test_statement_header_model_initialization_from_nullified_payload(self):
        """Tests if statement header model can be generated from nullified payload."""
        print(MockData.BILLING_STATEMENT)
        nullified_statement_header = self._nullify_payload(
            MockData.BILLING_STATEMENT["statementHeaders"][0],
            exceptions=["id", "balance", "name"],
        )
        assert StatementHeader.from_payload(nullified_statement_header)

    def test_patient_model_initialization_from_nullified_payload(self):
        """Tests if patient model can be generated from nullified payload."""
        nullified_patient = self._nullify_payload(MockData.PATIENT, exceptions=["id", "firstName", "lastName"])
        assert Patient.from_payload(nullified_patient)

    def test_location_model_initialization_from_nullified_payload(self):
        """Tests if location model can be generated from nullified payload."""
        nullified_location = self._nullify_payload(MockData.SINGULAR_LOCATION_INFO, exceptions=["id", "name"])
        assert Location.from_payload(nullified_location)

    def _nullify_payload(self, payload: dict, exceptions: list[str] = []) -> dict:
        """Nullify payload values as a way to test how processes react to when payload values are None or empty.

        Args:
            payload (dict): Payload to be nullified.
            exceptions (list[str]): key for values that should not be nullified.

        Returns:
            dict: Copy of the payload given with all values set to None.
        """
        nullified_payload = copy(payload)
        for key, value in nullified_payload.items():
            if key in exceptions:
                continue
            if isinstance(value, dict):
                nullified_payload[key] = {}
            elif isinstance(value, list):
                nullified_payload[key] = []
            else:
                nullified_payload[key] = None
        return nullified_payload
