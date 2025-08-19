"""Main module."""

import re
import time
from contextlib import suppress
from requests.exceptions import HTTPError
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from time import sleep, time  # noqa
from typing import Literal

from retry import retry
from numpy import busday_offset
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.remote.webelement import WebElement
from SeleniumLibrary.errors import ElementNotFound

from t_dentrix_service.consts.locators import Locators
from t_dentrix_service.consts.urls.dentrix_urls import DentrixUrls
from t_dentrix_service.exceptions import (
    BillingStatementsOpenError,
    DentrixLocationIdNotFound,
    DocumentIsEmptyException,
    DocumentNotSupportedException,
    FailedToUploadDocumentError,
    LocationNameNotFoundError,
    NoBillingStatementsInfoError,
    NoLedgerBalanceError,
    NoResultsError,
    PatientNotFoundError,
)
from t_dentrix_service.models.dtos.aged_receivables import AgedReceivable
from t_dentrix_service.models.activity_status import Status
from t_dentrix_service.models.attachment_types import AttachmentTypes
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
from t_dentrix_service.models.dtos.schedules import Schedule, Appointment
from t_dentrix_service.models.dtos.transaction import Transaction
from t_dentrix_service.models.dtos.xray import XrayExam, XrayImage
from t_dentrix_service.models.eligibility_flag import EligibilityFlag
from t_dentrix_service.operations.decorators import custom_selenium_retry
from t_dentrix_service.operations.dentrix_requests import DentrixServiceRequests
from t_dentrix_service.utils import clean_name
from t_dentrix_service.utils.converters import convert_date_to_timestamp
from t_dentrix_service.utils.date import get_equivalent_utc_time_of_midnights_date, now, now_timestamp, today
from t_dentrix_service.utils.logger import logger
from t_dentrix_service.utils.timer import Timer


