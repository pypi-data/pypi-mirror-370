"""Module that contains AscendUrls class."""


class AscendUrls:
    """URLs for Ascend API."""

    BASE_URL = "https://live3.dentrixascend.com/api"

    AGING_BALANCES = f"{BASE_URL}/v1/agingbalances"
    AGING_BALANCES_REPORT = f"{BASE_URL}/v1/agingbalances/report"

    APPOINTMENTS = f"{BASE_URL}/v1/appointments"
    APPOINTMENT_BY_ID = (BASE_URL + "/v1/appointments/{}").format
    APPOINTMENT_COLORS = f"{BASE_URL}/v1/appointmentcolors"
    APPOINTMENT_COLOR_BY_ID = (BASE_URL + "/v1/appointmentcolors/{}").format

    APPOINTMENT_HISTORIES = f"{BASE_URL}/v1/appointmenthistories"
    APPOINTMENT_HISTORY_BY_ID = (BASE_URL + "/v1/appointmenthistories/{}").format

    APPOINTMENT_STATUS_HISTORIES = f"{BASE_URL}/v1/appointmentstatushistories"
    APPOINTMENT_STATUS_HISTORY_BY_ID = (BASE_URL + "/v1/appointmentstatushistories/{}").format

    APPOINTMENT_TASKS = f"{BASE_URL}/v1/appointmenttasks"
    APPOINTMENT_TASK_BY_ID = (BASE_URL + "/v1/appointmenttasks/{}").format

    AUDITS = f"{BASE_URL}/v1/audits"

    BULK_INSURANCE_PAYMENTS = f"{BASE_URL}/v1/bulkinsurancepayments"
    BULK_INSURANCE_PAYMENT_BY_ID = (BASE_URL + "/v1/bulkinsurancepayments/{}").format

    CARRIER_INSURANCE_PLANS = f"{BASE_URL}/v1/carrierinsuranceplans"
    CARRIER_INSURANCE_PLAN_BY_ID = (BASE_URL + "/v1/carrierinsuranceplans/{}").format

    CARRIER_PLAN_COPAY_EXCEPTIONS = f"{BASE_URL}/v1/carrierplancopayexceptions"
    CARRIER_PLAN_COPAY_EXCEPTION_BY_ID = (BASE_URL + "/v1/carrierplancopayexceptions/{}").format

    CARRIER_PLAN_COVERAGE_EXCEPTIONS = f"{BASE_URL}/v1/carrierplancoverageexceptions"
    CARRIER_PLAN_COVERAGE_EXCEPTION_BY_ID = (BASE_URL + "/v1/carrierplancoverageexceptions/{}").format

    CLINICAL_NOTES = f"{BASE_URL}/v1/clinicalnotes"
    CLINICAL_NOTE_BY_ID = (BASE_URL + "/v1/clinicalnotes/{}").format

    LOCATIONS = f"{BASE_URL}/v1/locations"
    LOCATION_BY_ID = (BASE_URL + "/v1/locations/{}").format

    USERS = f"{BASE_URL}/v1/users"
    USER_BY_ID = (BASE_URL + "/v1/users/{}").format

    TRANSACTIONS = f"{BASE_URL}/v1/transactions"
    TRANSACTION_BY_ID = (BASE_URL + "/v1/transactions/{}").format

    VISITS = f"{BASE_URL}/v1/visits"
    VISIT_BY_ID = (BASE_URL + "/v1/visits/{}").format

    TIMECLOCKS = f"{BASE_URL}/v1/timeclocks"
    TIMECLOCK_BY_ID = (BASE_URL + "/v1/timeclocks/{}").format

    USAGE_REPORT = f"{BASE_URL}/v1/usageReport"

    PATIENT_INSURANCE_PLANS_URL = f"{BASE_URL}/v1/patientinsuranceplans"
