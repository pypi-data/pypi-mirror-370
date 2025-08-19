"""Contains DentrixServiceRequests object."""
import json

from retry import retry

from t_dentrix_service.consts.urls.dentrix_urls import DentrixUrls
from t_dentrix_service.operations.decorators import dentrix_request_handling
from t_dentrix_service.operations.dentrix_login import DentrixServiceLogin
from t_dentrix_service.utils.encrypt import encrypt_with_rsa
from t_dentrix_service.utils.logger import logger


class DentrixServiceRequests(DentrixServiceLogin):
    """Segment of the Dentrix Service solely responsible with handling requests."""

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_locations_info(self) -> list[dict]:
        """Gets the location information from Dentrix."""
        response = self.session.get(DentrixUrls.LOCATIONS_URL, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _change_location(self, location_id: int) -> dict:
        """Changes location set in dentrix to the location that refers to the id provided."""
        payload = {"id": location_id}
        headers = self._headers(content_type="application/x-www-form-urlencoded; charset=UTF-8")
        response = self.session.post(DentrixUrls.SET_LOCATION_URL, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_schedules(self, params: dict) -> dict:
        """Gather schedules based on a timestamp and location ID, with optional week view."""
        response = self.session.get(DentrixUrls.GET_SCHEDULES, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_current_location(self) -> dict:
        """Method to get the current active location on the dentrix site."""
        response = self.session.get(DentrixUrls.CURRENT_LOCATION, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_providers_from_location(self, location_id: int) -> list:
        """Gets the providers from a location in Dentrix.

        Args:
            location_id (int): The location ID that the providers will be fetched from.

        Returns:
            list: The list of providers from the location.
        """
        url = DentrixUrls.PROVIDERS_FROM_LOCATION_URL(DentrixUrls.BASE_URL, location_id)
        response = self.session.get(url, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_patient_basic_information(self, patient_id: int) -> dict:
        """Gets the patient basic information from Dentrix.

        Args:
            patient_id (str): The patient ID that the basic information will be fetched from.

        Returns:
            dict: The basic information of the patient.
        """
        url = DentrixUrls.PATIENT_INFO_URL(patient_id)
        response = self.session.get(url, headers=self._headers(), timeout=500)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _update_patient_info(self, payload: dict) -> dict:
        """Updates the patient information in Dentrix.

        Args:
            payload (dict): The payload that contains the updated patient information.

        Returns:
            dict: The updated patient information.
        """
        url = DentrixUrls.PATIENT_INFO_URL(payload["id"])
        response = self.session.put(url, headers=self._headers(), json=payload, timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def generate_chart_number(self, patient_information: dict) -> str:
        """Generate chart number for patient.

        Args:
            patient_information (dict): The patient information that is used to generate the chart number,
            the dict should contain the following keys: firstName, lastName.

        Returns:
            str: The generated chart number.
        """
        params = {
            "firstName": patient_information["firstName"],
            "lastName": patient_information["lastName"],
        }
        response = self.session.get(
            DentrixUrls.GENERATE_CHART_NUMBER_URL,
            headers=self._headers(),
            params=params,
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["chartNumber"]

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def perform_claim_action(self, activity: dict) -> dict:
        """This method either creates or sends a claim depending on the activity param.

        Args:
            activity (dict): dict from get_patient_procedures or get_unsent_claims function
            with necessary information to create or send a claim.

        Returns:
            dict: The response from the claim action.
        """
        payload = {
            "description": activity["description"],
            "entityId": activity["entityId"],
            "entityType": activity["entityType"],
            "providerType": activity["providerType"],
            "restVerb": activity["restVerb"],
            "data": activity["data"],
        }
        response = self.session.post(
            DentrixUrls.ACTIVITY_URL,
            headers=self._headers(content_type=""),
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def get_attachments_validation(self, claim_id: int) -> dict:
        """Gets the attachment validations information from Dentrix.

        Args:
            claim_id (int): The claim ID that the attachment validations will be fetched from.

        Returns:
            dict: The attachment validations information.
        """
        payload = {"claimIDs": [claim_id]}
        response = self.session.post(DentrixUrls, headers=self._headers(), json=payload, timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def get_claims_from_payment(self, patient_id: int) -> list:
        """Gets the patient ledger from Dentrix.

        Args:
            patient_id (int): The patient ID that the claims will be fetched from.

        Returns:
            list: The list of claims from the payment window in Dentrix Ledger.
        """
        url = DentrixUrls.GET_CLAIMS_URL(patient_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_ledger_list(self, patient_id: int, params: dict) -> list:
        """Gather claims from ledger page.

        Args:
            patient_id (int): The patient ID that the information will be fetched from.
            params (dict): The parameters that will be used to fetch the information.

        Returns:
            list: The list of information from the ledger page.
        """
        url = DentrixUrls.LEDGER_LIST_URL(patient_id)
        response = self.session.get(url, params=params, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def get_services_info(self, claim_id: int, amount: float) -> list:
        """Gets the claim services information from Dentrix.

        Args:
            claim_id (int): The claim ID that the service information will be fetched from.
            amount (float): The amount that the service information will be fetched from.

        Returns:
            list: The list of services information from the claim.
        """
        url = DentrixUrls.GET_CLAIM_SERVICES_INFO(DentrixUrls.BASE_URL, amount, claim_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_insurance_claim(self, claim_id: int) -> dict:
        """Gets the insurance claim information from Dentrix.

        Args:
            claim_id (int): The claim ID that the insurance claim information will be fetched from.

        Returns:
            dict: The insurance claim information.
        """
        url = DentrixUrls.INSURANCE_CLAIM_URL(claim_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def post_payment(self, payload: dict) -> dict:
        """Post a payment to a claim.

        Args:
            payload (dict): The payload that contains the payment information.

        Returns:
            dict: The response from the payment post.
        """
        response = self.session.post(DentrixUrls.POST_PAYMENT_INFO_URL, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def create_subsequent_insurance_claim(self, claim_id: dict) -> dict:
        """Posts the claim information to Dentrix.

        Args:
            claim_id (dict): The claim ID that the subsequent insurance claim will be created from.

        Returns:
            dict: The response from the subsequent insurance claim creation.
        """
        url = DentrixUrls.SUBSEQUENT_INSURANCE_CLAIM_URL(claim_id)
        response = self.session.post(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _update_claim(self, claim_id: int, payload: dict) -> dict:
        """Updates the claim information in Dentrix.

        Args:
            claim_id (int): The claim ID that the claim information will be updated from.
            payload (dict): The payload that contains the updated claim information.

        Returns:
            dict: The updated claim information.
        """
        url = DentrixUrls.INSURANCE_CLAIM_URL(claim_id)
        response = self.session.put(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def submit_claim(self, claim_id: int, payload: dict) -> dict:
        """Sends the claim information to Dentrix.

        Args:
            claim_id (int): The claim ID that the claim information will be sent from.
            payload (dict): The payload that contains the claim information.

        Returns:
            dict: The response from the claim submission.
        """
        url = DentrixUrls.SUBMIT_CLAIM_URL(claim_id)
        response = self.session.put(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=3, backoff=2)
    def delete_unsent_claim(self, entity_id: str) -> dict:
        """Delete the unsent insurance claim using the provided entity ID.

        Args:
            entity_id (str): The entity ID of the claim that represents the unique identifier of
            the insurance claim that needs to be deleted.

        Returns:
            dict: The response from the claim deletion.
        """
        url = DentrixUrls.INSURANCE_CLAIM_URL(entity_id)
        response = self.session.delete(url, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def get_overdue_claims(self) -> list:
        """Gets the overdue claims list from an Unresolved claims section.

        Returns:
            list: The list of overdue claims.
        """
        response = self.session.get(DentrixUrls.OVERDUE_CLAIMS_URL, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()["data"]["claims"]

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_problem_data(self, params: dict) -> dict:
        """Get problem data for a specific entity.

        Args:
            params (dict): The parameters that will be used to fetch the problem data.

        Returns:
            dict: Data for the specific entity.
        """
        response = self.session.get(DentrixUrls.PROBLEM_URL, headers=self._headers(), params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_solution_data(self, params_to_add: dict, entity_id: str, entity_type: str, date_of_service: str) -> dict:
        """Get solution data for a specific entity.

        Args:
            params_to_add (dict): The parameters that will be added to the request.
            entity_id (str): The entity ID that the solution data will be fetched from.
            entity_type (str): The entity type that the solution data will be fetched from.
            date_of_service (str): The date of service that the solution data will be fetched from.

        Returns:
            dict: Data for the specific entity.
        """
        params = {
            "maxSolutions": "15",
            "entityId": entity_id,
            "entityType": entity_type,
            "dateOfService": date_of_service,
        }
        params.update(params_to_add)
        response = self.session.get(DentrixUrls.SOLUTION_URL, headers=self._headers(), params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def get_deductibles(self, insurance_claim_id: int) -> dict:
        """Gets the deductible information from Dentrix.

        Args:
            insurance_claim_id (int): The insurance claim ID that the deductible information will be fetched from.

        Returns:
            dict: The deductible information.
        """
        url = DentrixUrls.DEDUCTIBLES_MET_URL(insurance_claim_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def get_adjustments(self, claim_id: int) -> dict:
        """Gets the adjustment information from Dentrix.

        Args:
            claim_id (int): The claim ID that the adjustment information will be fetched from.

        Returns:
            dict: The adjustment information.
        """
        url = DentrixUrls.ADJUSTMENTS_URL(claim_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_patient_balance(self, patient_id: int) -> dict:
        """Gets the patient balance information from Dentrix.

        Args:
            patient_id (int): The patient ID that the balance information will be fetched from.

        Returns:
            dict: The balance information.
        """
        url = DentrixUrls.PATIENT_BALANCE_URL(patient_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def generate_clinical_note(self, patient_id: str, text: str, date: float, provider_id: int) -> list:
        """Generates a clinical note for a patient.

        Args:
            patient_id (str): The patient ID that the clinical note will be generated for.
            text (str): The text that will be used in the clinical note.
            date (float): The date that the clinical note will be dated as.
            provider_id (int): The provider ID that will be associated with the clinical note.

        Returns:
            list: The response from the clinical note generation.
        """
        url = DentrixUrls.GENERATE_CLINICAL_NOTES_URL(patient_id)
        payload = {
            "text": text,
            "provider": {"id": provider_id},
            "primaryProvider": {"id": provider_id},
            "assignedTeeth": [],
            "addendums": [],
            "datedAs": date,
            "isDraft": False,
            "reviewed": False,
            "password": "",
        }
        response = self.session.post(url, headers=self._headers(content_type=""), json=payload, timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def get_claims_notes(self, patient_id: str) -> list:
        """Gets the claims notes information from Dentrix.

        Args:
            patient_id (str): The patient ID that the claims notes information will be fetched from.

        Returns:
            list: The claims notes information.
        """
        url = DentrixUrls.CLAIM_NOTES_URL(patient_id)
        response = self.session.get(url, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def get_clinical_notes(self, patient_id: int) -> dict:
        """Gets the clinical notes information from Dentrix.

        Args:
            patient_id (int): The patient ID that the clinical notes information will be fetched from.

        Returns:
            dict: The clinical note's information.
        """
        url = DentrixUrls.CLINICAL_NOTES_URL(patient_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def get_clinical_note_info(self, patient_id: str, note_id: int) -> list:
        """Gets the clinical note information from Dentrix."""
        url = DentrixUrls.CLINICAL_NOTE_INFO_URL(patient_id, note_id)
        response = self.session.get(url, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def get_exams_for_claim(self, patient_id: str) -> list:
        """Gets the exams for claim information from Dentrix.

        Args:
            patient_id (str): The patient ID that the exams for claim information will be fetched from.

        Returns:
            list: The exams for claim information.
        """
        url = DentrixUrls.EXAMS_FOR_CLAIM_URL(patient_id)
        response = self.session.get(url, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_xray_exams(self, patient_id: str) -> list:
        """Gets the X-ray exams from Dentrix.

        Args:
            patient_id (str): The patient ID that the X-ray exams will be fetched from.

        Returns:
            list: The X-ray exam's information.
        """
        payload = {"patientId": patient_id}
        response = self.session.post(DentrixUrls.GET_XRAY_EXAMS_URL, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()["d"]

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_xray_images(self, exam_id: int) -> list:
        """Gets the X-ray images from Dentrix.

        Args:
            exam_id (int): The exam ID that the X-ray images will be fetched from.

        Returns:
            list: The X-ray images information.
        """
        payload = {"examId": exam_id}
        response = self.session.post(DentrixUrls.GET_XRAY_IMAGES_URL, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()["d"]

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def get_image_size_from_url(self, image_url: str) -> float:
        """Get image size from URL.

        Args:
            image_url (str): URL of the image

        Returns:
            float: Size of the image in bytes
        """
        headers = {
            "accept-encoding": "gzip, deflate, br, zstd",
            "Referer": DentrixUrls.BASE_URL,
        }
        response = self.session.get(image_url, headers=self._headers(content_type="", add_headers=headers), timeout=300)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        return float(response.headers["Content-Length"])

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def get_claim_state_text(self, claim_state: str) -> str:
        """Get claim state text.

        Args:
            claim_state (str): The claim states that the text will be fetched from.

        Returns:
            str: The claim state text.
        """
        index = self._get_index()
        return index[f"com.henryschein.onlinepm.ClaimState.{claim_state}.text"]

    @dentrix_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _search_patient(self, patient_name: str, params: dict | None = None) -> list:
        """Searches for a patient in Dentrix."""
        if not params:
            params = {"term": patient_name, "startFrom": 0, "showInactive": False}
        response = self.session.get(DentrixUrls.PATIENT_SEARCH_URL, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def create_patient_plan(self, patient_id: str | int, payload: dict) -> dict:
        """Create a plan attached with a patient.

        Args:
            patient_id (str): The patient ID that the new plan will be attached to.
            payload (dict): The payload that contains the new plan information to be created.

        Returns:
            dict: The response from the new plan creation.
        """
        url = DentrixUrls.PATIENT_INSURANCE_PLANS_URL.format(patient_id)
        response = self.session.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def _get_patient_insurance_plans(self, patient_id: int) -> list:
        """Get plan benefit table from Dentrix.

        Args:
            patient_id (str): The patient ID that the plan benefit table will be fetched from.

        Returns:
            list: The patient's plan benefit table.
        """
        url = DentrixUrls.PATIENT_INSURANCE_PLANS_URL.format(patient_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def _update_patient_plan_benefits(self, patient_id: int, payload: dict) -> dict:
        """Makes a request to update a whole Patient Plan with purpose of updating benefit section of plan's payload."""
        url = f"{DentrixUrls.PATIENT_INSURANCE_PLANS_URL(patient_id)}/{payload['id']}"
        response = self.session.put(url=url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _set_plan_eligibility_flag(self, payload: dict) -> dict:
        """Set the plan eligibility flag in Dentrix.

        Args:
            payload (dict): The payload that contains the updated plan eligibility flag information.

        Returns:
            dict: The response from the plan eligibility flag update.
        """
        response = self.session.post(
            DentrixUrls.SET_ELIGIBILITY_URL,
            headers=self._headers(content_type="application/x-www-form-urlencoded; charset=UTF-8"),
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def query_aged_receivables(self, payload: dict) -> dict:
        """Query the Aged Receivables Report for a specific location.

        Args:
            payload (dict): payload for aged receivables patients list

        Returns:
            dict: aged receivables information
        """
        response = self.session.post(
            url=DentrixUrls.AGED_RECEIVABLES,
            headers=self._headers(),
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_apply_credits(self, view_mode: str, patient_id: str) -> None:
        """Apply unapplied credits for a patient.

        Args:
            view_mode (str): view mode ('PATIENT_VIEW' or 'GUARANTOR_VIEW')
            patient_id (str): patient backend id

        Returns:
            dict: _description_
        """
        url = DentrixUrls.APPLY_CREDITS(patient_id)

        params = {"view": view_mode}
        response = self.session.get(url, params=params, headers=self._headers(), timeout=300)
        response.raise_for_status()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _query_billing_statements(self) -> dict:
        """Querying billing statements.

        Returns:
            dict: Available billing statements.
        """
        response = self.session.get(DentrixUrls.BILLING_STATEMENT, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_unlock_time(self) -> dict:
        """Get the unlock time from Dentrix."""
        response = self.session.get(DentrixUrls.UNLOCK_TIME_URL, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_public_key(self) -> dict:
        """Get the public key from Dentrix."""
        response = self.session.get(DentrixUrls.PUBLIC_KEY_URL, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _encrypt_password(self) -> str:
        """Method to Encrypt the password for unlocking the ledger."""
        pub_key = self._get_public_key()
        unlock_time = self._get_unlock_time()["time"]
        salted_password = f"{unlock_time}:{self.password}"
        return encrypt_with_rsa(salted_password, pub_key)

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _unlock_ledger_for_modification(self, payload: dict) -> dict:
        response = self.session.post(DentrixUrls.UNLOCK_LEDGER_URL, json=payload, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_transaction_payload(self, transaction_id: str) -> dict:
        """Method to request basic current payload structure of a transaction."""
        url = DentrixUrls.TRANSACTION_PAYMENT_URL(transaction_id)
        response = self.session.get(url, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_transaction_charges(self, params: dict, transaction_type: str) -> dict:
        """Get all charges for a specific Transaction in the ledger given the id."""
        url = DentrixUrls.TRANSACTION_CHARGES_URL(transaction_type)
        response = self.session.get(url, headers=self._headers(), params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _update_transaction(self, transaction_id: int, payload: dict, transaction_type: str) -> dict:
        """Update a transaction in Dentrix."""
        url = DentrixUrls.TRANSACTION_LEDGER_URL(transaction_type, transaction_id)
        response = self.session.put(url, json=payload, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _generate_statement_request(self, params: dict) -> dict:
        """Generate statements.

        Args:
            params (dict): Parameters containing billingStatement data.

        Returns:
            dict: The JSON response.
        """
        response = self.session.get(DentrixUrls.GENERATE_BILLING_STATEMENT, params=params, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _is_billing_statement_locked(self) -> dict:
        """Check if billing statement is locked.

        Returns:
            dict: The JSON response.
        """
        response = self.session.get(DentrixUrls.IS_BILLING_LOCKED, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def uncheck_all_patients(self) -> None:
        """Uncheck all patients related to current billing statement."""
        params = {"shouldPrint": False}
        response = self.session.put(DentrixUrls.BILLING_STATEMENT, params=params, headers=self._headers())
        response.raise_for_status()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def check_patient(self, patient_id: int) -> None:
        """Check patient related to billing statement."""
        payload = {"id": patient_id, "shouldPrint": True}
        response = self.session.get(
            DentrixUrls.PATIENTS_BILLING_STATEMENT(patient_id),
            headers=self._headers(),
            json=payload,
        )
        response.raise_for_status()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def query_patient_connection_statements(self, patient_id: int) -> dict:
        """Querying patient connection statements.

        :param patient_id: str

        :return: response_dict
        """
        payload = {"patientId": patient_id}
        response = self.session.get(
            DentrixUrls.QUERY_PATIENT_CONNECTION(patient_id),
            headers=self._headers(),
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def send_eStatement(self) -> dict:
        """Send eStatment to patient email."""
        params = {"shouldAddToPatientConnection": True, "shouldSendEStatement": True}
        response = self.session.get(DentrixUrls.SEND_E_STATEMENT, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def _post_appointment_note(self, payload: dict) -> dict:
        """Posts an appointment note to the Dentrix server.

        Args:
            payload (dict): The JSON payload containing the appointment and patient information.

        Raises:
            HTTPError: If the HTTP request to the Dentrix server fails.

        Returns:
            dict: The JSON response from the server after posting the appointment note.
        """
        response = self.session.post(
            url=DentrixUrls.APPOINTMENT_WITH_PATIENT_URL, json=payload, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def get_plan_info(self, plan_id: str) -> dict:
        """Get information about a carrier insurance plan.

        Args:
            plan_id (str): Unique identifier for the plan.

        Returns:
            dict: JSON response containing plan information.
        """
        url = DentrixUrls.CARRIER_INSURANCE_PLAN_URL(plan_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def update_plan_info(self, plan_id: int, payload: dict) -> dict:
        """Update carrier plan information.

        Args:
            plan_id (int): The unique identifier for the carrier plan.
            payload (dict): The payload containing the updated information for the carrier plan.

        Returns:
            dict: The JSON response containing the updated carrier plan information.
        """
        url = DentrixUrls.CARRIER_INSURANCE_PLAN_URL(plan_id)
        response = self.session.put(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def get_plan_coverage(self, plan_coverage_id: str | int) -> dict:
        """Retrieves plan coverage information for a patient based on plan coverage ID.

        Args:
            plan_coverage_id (str/int): The identifier for the plan coverage.

        Returns:
            dict: The JSON response containing the information of the plan coverage
        """
        url = DentrixUrls.CARRIER_PLAN_COVERAGE_URL(plan_coverage_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def update_plan_coverage(self, plan_coverage_id: int, payload: dict) -> dict:
        """Update carrier plan coverage.

        Args:
            plan_coverage_id (int): The unique identifier for the carrier plan.
            payload (dict): The payload containing the updated information for the carrier plan.

        Returns:
            dict: The JSON response containing the updated carrier plan information.
        """
        url = DentrixUrls.CARRIER_PLAN_COVERAGE_URL(plan_coverage_id)
        response = self.session.put(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def get_plan_subscriber_id(self, plan_subscriber_id: str | int) -> dict:
        """Search for the plan subscriber id.

        This method only makes sense if the patient is/has a dependent or an active plan.

        Args:
            plan_subscriber_id (str | int): plan subscriber id
        """
        url = DentrixUrls.SUBSCRIBER_INSURANCE_PLAN_URL(plan_subscriber_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def _get_document_list(self, patient_id: int) -> list:
        """Get a list of documents for a patient.

        Args:
            patient_id (int): The patient ID to get the documents for.

        Returns:
            list: A list of documents for the patient.
        """
        url = DentrixUrls.GET_DOCUMENTS_URL(patient_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def get_document_info(self, document_id: int) -> str:
        """Get information about a document.

        Args:
            document_id (int): The ID of the document to get information for.

        Returns:
            str: The document information as a string, HTML encoded.
        """
        url = DentrixUrls.DOCUMENT_INFO_URL(document_id)
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.content.decode("latin-1")

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def post_tag_to_document(self, document_id: int, tag: str) -> dict:
        """Add a tag to a document.

        Args:
            document_id (int): The ID of the document to add the tag to.
            tag (str): The tag to add to the document.

        Returns:
            dict: The response from adding the tag to the document.
        """
        url = DentrixUrls.ADD_TAG_TO_DOCUMENT_URL(document_id)
        response = self.session.post(url, headers=self._headers(), json={"tag": tag})
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def _get_all_payers(self) -> dict:
        """Get information about all insurance carriers.

        Returns:
            dict: JSON response containing information about all insurance carriers.
        """
        response = self.session.get(DentrixUrls.INSURANCE_CARRIERS_URL, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def get_fee_schedule_list(self) -> list[dict]:
        """Get list of fee schedules from Dentrix.

        Returns:
            list[dict]: JSON response containing a list of dicts containing the name and id of the fee schedules.
        """
        response = self.session.get(DentrixUrls.FEE_SCHEDULE_URL, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def get_fee_schedule_by_id(self, fee_schedule_id: str) -> dict:
        """Get fee schedule from Dentrix.

        Returns:
            dict: JSON response containing fee schedule.
        """
        url = DentrixUrls.FEE_SCHEDULE_URL + f"/{fee_schedule_id}"
        response = self.session.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=5, delay=1, backoff=2)
    def _get_procedure_codes(self) -> list:
        """Get procedure codes.

        Returns:
            list: JSON response containing procedure codes.
        """
        response = self.session.get(DentrixUrls.PRACTICE_PROCEDURE_URL, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_ledger_information_by_view(self, patient_id: str, params: dict) -> dict:
        """Get ledger information filtering by view mode.

        Args:
            patient_id (str): patient backend id
            params (dict): Filter by patientID and view mode.

        Returns:
            dict: Aging balance information
        """
        url = DentrixUrls.LEDGER_INFO(DentrixUrls.BASE_URL, patient_id)
        response = self.session.get(url, params=params, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_guarantor_related_patients(self, patient_id: str) -> list:
        """Method to get patients dependent to the guarantor's plan.

        Args:
            patient_id (str): patient backend id

        Returns:
            list: dicts of patients dependent to the guarantor's plan.
        """
        url = DentrixUrls.GET_GUARANTOR_RELATED_PATIENTS(DentrixUrls.BASE_URL, patient_id)
        response = self.session.get(url, headers=self._headers(), timeout=300)
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_patients_information(self, patient_ids: list[int]) -> list[dict]:
        """Get information about multiple patients.

        Args:
            patient_ids (list[int]): List of patient IDs to retrieve information for.

        Returns:
            list[dict]: List of dictionaries containing patient information.
        """
        response = self.session.post(
            DentrixUrls.PATIENTS_INFO_URL, headers=self._headers(), json={"patientIds": patient_ids}
        )
        response.raise_for_status()
        return response.json()

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _download_document(self, document_id: int, patient_id: int) -> bytes:
        """Download a document from DentrixAscend.

        Args:
            document_id (int): The ID of the document to download.
            patient_id (int): The ID of the patient associated with the document.

        Returns:
            bytes: The content of the downloaded document.
        """
        headers_to_add = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",  # noqa: E501
            "Accept-Encoding": "gzip, deflate, br",
        }
        params = {"documents": document_id, "patientId": patient_id}
        response = self.session.get(
            DentrixUrls.DOCUMENT_EXPORT_URL,
            headers=self._headers(content_type="", add_headers=headers_to_add),
            params=params,
        )
        response.raise_for_status()
        return response.content

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def update_appointment_data(self, body: dict) -> dict:
        """Updates the calendar appointment based on given body data.

        Args:
            body (dict): Appointment update data.

        Returns:
            dict: The response from the Dentrix server.
        """
        response = self.session.post(DentrixUrls.UPDATE_APPOINTMENT_URL, headers=self._headers(), json=body)
        response.raise_for_status()
        string_data = response.content.decode("utf-8")
        return json.loads(string_data)

    @dentrix_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_appointments_by_patient_id(self, patient_id: int) -> list[dict]:
        """Get appointments by patient ID.

        Args:
            patient_id (int): The ID of the patient.

        Returns:
            list[dict]: A list of appointments for the specified patient.
        """
        response = self.session.get(
            DentrixUrls.APPOINTMENT_REST_URL, params={"patientId": patient_id}, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
