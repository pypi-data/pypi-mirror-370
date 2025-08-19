"""Contains DentrixServiceRequests object."""

from requests.sessions import Session
from retry import retry

from t_dentrix_service.consts.urls.ascend_urls import AscendUrls
from t_dentrix_service.operations.decorators import ascend_request_handling


class AscendRequests:
    """Segment of the Dentrix Service solely responsible with handling requests."""

    def __init__(self) -> None:
        """Initialization for AscendRequests."""
        self.session = Session()

    @ascend_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_appointments(self) -> list[dict]:
        """Gets the location information from Dentrix."""
        response = self.session.get(AscendUrls.APPOINTMENTS)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def _get_appointments_by_id(self, appointment_id: int) -> list[dict]:
        """Gets the location information from Dentrix."""
        response = self.session.get(AscendUrls.APPOINTMENT_BY_ID(appointment_id))
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def get_aging_balance(self, payload: dict) -> dict:
        """Query aging balance patient info.

        Args:
            payload (dict): Query parameters for the request.

        Returns:
            dict: JSON response containing aging balance info.
        """
        response = self.session.get(url=AscendUrls.AGING_BALANCES, params=payload, timeout=300)
        response.raise_for_status()
        return response.json()

    @retry(tries=3, delay=2, backoff=2)
    def get_patient_insurance_plans(self, params: dict) -> list:
        """Returns a list of patient insurance plans based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            list: The list of patient insurance plans.
        """
        response = self.session.get(AscendUrls.PATIENT_INSURANCE_PLANS_URL, params=params)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=2, backoff=2)
    def get_patient_insurance_plan_by_id(self, patient_insurance_plan_id: int, params: dict) -> dict:
        """Returns a patient insurance plan by entry ID.

        Args:
            patient_insurance_plan_id (int): The ID of Patient Insurance Plan.
            params (dict): Filter criteria, including response fields.

        Returns:
            dict: The patient insurance plan information.
        """
        url = f"{AscendUrls.PATIENT_INSURANCE_PLANS_URL}/{patient_insurance_plan_id}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_audits(self, params: str) -> dict:
        """Returns list of audits based on a filter.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: json resulted
        """
        response = self.session.get(url=AscendUrls.AUDITS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_bulk_insurance_payments(self, params: str) -> dict:
        """Returns a list of bulk insurance payments based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: json resulted
        """
        response = self.session.get(url=AscendUrls.BULK_INSURANCE_PAYMENTS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_bulk_insurance_payments_by_id(self, bulk_payment_id: int) -> dict:
        """Returns a list of bulk insurance payments based on id.

        Args:
            bulk_payment_id (str): id of the bulk insurance payments

        Returns:
            dict: json resulted
        """
        response = self.session.get(url=AscendUrls.BULK_INSURANCE_PAYMENT_BY_ID(bulk_payment_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_carrier_insurance_plans(self, params: str) -> dict:
        """Returns a list of carrier insurance plans based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: json resulted
        """
        response = self.session.get(url=AscendUrls.CARRIER_INSURANCE_PLANS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_carrier_insurance_plan_by_id(self, carrier_id: int) -> dict:
        """Returns a carrier insurance plan by entry ID.

        Args:
            carrier_id (str): id of the carrier insurance plan

        Returns:
            dict: json resulted
        """
        response = self.session.get(url=AscendUrls.CARRIER_INSURANCE_PLAN_BY_ID(carrier_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_carrier_plan_copay_exceptions(self, params: dict) -> dict:
        """Returns a list of carrier plan copay exceptions based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: JSON result.
        """
        response = self.session.get(url=AscendUrls.CARRIER_PLAN_COPAY_EXCEPTIONS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_carrier_plan_copay_exception_by_id(self, exception_id: int) -> dict:
        """Returns a carrier plan copay exception by entry ID.

        Args:
            exception_id (int): ID of the carrier plan copay exception.

        Returns:
            dict: JSON result.
        """
        response = self.session.get(url=AscendUrls.CARRIER_PLAN_COPAY_EXCEPTION_BY_ID(exception_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_carrier_plan_coverage_exceptions(self, params: dict) -> dict:
        """Returns a list of carrier plan coverage exceptions based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: JSON result.
        """
        response = self.session.get(url=AscendUrls.CARRIER_PLAN_COVERAGE_EXCEPTIONS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_carrier_plan_coverage_exception_by_id(self, exception_id: int) -> dict:
        """Returns a carrier plan coverage exception by entry ID.

        Args:
            exception_id (int): ID of the carrier plan coverage exception.

        Returns:
            dict: JSON result.
        """
        response = self.session.get(url=AscendUrls.CARRIER_PLAN_COVERAGE_EXCEPTION_BY_ID(exception_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_clinical_notes(self, params: dict) -> dict:
        """Returns a list of clinical notes based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: JSON result.
        """
        response = self.session.get(url=AscendUrls.CLINICAL_NOTES, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_clinical_note_by_id(self, note_id: int) -> dict:
        """Returns a clinical note by entry ID.

        Args:
            note_id (int): ID of the clinical note.

        Returns:
            dict: JSON result.
        """
        response = self.session.get(url=AscendUrls.CLINICAL_NOTE_BY_ID(note_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_locations(self, params: dict) -> dict:
        """Returns a list of locations based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.LOCATIONS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_location_by_id(self, location_id: int) -> dict:
        """Returns a location by entry ID.

        Args:
            location_id (int): ID of the location

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.LOCATION_BY_ID(location_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_users(self, params: dict) -> dict:
        """Returns a list of users based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.USERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_user_by_id(self, user_id: int) -> dict:
        """Returns a user by entry ID.

        Args:
            user_id (int): ID of the user

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.USER_BY_ID(user_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_transactions(self, params: dict) -> dict:
        """Returns a list of transactions based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.TRANSACTIONS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_transaction_by_id(self, transaction_id: int) -> dict:
        """Returns a transaction by entry ID.

        Args:
            transaction_id (int): ID of the transaction

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.TRANSACTION_BY_ID(transaction_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_visits(self, params: dict) -> dict:
        """Returns a list of visits based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.VISITS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_visit_by_id(self, visit_id: int) -> dict:
        """Returns a visit by entry ID.

        Args:
            visit_id (int): ID of the visit

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.VISIT_BY_ID(visit_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_timeclocks(self, params: dict) -> dict:
        """Returns a list of timeclocks based on filter criteria.

        Args:
            params (dict): Filter criteria.

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.TIMECLOCKS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_timeclock_by_id(self, timeclock_id: int) -> dict:
        """Returns a timeclock by entry ID.

        Args:
            timeclock_id (int): ID of the timeclock

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.TIMECLOCK_BY_ID(timeclock_id), timeout=300)
        response.raise_for_status()
        return response.json()

    @ascend_request_handling
    @retry(tries=3, delay=1, backoff=2)
    def _get_usage_report(self) -> dict:
        """Returns the usage report.

        Returns:
            dict: JSON response
        """
        response = self.session.get(url=AscendUrls.USAGE_REPORT, timeout=300)
        response.raise_for_status()
        return response.json()
