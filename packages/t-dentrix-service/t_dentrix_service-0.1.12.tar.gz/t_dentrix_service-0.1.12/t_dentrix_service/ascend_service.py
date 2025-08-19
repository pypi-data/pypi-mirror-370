"""Contains AscendService class."""


from t_dentrix_service.models.ownership_types import OwnershipTypes
from t_dentrix_service.operations.ascend_requests import AscendRequests


class AscendService(AscendRequests):
    """Contains Service methods for the official Ascend API."""

    def get_plan_benefit(
        self,
        plan_coverage_id: str,
        response_fields: str | None = None,
        filter: str | None = None,
        page: str | None = None,
        page_size: str | None = None,
        last_id: str | None = None,
    ) -> dict:
        """Extracts the plan benefit table for a patient.

        Args:
            plan_coverage_id (str): The plan coverage ID.
            response_fields (str, optional): A comma-delimited list of field names to include in the response data.
            filter (str, optional): Specifies the criteria by which to filter the patient insurance plans.
            page (str, optional): Page number for pagination control.
            page_size (str, optional): Page size for pagination control.
            last_id (str, optional): The biggest patient insurance plan ID from the previous page.

        Returns:
            dict: The full plan benefit table.
        """
        params = {
            "responseFields": response_fields,
            "filter": filter,
            "page": page,
            "pageSize": page_size,
            "lastId": last_id,
        }
        payload_list = self.get_patient_insurance_plans(params)

        for payload in payload_list:
            if (
                payload["subscriberInsurancePlan"]["carrierInsurancePlan"]["inNetworkCoverage"]["id"]
                == plan_coverage_id
            ):
                return payload
        return {}

    def fetch_patient_insurance_plan_by_id(
        self,
        patient_insurance_plan_id: int,
        response_fields: str | None = None,
    ) -> dict:
        """Returns a patient insurance plan by entry ID.

        Args:
            patient_insurance_plan_id (int): The ID of Patient Insurance Plan.
            response_fields (str, optional): Comma-delimited list of field names to include in the response data.

        Returns:
            dict: The patient insurance plan.
        """
        params = {"responseFields": response_fields} if response_fields else {}
        return self.get_patient_insurance_plan_by_id(patient_insurance_plan_id, params)

    def get_aging_balance_for_patient_ownership(self, patient_id: str, response_fields: str = "ALL") -> dict:
        """Get aging balance for a patient based on an ownership type.

        Args:
            patient_id (str): patient backend id
            response_fields (str, optional): Comma-delimited list of fields to include in the response.
                Use "ALL" to return all fields. Defaults to "ALL".

        Returns:
            dict: Aging balance information
        """
        params = {
            "patientId": patient_id,
            "ownership": OwnershipTypes.PATIENT,
            "responseFields": response_fields,
        }
        return self.get_aging_balance(params)

    def get_aging_balance_for_guarantor_ownership(self, patient_id: str, response_fields: str = "ALL") -> dict:
        """Get aging balance for a patient based on an ownership type.

        Args:
            patient_id (str): patient backend id
            response_fields (str, optional): Comma-delimited list of fields to include in the response.
                Use "ALL" to return all fields. Defaults to "ALL".

        Returns:
            dict: Aging balance information
        """
        params = {
            "patientId": patient_id,
            "ownership": OwnershipTypes.GUARANTOR,
            "responseFields": response_fields,
        }
        return self.get_aging_balance(params)