class DentrixService(DentrixServiceRequests):
    """Main object that contains logic for Dentrix Service."""

    @custom_selenium_retry()
    def click_element_and_retry(self, locator: WebElement | str) -> None:
        """Click the element and retry."""
        self.browser.set_focus_to_element(locator)
        self.browser.click_element_when_visible(locator)

    @custom_selenium_retry(tries=3, delay=2)
    def does_page_contain_this_element(self, selector: WebElement | str, timeout: int | float = 5) -> bool:
        """Check if the page contains the element."""
        with suppress(AssertionError):
            self.browser.wait_until_element_is_visible(selector, timeout=timeout)
            return True
        return False

    @custom_selenium_retry()
    def get_attribute_value_and_retry(self, locator: WebElement | str, attribute: str = "value") -> str:
        """Get attribute value and retry."""
        return self.browser.get_element_attribute(locator, attribute=attribute)

    @custom_selenium_retry()
    def input_text_and_retry(self, locator: WebElement | str, text: str) -> None:
        """Input text and retry."""
        return self.browser.input_text(locator, text)

    def __wait_until_element_attribute_changed(
        self,
        locator: WebElement | str,
        attribute: str,
        value: str,
        timeout: int = 10,
    ) -> bool:
        """Function for waiting until the element attribute is changed."""
        timer = Timer(timeout)
        while timer.not_expired:
            current_value = str(self.get_attribute_value_and_retry(locator, attribute))
            if re.sub(r"\s", "", current_value) == re.sub(r"\s", "", value):
                return True
        msg = f"Attribute {attribute} is not changed to desired value after {timeout} seconds"
        raise AssertionError(msg)

    @custom_selenium_retry()
    def input_text_and_check(
        self,
        locator: WebElement | str,
        text: str,
        sleep_time: int = 1,
        timeout: int = 5,
    ) -> None:
        """Function for input text and check."""
        self.browser.clear_element_text(locator)
        self.click_element_and_retry(locator)
        self.input_text_and_retry(locator, text)
        sleep(sleep_time)
        self.__wait_until_element_attribute_changed(locator, "value", text, timeout=timeout)

    def _did_element_disappear_from_page(self, locator: WebElement | str, timeout: int | float = 5) -> bool:
        """Waits until a given element is not present on the page anymore."""
        try:
            self.browser.wait_until_page_does_not_contain_element(locator, timeout)
        except AssertionError:
            return False
        else:
            return True

    @custom_selenium_retry()
    def _scroll_to_item(self, element: str) -> None:
        self.browser.execute_javascript(f'document.querySelector("{element}").scrollIntoView({{"block": "center"}});')

    @retry(exceptions=HTTPError, tries=3, delay=2, backoff=2)
    def change_location(self, location_id: int | str, *, by_name: bool = False) -> dict:
        """Changes current dentrix location.

        Args:
            location_id (int | str): identifier of the specified location, can be a literal id or the locations name.
            by_name (bool, optional): determines if the identifier given is the name of the location. Defaults to False.

        Returns:
            dict: The response from the Dentrix API after changing the location.

        Raises:
            LocationNameNotFoundError: raised if the name given was not found among the dentrix locations.
        """
        location_name = None
        if by_name:
            location_name = location_id
            location_id = self.get_location_id_by_name(location_name)
            if location_id is None:
                raise LocationNameNotFoundError

        try:
            return self._change_location(location_id)
        except HTTPError as e:
            if e.response.status_code == 500:
                name_message = f"and name {location_name} " if location_name is not None else ""
                msg = f"Dentrix Location of id {location_id} {name_message}not found, please review."
                raise DentrixLocationIdNotFound(
                    msg,
                )
            raise e

    def get_location_id_by_name(self, location_name: str) -> int | None:
        """Gather id of a certain location by it's name.

        Args:
            location_name (str): The name of the location that should be searched.

        Returns:
            int | None: returns int relating to the id of the location, returns None if it fails to find a location.
        """
        locations_info = self._get_locations_info()
        for location_info in locations_info:
            if location_name.lower() in location_info["name"].lower():
                logger.info(f"Found location of approximate name: {location_info['name']}")
                return location_info["id"]

        return None

    def update_chart_number(self, patient_information: dict, chart_number: str) -> dict:
        """Updates the chart number of a patient.

        Args:
            patient_information (dict): The patient information to be updated.
            chart_number (str): The new chart number.

        Returns:
            dict: The updated patient information.
        """
        logger.info(f"Updating chart number: {chart_number} for patient id: {patient_information['id']}")
        payload = patient_information
        payload.update({"chartNumber": chart_number})
        return self._update_patient_info(payload)

    def get_unattached_procedures(self) -> list[UnattachedProcedure]:
        """Get unattached procedures as objects."""
        params = {"goalType": "UNATTACHED_PROCEDURE"}
        raw_data = self._get_problem_data(params)

        return [UnattachedProcedure.from_payload(item) for item in raw_data if item.get("metadata")]

    def get_unsent_claims(self) -> dict:
        """Get unsent claims."""
        params = {"goalType": "UNSENT_CLAIMS"}
        patient_list = [UnattachedProcedureMetadata.from_payload(patient) for patient in self._get_problem_data(params)]
        return patient_list

    def get_overdue_claim_info(self, claim_id: int) -> dict:
        """Getting specific overdue Claim info.

        Args:
            claim_id (int): The claim id to be searched for.

        Returns:
            dict: The claim information.
        """
        params = {
            "goalType": "OVERDUE_CLAIMS",
            "claimId": claim_id,
        }
        return self._get_problem_data(params)[0]

    def get_patient_procedures(self, entity_id: str, date_of_service: str, entity_type: str) -> dict:
        """Gets the patient procedures from Dentrix.

        Args:
            entity_id (str): The entity id.
            date_of_service (str): The date of service.
            entity_type (str): The entity type.

        Returns:
            dict: The patient procedures.
        """
        params = {"problemType": "UNATTACHED_PROCEDURE"}
        return self._get_solution_data(params, entity_id, entity_type, date_of_service)[0]

    def get_patient_unsent_claim(self, entity_id: str, entity_type: str, date_of_service: str) -> dict:
        """Gets the patient unsent claim from Dentrix.

        Args:
            entity_id (str): The entity id.
            entity_type (str): The entity type.
            date_of_service (str): The date of service.

        Returns:
            dict: The patient unsent claim.
        """
        params = {"problemType": "UNSENT_CLAIM"}
        return self._get_solution_data(params, entity_id, entity_type, date_of_service)[0]

    def close_dialogue(
        self,
        alert_texts: list[str] | None = None,
        close_buttons: list[str] | None = None,
    ) -> None:
        """Closes the dialogue.

        Args:
            alert_texts (list[str], optional): List of alert texts to check and close. Defaults to None.
            close_buttons (list[str], optional): List of locators for close buttons. Defaults to None.
        """
        alert_texts = alert_texts or [
            Locators.Ledger.MEDICAL_ALERT_TEXT,
            Locators.Ledger.PROCEDURES_POSTED_TEXT,
        ]
        close_buttons = close_buttons or [
            Locators.Documents.CLOSE_BUTTON,
            Locators.Ledger.CLOSE_COVERAGE_GAP_ALERT,
        ]

        for alert_text, close_button in zip(alert_texts, close_buttons):
            if self.browser.does_page_contain(alert_text):
                self.click_element_and_retry(close_button)
                self.browser.wait_until_page_does_not_contain_element(alert_text, timeout=1)

        if self.does_page_contain_this_element(Locators.Documents.DIALOGUE_ALERT):
            self.click_element_and_retry(Locators.Documents.DIALOGUE_ALERT)

    def open_claim_window(self, patient_id: int, locator: str) -> None:
        """Opens the claim window.

        Args:
            patient_id (int): The patient id.
            locator (str): The locator for the claim.
        """
        self.browser.go_to(DentrixUrls.LEDGER_URL(patient_id))
        self.close_dialogue()
        self.browser.wait_until_element_is_visible(locator)
        claim = self.browser.find_element(locator)
        claim.click()
        self.browser.wait_until_element_is_visible(Locators.Ledger.ATTACHMENTS_TAB)

    @custom_selenium_retry()
    def gather_claim_imaging_cookies(self, patient_id: int | str, claim_locator: str) -> None:
        """Go to the claim and gather imaging cookies.

        Args:
            patient_id (int | str): The patient id.
            claim_locator (str): The claim locator.
        """
        self.open_claim_window(patient_id, claim_locator)
        self.browser.click_element(Locators.Ledger.ATTACHMENTS_TAB)
        self.browser.wait_until_page_contains_element(Locators.Ledger.ADD_IMAGES, timeout=10)
        self.browser.click_element(Locators.Ledger.ADD_IMAGES)
        self.browser.wait_until_page_contains_element(Locators.Ledger.ATTACH_IMAGES)
        sleep(5)
        self._set_cookies()

    def add_attachment_to_claim(self, claim_id: int, attachment_type: AttachmentTypes, attachments: list) -> None:
        """Add attachments to the claim.

        Args:
            claim_id (int): The claim id to add attachments to.
            attachment_type (AttachmentTypes): The attachment type.
            attachments (list[str]): The attachments to add.
        """
        insurance_claim = self._get_insurance_claim(claim_id)
        if attachment_type == AttachmentTypes.XRAY:
            insurance_claim["imageAttachments"].extend(attachments)
        else:
            insurance_claim["claimAttachments"].extend(attachments)

        self._update_claim(claim_id, insurance_claim)

    def update_claim(
        self,
        claim_id: int,
        payload: dict | None = None,
        field_to_update: dict | None = None,
    ) -> dict:
        """Updates the claim with the given field.

        Args:
            claim_id (int): The claim id to be updated.
            payload (dict): The payload to be updated, if None, it will be fetched from the claim.
            field_to_update (dict): The field to be updated.

        Returns:
            dict: The updated claim information.
        """
        if payload is None and field_to_update:
            payload = self._get_insurance_claim(claim_id)

        payload.update(field_to_update)
        return self._update_claim(claim_id, payload)

    def get_schedules(self, schedule_date: date, is_week_view: bool = True) -> Schedule:
        """Retrieves schedules for a given date from the defined base URL."""
        timestamp = convert_date_to_timestamp(schedule_date)
        is_today = schedule_date == now().date()
        current_location = self._get_current_location()
        params = {
            "dates": timestamp,
            "isWeekView": is_week_view,
            "locationIds": current_location["id"],
            "isForToday": is_today,
        }
        raw_payload = self._get_schedules(params)
        return Schedule.from_payload(raw_payload)

    def patient_has_schedules(self, patient_id: int, days: int = 3) -> bool:
        """Checks if Patient has schedules from the last given number of days.

        Args:
            patient_id (int): id from the dentrix patient.
            days (int): number of days to check.

        Returns:
            bool: boolean value related to patient having schedules from last 2 days
        """
        for day in range(0, days + 1):
            # This logic calculates today - days, considering only business days, but it returns datetime64
            schedule_datetime64 = busday_offset(now().date(), -day, roll="backward")
            # Here we convert datetime64 to datetime by turning it into a timestamp measured in seconds
            schedule_datetime = datetime.fromtimestamp(schedule_datetime64.astype("M8[s]").astype(int), tz=timezone.utc)
            schedules = self.get_schedules(schedule_datetime)
            for appointment in schedules["appointments"]:
                if appointment["patient"]["id"] == patient_id:
                    return True
        return False

    @retry(tries=3, delay=1, backoff=2)
    def upload_document(self, file_path: Path | str, patient_id: int) -> None:
        """Uploads a document to the patients document manager.

        Args:
            file_path (Path | str): The path to the file to be uploaded.
            patient_id (int): Patient ID.
        """
        file_path: Path = Path(file_path).absolute()

        if not self.is_browser_open():
            self.login_to_dentrix()
        self.browser.go_to(DentrixUrls.PATIENT_DOCUMENTS_URL(patient_id))
        self.browser.wait_until_element_is_visible(Locators.Documents.SHADOW_ROOT_PARENT, timeout=60)
        shadow_root: ShadowRoot = self.browser.get_webelement(Locators.Documents.SHADOW_ROOT_PARENT).shadow_root

        try:
            shadow_root.find_element(By.CSS_SELECTOR, Locators.Documents.UPLOAD_BUTTON).click()
        except ElementClickInterceptedException:
            sleep(10)
            self._click_element_if_exists(Locators.Documents.CLOSE_BUTTON)
            self._click_element_if_exists(Locators.Documents.DIALOGUE_ALERT)
            shadow_root.find_element(By.CSS_SELECTOR, Locators.Documents.UPLOAD_BUTTON).click()
        upload_shadow_root: ShadowRoot = self.browser.get_webelement(Locators.Documents.UPLOAD_SHADOW_ROOT).shadow_root
        drag_and_drop: WebElement = upload_shadow_root.find_element(By.CSS_SELECTOR, Locators.Documents.UPLOAD_INPUT)
        sleep(5)

        drag_and_drop.send_keys(str(file_path))
        self.browser.driver.execute_script("arguments[0].value = '';", drag_and_drop)

        sleep(2)
        if not self.browser.driver.execute_script(Locators.Documents.UPLOAD_SCRIPT):
            msg = "Upload Script failed."
            raise FailedToUploadDocumentError(msg)

        with suppress(NoSuchElementException):
            upload_message_element: WebElement = upload_shadow_root.find_element(
                By.CSS_SELECTOR,
                Locators.Documents.UPLOAD_MESSAGE,
            )
            if upload_message_element.text == "Upload Failed.":
                sub_message = upload_message_element.find_element(By.XPATH, "..").text
                if "Not a supported file type" in sub_message:
                    msg = "Document is not of a supported type."
                    raise DocumentNotSupportedException(msg)
                elif "File is empty" in sub_message:
                    msg = "Document has no contents, please review."
                    raise DocumentIsEmptyException(msg)
                else:
                    msg = f"Received failure message with sub message '{sub_message}'."
                    raise FailedToUploadDocumentError(msg)

        logger.info("Document uploaded successfully.")

    def search_patient(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: date | None = None,
        activity_status: Literal["New", "Non Patient", "Active"] | Status | None = None,
        *,
        strict_search: bool = False,
    ) -> list[Patient] | Patient:
        """Search for a patient in Dentrix.

        Args:
            first_name (str): Patient's first name.
            last_name (str): Patient's last name.
            date_of_birth (date | None): Date of birth of the patient that is being searched.
            activity_status (Literal["New", "Non Patient", "Active"] | Status | None): Status of the patient.
            activity_status (bool): Status of the patient.
            strict_search (bool): If True, only one patient will be returned.
            If False, a list of patients will be returned.

        Raises:
            NoResultsError: Raised when no results are found in the beginning of the process.
            PatientNotFoundError: Raised when not found an exact patient on a strict search

        Returns:
            list[Patient] | Patient: Results of either single patient (with strict search) or list of patients filtered
            by given data.
        """
        full_name = f"{first_name} {last_name}"
        logger.info(f"Searching for patient {full_name} in Dentrix.")
        patients = self._search_patient(full_name)
        if not patients:
            msg = "No patient could be found with this name in Ascend."
            raise NoResultsError(msg)

        results = self._filter_patients_by_name(patients, first_name, last_name)

        if date_of_birth is not None:
            dob_timestamp = convert_date_to_timestamp(date_of_birth)
            results = self._filter_patients_by_date_of_birth(results, dob_timestamp)

        if activity_status is not None:
            results = self._filter_patients_by_active_status(results, activity_status)

        if strict_search:
            if len(results) == 1:
                return Patient.from_payload(results[0])
            else:
                msg = "A patient with theses specifications was not found"
                raise PatientNotFoundError(msg)
        else:
            return [Patient.from_payload(result) for result in results]

    def search_patient_by_chart_number(self, chart_number: str) -> Patient:
        """Search for a patient in Dentrix by chart number.

        Args:
            chart_number (str): Chart number of the patient that is being searched.

        Raises:
            NoResultsError: Raised when no results are found for the given chart number.
        Returns:
            Patient: Object with the found patient information.
        """
        patients = self._search_patient(chart_number)
        if not patients:
            msg = "No patient could be found with this chart number in Ascend."
            raise NoResultsError(msg)
        patient = next((patient for patient in patients if patient["chartNumber"] == chart_number), None)
        if not patient:
            msg = f"No patient found with chart number {chart_number}."
            raise PatientNotFoundError(msg)
        return Patient.from_payload(patient)

    def _filter_patients_by_name(
        self,
        patients: list,
        first_name: str,
        last_name: str,
    ) -> list:
        """Filter patients by first and last name."""
        return [
            patient
            for patient in patients
            if (
                clean_name(patient["firstName"]) == clean_name(first_name)
                or clean_name(patient["preferredName"]) == clean_name(first_name)
            )
            and (clean_name(patient["lastName"]) == clean_name(last_name))
        ]

    @staticmethod
    def _filter_patients_by_date_of_birth(patients: list, timestamp: int) -> list:
        """Filter patient or patients with a given date of birth."""
        return [patient for patient in patients if patient["dateOfBirth"] == timestamp]

    @staticmethod
    def _filter_patients_by_active_status(patients: list, activity_status: str) -> list:
        """Filter patient or patients with a given date of birth."""
        return [patient for patient in patients if patient["status"] == activity_status]

    def get_current_location(self) -> Location:
        """Method to get the current active location on the dentrix site."""
        return Location.from_payload(self._get_current_location())

    def get_locations(self) -> list[Location]:
        """Get all Dentrix locations."""
        return [Location.from_payload(location_info) for location_info in self._get_locations_info()]

    def get_plan_benefit(self, patient_id: int, plan_coverage_id: str) -> dict:
        """Extracts the plan benefit table for a patient.

        Args:
            patient_id (int): The patient ID that the plan benefit table will be fetched from.
            plan_coverage_id (str): The plan coverage ID that the plan benefit table will be fetched from.

        Returns:
            dict: The plan benefit table for the patient.
        """
        payload_list = self._get_patient_insurance_plans(patient_id)

        for payload in payload_list:
            if (
                payload["subscriberInsurancePlan"]["carrierInsurancePlan"]["inNetworkCoverage"]["id"]
                == plan_coverage_id
            ):
                return payload
        return {}

    def update_plan_benefit(
        self,
        patient_id: int,
        payload: dict | None = None,
        plan_coverage_id: str | None = None,
        field_to_update: dict | None = None,
    ) -> dict:
        """Updates the plan benefit table for a patient.

        Args:
            patient_id (int): The patient ID.
            payload (dict, optional): The payload to update the plan benefit table.
            plan_coverage_id (str, optional): The plan coverage ID.
            field_to_update (dict, optional): The field to update in the plan benefit table.

        Returns:
            dict: The updated plan benefit table.
        """
        if payload is None and plan_coverage_id and field_to_update:
            payload = self.get_plan_benefit(patient_id, plan_coverage_id)
            payload.update(field_to_update)
        return self._update_patient_plan_benefits(patient_id, payload)

    def update_plan_end_date(
        self,
        patient_id: int,
        plan_coverage_id: str,
        payload: dict | None,
        date_epoch: int | None = int(time()) * 1000,
    ) -> dict:
        """Updates the end date of a plan.

        Args:
            patient_id (int): The patient ID.
            plan_coverage_id (str): The plan coverage ID.
            payload (dict, optional): The payload to update the plan benefit table.
            date_epoch (int, optional): The date to update in the plan benefit table.

        Returns:
            dict: The updated plan benefit table.
        """
        if payload is None and plan_coverage_id:
            payload = self.get_plan_benefit(patient_id, plan_coverage_id)
        payload["responsibilities"][0]["endDate"] = date_epoch
        return self._update_patient_plan_benefits(patient_id, payload)

    def update_patient_eligibility_flag(
        self,
        patient_id: int | None,
        patient_list: list[int] | None,
        eligibility_flag: EligibilityFlag,
    ) -> dict:
        """Updates the eligibility flag for a patient.

        Args:
            patient_id (int): The patient ID.
            patient_list (list[int]): The list of patient IDs.
            eligibility_flag (EligibilityFlag): The eligibility flag.

        Returns:
            dict: The updated patient information.
        """
        if patient_id:
            patient_list = [patient_id]
        payload = {"patientList": patient_list, "eligibilityStatus": eligibility_flag}
        return self._set_plan_eligibility_flag(payload)

    def identify_plan_members(self, patient_id: int, plan_coverage_id: str) -> list:
        """Returns the ids of all dependents under that plan.

        Args:
            patient_id (int): The patient ID.
            plan_coverage_id (str): The plan coverage ID.

        Returns:
            list: The list of dependent ids.
        """
        payload = self._get_patient_insurance_plans(patient_id)
        return [
            dependent["id"]
            for plan in payload
            if plan["subscriberInsurancePlan"]["carrierInsurancePlan"]["id"] == plan_coverage_id
            for dependent in plan["subscriberInsurancePlan"]["dependentPatients"]
        ]

    def query_aged_receivables_patients_list(self, payload: dict) -> list[AgedReceivable]:
        """Get aged receivables patients list as AgedReceivable objects."""
        logger.info("Getting aged receivables patients list")
        payload["asOfDate"] = now_timestamp()
        response = self.query_aged_receivables(payload=payload)

        receivables = response.get("receivables")
        if not receivables or not isinstance(receivables, dict):
            logger.warning("Receivables is missing or invalid in response")
            return []

        aged_list = receivables.get("agedReceivables", [])
        return [AgedReceivable.from_payload(ar) for ar in aged_list]

    def apply_credits_for_guarantor(self, patient_id: str) -> None:
        """Allocate applied credits for a guarantor.

        Args:
            patient_id (str): patient backend object
        """
        logger.info("Allocating applied credits for patient in GUARANTOR_VIEW mode")
        self._get_apply_credits("GUARANTOR_VIEW", patient_id)

    def apply_credits_for_patient(self, patient_id: str) -> None:
        """Allocate applied credits for a patient.

        Args:
            patient_id (str): patient backend object.
        """
        logger.info("Allocating applied credits for patient in PATIENT_VIEW mode")
        self._get_apply_credits("PATIENT_VIEW", patient_id)

    @staticmethod
    def _adjust_date_for_billing_request(date_to_be_converted: date) -> int:
        """Returns the timestamp for an utc datetime midnight time."""
        return convert_date_to_timestamp(get_equivalent_utc_time_of_midnights_date(date_to_be_converted))

    def generate_statement(
        self,
        billing_statement: BillingStatement,
        not_billed_since: date,
        date_from: date,
    ) -> dict:
        """Logic for a generating statement within dentrix.

        Args:
            billing_statement (BillingStatement): Billing Statement containing information to be used in generation.
            not_billed_since (date): Only generate a statement if not billed since this date
            date_from (date): to be used in the "dateFrom" key

        Returns:
            dict: statement generation JSON response.
        """
        # THIS METHOD CANNOT BE AND WAS NOT SAFELY TESTED
        # Please remove this comment if this logic was executed and worked as intended.
        date_from_timestamp = self._adjust_date_for_billing_request(date_from)
        todays_timestamp = self._adjust_date_for_billing_request(today())
        not_billed_since_timestamp = self._adjust_date_for_billing_request(not_billed_since)
        due_date_timestamp = (
            self._adjust_date_for_billing_request(billing_statement.due_date) if billing_statement.due_date else None
        )
        params = {
            "paymentPlanRequirement": "WITH_OR_WITHOUT_PAYMENT_PLAN",
            "notBilledSinceDate": not_billed_since_timestamp,
            "pendingCharges": True,
            "minimumBalance": billing_statement.minimum_balance,
            "showCC": billing_statement.show_creditcard_info,
            "showAbbreviation": billing_statement.show_abreviation,
            "message": billing_statement.message,
            "dueDate": due_date_timestamp,
            "lastNameFrom": "",
            "lastNameTo": "",
            "dateFrom": date_from_timestamp,
            "range": "ZERO_BALANCE_DATE_RANGE",
            "today": todays_timestamp,
            "billingTypes": ["8000000000261", "8000000000887", "8000000001513", "8000000002139"],
        }
        return self._generate_statement_request(params)

    def query_billing_statements(self) -> BillingStatement:
        """Gather billing statements information.

        Returns:
            BillingStatement: Billing Statement object for easy data transfering.
        """
        billing_statement_info = self._query_billing_statements()
        if billing_statement_info:
            return BillingStatement.from_payload(billing_statement_info)
        else:
            msg = "No Billing Statement Info found on Dentrix"
            raise NoBillingStatementsInfoError(msg)

    def unlock_ledger_for_modification(self, transaction_id: int, time: str | None = "FIFTEEN_MINUTES") -> dict:
        """Unlock ledger for modification.

        Args:
            transaction_id (int): The transaction id.
            time (str, optional): The time. Defaults to "FIFTEEN_MINUTES".

        Returns:
            dict: JSON response.
        """
        encrypted_password = self._encrypt_password()
        payload = {
            "entityId": transaction_id,
            "time": time,
            "userLogin": self.username,
            "userPassword": encrypted_password,
        }
        return self._unlock_ledger_for_modification(payload)

    def get_transaction_charges(
        self,
        transaction_id: str,
        patient_id: str,
        amount: float,
        transaction_type: str,
        ledger_view: Literal["GUARANTOR_VIEW", "PATIENT_VIEW"],
    ) -> list[Charge]:
        """
        Get all charges for a specific transaction in dentrix for a given id.

        Args:
            transaction_id (str): The transaction id.
            patient_id (str): The patient id.
            amount (float): The amount.
            transaction_type (str): The transaction type.
            ledger_view (Literal["GUARANTOR_VIEW", "PATIENT_VIEW"]): The ledger view type.

        Returns:
            list[Charge]: List of charge objects.
        """
        params = {
            "amount": amount,
            "ledgerView": ledger_view,
            "creditId": transaction_id,
            "patientId": patient_id,
        }
        raw_charges = self._get_transaction_charges(params, transaction_type)
        return [Charge.from_payload(c) for c in raw_charges]

    def update_transaction(
        self,
        transaction_id: int,
        payload: dict,
        transaction_type: str = "adjustment/credit",
    ) -> dict:
        """Update a transaction in the ledger.

        Args:
            transaction_id (str): The transaction id.
            payload (dict): The payload.
            transaction_type (str): The transaction type, defaults to "adjustment/credit".

        Returns:
            dict: The updated transaction.
        """
        self.unlock_ledger_for_modification(transaction_id)
        return self._update_transaction(transaction_id, payload, transaction_type)

    def is_billing_statement_locked(self) -> bool | None:
        """Checks if a billing statement is locked."""
        return self._is_billing_statement_locked().get("isLocked")

    def _check_if_billing_form_is_open(self) -> bool:
        """Check if the billing form is open.

        Returns:
            bool: True if the billing form is open, False otherwise.
        """
        try:
            sleep(2)
            if not self.browser.is_element_visible(locator=Locators.Billing.FORM_CHECK):
                self.browser.click_element(locator=Locators.Billing.GENERATE_STATEMENT_FORM)
                sleep(2)
                if self.browser.is_element_visible(locator=Locators.Billing.FORM_CHECK):
                    return True
                return False
            else:
                return True
        except Exception as error:
            logger.info(f"Failed to check if billing form is open. {str(error)}")
            return False

    @retry(tries=3, delay=1, backoff=2)
    def generate_billing_statements_ui(self) -> None:
        """Generates billing statements using the Dentrix UI.

        This method performs the following steps:
        1. Logs in to Dentrix.
        2. Navigates to the billing review page.
        3. Checks if billing statements are currently being reviewed by another user.
        4. Checks if the billing statements form is visible.
        5. Skips accounts with pending claims.
        6. Generates statements only for accounts not billed since a specific date.
        7. Sets the due date for the statements.
        8. Starts generating the statements and monitors the progress.
        9. Logs the execution time.
        10. Closes the browser.

        Raises:
            BillingStatementsOpenError: If billing statements are currently being reviewed
            by another user or if the billing statements form is not visible.
            Exception: If an error occurs during the generation of billing statements.

        Returns:
            None
        """
        # THIS METHOD CANNOT BE AND WAS NOT SAFELY TESTED
        # Please remove this comment if this logic was executed and worked as intended.
        self.browser.go_to(DentrixUrls.BILLING_STATEMENT_UI)

        if self.browser.is_element_visible(locator=Locators.Billing.MESSAGE):
            billing_message_text = self.browser.get_text(locator=Locators.Billing.MESSAGE)
            if "currently reviewing billing statements" in billing_message_text:
                msg = (
                    "Billing statements are currently being reviewed with another user, "
                    "please close that session and try again."
                )
                raise BillingStatementsOpenError(
                    msg,
                )

        if not self.browser.is_element_visible(locator=Locators.Billing.MESSAGE):
            if not self.browser.is_element_visible(locator=Locators.Billing.FORM_CHECK):
                for _ in range(4):
                    is_form_visible = self._check_if_billing_form_is_open()
                    if is_form_visible:
                        break
                else:
                    msg = "Billing statements form is not visible."
                    raise BillingStatementsOpenError(msg)
            # Skip accounts with claim pending
            if not self.browser.is_checkbox_selected(locator=Locators.Billing.PENDING_CHARGE_BOX):
                self.browser.click_element(locator=Locators.Billing.SKIP_CLAIM_PENDING)
            # Only generate statement if not billed since
            if not self.browser.is_checkbox_selected(locator=Locators.Billing.NOT_BILLED_SINCE_DATE_CHECK_BOX):
                self.browser.click_element(locator=Locators.Billing.NOT_BILLED_SINCE_DATE_LABEL)
            # Set date today-2 days.
            date_day = (now() - timedelta(days=2)).day
            date_to_select = Locators.Billing.DATE_TO_SELECT(date_day)
            self.browser.click_element(locator=Locators.Billing.NOT_BILLED_SINCE_DATE_INPUT)

            if not self.browser.is_element_visible(locator=date_to_select):
                self.browser.click_element(locator=Locators.Billing.PREVIOUS_AVAILABLE_MONTH)

            self.browser.click_element(locator=date_to_select)

            if self.browser.is_checkbox_selected(locator=Locators.Billing.DUE_DATE_CHECK_BOX):
                self.browser.click_element(locator=Locators.Billing.DUE_DATE_LABEL)
            self.browser.click_element(locator=Locators.Billing.GENERATE_LIST)

        # Set condition to check if the element is visible and start time
        condition = self.browser.is_element_visible(locator=Locators.Billing.MESSAGE)
        # Start the timer
        start_time = time()

        while condition:
            sleep(1)
            condition = self.browser.is_element_visible(locator=Locators.Billing.MESSAGE)
            if not condition:
                break
            else:
                try:
                    percentage = self.browser.get_text(locator=Locators.Billing.PERCENTAGE_LOADED)
                    logger.info(f"Generating statements {percentage}...")
                except ElementNotFound:
                    # If the element is not found and previous loggers shows percentages
                    # it means it ended up but ui was not refreshed
                    # breaking and continuing the workflow
                    break

        logger.info("Finished generating statements.")
        end_time = time()
        execution_time = end_time - start_time
        logger.info(f"Execution time: {str(execution_time)} seconds")
        self.browser.close_all_browsers()

    def post_appointment_note(self, location_id: int | str, request_body: dict) -> dict:
        """Posts an appointment note to the Dentrix server for a specific location.

        Args:
            location_id (int): The identifier of the location where the appointment is to be posted.
            request_body (dict): The request body containing the appointment note and patient information.

        Returns:
            dict: The response from the Dentrix server.
        """
        self._change_location(location_id)
        return self._post_appointment_note(request_body)

    def get_payer_info(self) -> list[Payer]:
        """Get all payer info from Dentrix.

        Returns:
            List[Payer]: List of Payer objects.
        """
        return [Payer.from_payload(data) for data in self._get_all_payers()]

    def get_ledger_information_by_patient(self, patient_id: str) -> LedgerBalance:
        """Get ledger information filtering by patient.

        Args:
            patient_id (str): patient backend id

        Returns:
            LedgerBalance: The ledger information.
        """
        params = {"view": "PATIENT"}
        ledger_info = self._get_ledger_information_by_view(patient_id, params)
        if ledger_info:
            return LedgerBalance.from_payload(ledger_info)
        else:
            msg = "No Ledger Balance Info found on Dentrix"
            raise NoLedgerBalanceError(msg)

    def get_ledger_information_by_guarantor(self, patient_id: str) -> LedgerBalance:
        """Get ledger information filtering by guarantor.

        Args:
            patient_id (str): patient backend id

        Returns:
            LegerBalance: The ledger information.
        """
        params = {"view": "GUARANTOR"}
        ledger_info = self._get_ledger_information_by_view(patient_id, params)
        if ledger_info:
            return LedgerBalance.from_payload(ledger_info)
        else:
            msg = "No Ledger Balance Info found on Dentrix"
            raise NoLedgerBalanceError(msg)

    def get_patient_ledger_transactions(
        self,
        patient_id: int,
        *,
        auto_scroll_to_recent_transactions: bool = True,
        range: str = "ALL_HISTORY_DATE_RANGE",
        sorting: str = "BY_STATEMENT",
        view: Literal["GUARANTOR_VIEW", "PATIENT_VIEW"],
        show_history: bool = False,
        show_time: bool = False,
        show_deleted: bool = True,
        show_xfers: bool = True,
        reset_history: bool = False,
        is_since_last_zero_balance_enabled: bool = True,
        filtered_date_range: str = "All history",
    ) -> list[PatientLedgerTransaction]:
        """Method to get all transactions in a patient's ledger in the specified view.

        Args:
            patient_id (int): The patient ID that the information will be fetched from.
            view (Literal["GUARANTOR_VIEW", "PATIENT_VIEW"]): The view type.
            auto_scroll_to_recent_transactions (bool): If True, scrolls to recent transactions.
            range (str): The date range for the transactions.
            sorting (str): The sorting method for the transactions.
            show_history (bool): If True, shows the history of transactions.
            show_time (bool): If True, shows the time of transactions.
            show_deleted (bool): If True, shows deleted transactions.
            show_xfers (bool): If True, shows transfer transactions.
            reset_history (bool): If True, resets the history of transactions.
            is_since_last_zero_balance_enabled (bool): If True, enables the since last zero balance filter.
            filtered_date_range (str): The date range for filtering transactions.

        Returns:
            list[PatientLedgerTransaction]: The list of PatientLedgerTransaction objects.
        """
        default_params = {
            "autoScrollToRecentTransactions": auto_scroll_to_recent_transactions,
            "range": range,
            "sorting": sorting,
            "view": view,
            "showHistory": show_history,
            "showTime": show_time,
            "showDeleted": show_deleted,
            "showXfers": show_xfers,
            "resetHistory": reset_history,
            "isSinceLastZeroBalanceEnabled": is_since_last_zero_balance_enabled,
            "filteredDateRange": filtered_date_range,
        }

        raw_transactions = self._get_ledger_list(patient_id, default_params)

        return [PatientLedgerTransaction.from_payload(tx) for tx in raw_transactions]

    def get_providers_from_location(self, location_id: int) -> list[Provider]:
        """Get all providers from a specific location.

        Args:
            location_id (int): The location ID.

        Returns:
            list[Provider]: List of Provider objects.
        """
        return [Provider.from_payload(provider) for provider in self._get_providers_from_location(location_id)]

    def get_patient_information(self, patient_id: int) -> PatientInfo:
        """Get patient information.

        Args:
            patient_id (int): The patient ID.

        Returns:
            PatientInfo: The patient information.
        """
        patient_info = self._get_patient_basic_information(patient_id)
        if patient_info:
            return PatientInfo.from_payload(patient_info)
        else:
            msg = "No Patient Info found on Dentrix"
            raise PatientNotFoundError(msg)

    def get_xray_exams(self, patient_id: str, claim_locator: str) -> list[XrayExam]:
        """Get X-ray exams for a patient.

        Args:
            patient_id (str): The patient ID.
            claim_locator (str): The claim locator needed to reauthorize gathering cookies.

        Returns:
            list[XrayExam]: List of XrayExam objects.
        """
        self.gather_claim_imaging_cookies(patient_id, claim_locator)
        return [XrayExam.from_payload(xray_exam) for xray_exam in self._get_xray_exams(patient_id)]

    def get_xray_images(self, exam_id: int) -> list[XrayImage]:
        """Get X-ray images for a patient.

        Args:
            exam_id (int): The exam ID to get images for.

        Returns:
            list[XrayImage]: List of XrayImage objects.
        """
        return [XrayImage.from_payload(xray_exam) for xray_exam in self._get_xray_images(exam_id)]

    def get_document_list(self, patient_id: int) -> list[Document]:
        """Get documents for a patient.

        Args:
            patient_id (int): The patient ID.

        Returns:
            list[Document]: List of Document objects.
        """
        return [Document.from_payload(document) for document in self._get_document_list(patient_id)]

    def get_procedure_codes(self) -> list[ProcedureCode]:
        """Get procedure codes.

        Returns:
            list[ProcedureCode]: List of ProcedureCode objects.
        """
        return [ProcedureCode.from_payload(code) for code in self._get_procedure_codes()]

    def get_guarantor_dependents(self, patient_id: str) -> list[Patient]:
        """Get dependent patients (under the guarantor) as Patient objects.

        Args:
            patient_id (str): patient id to get dependent patients.

        Returns:
            list[Patient]: List of Patient objects.
        """
        return [Patient.from_payload(patient) for patient in self._get_guarantor_related_patients(patient_id)]

    def get_transaction_payload(self, transaction_id: str) -> Transaction:
        """Fetches and converts a transaction payload into a TransactionPayload object."""
        raw_payload = self._get_transaction_payload(transaction_id)
        return Transaction.from_payload(raw_payload)

    def fetch_patients_information(self, patient_ids: list[int]) -> list[PatientSearchResult]:
        """Fetches and converts a list of patients into Patient objects.

        Args:
            patient_ids (list[int]): List of patient IDs to fetch.

        Returns:
            list[PatientSearchResult]: List of Patient objects.
        """
        patients = self._get_patients_information(patient_ids)
        return [PatientSearchResult.from_payload(patient) for patient in patients]

    def download_document(self, document_id: int, patient_id: int, target_path: str | Path = None) -> Path | str:
        """Download a document from DentrixAscend API.

        Args:
            document_id (int): The document ID.
            patient_id (int): The patient ID.
            target_path (str | Path, optional): The path to save the downloaded document.
            Defaults to None.

        Returns:
            Path | str: The path where the document is saved.
        """
        if target_path is None:
            target_path = Path(f"{document_id}.pdf")

        content = self._download_document(document_id, patient_id)
        with open(target_path, "wb") as file:
            file.write(content)

        return target_path

    def get_appointments_by_patient_id(self, patient_id: int) -> list[Appointment]:
        """Get appointments by patient ID.

        Args:
            patient_id (int): The ID of the patient.

        Returns:
            list[Appointment]: A list of Appointment objects for the specified patient.
        """
        appointments_data = self._get_appointments_by_patient_id(patient_id)
        appointments = [Appointment.from_payload(appointment) for appointment in appointments_data]
        return appointments
