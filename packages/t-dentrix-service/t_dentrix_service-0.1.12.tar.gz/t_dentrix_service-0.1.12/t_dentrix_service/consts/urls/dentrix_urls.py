"""Module for Urls object."""


class DentrixUrls:
    """URLs for Dentrix website."""

    BASE_URL = "https://live3.dentrixascend.com"
    LOGIN_URL = f"{BASE_URL}/login"
    INDEX_URL = f"{BASE_URL}/IEighteenN/index"
    UNLOCK_LEDGER_URL = f"{BASE_URL}/ledger/unlock"
    PUBLIC_KEY_URL = f"{BASE_URL}/ledger/unlock/publicKey"
    UNLOCK_TIME_URL = f"{BASE_URL}/unlock/time"
    DASHBOARD = f"{BASE_URL}/pm#/dashboard"
    PATIENT_DOCUMENTS_URL = (BASE_URL + "/pm#/patient/document/{}").format

    LOCATIONS_URL = f"{BASE_URL}/bootstrap/location"
    INSURANCE_CARRIERS_URL = f"{BASE_URL}/bootstrap/insuranceCarrier"
    FEE_SCHEDULE_URL = f"{BASE_URL}/feeSchedule"
    PRACTICE_PROCEDURE_URL = f"{BASE_URL}/practiceProcedureREST"
    GET_SCHEDULES = f"{BASE_URL}/v2/schedule/day"
    CURRENT_LOCATION = f"{BASE_URL}/eraEnrollment/getCurrentLocationEnrollmentStatus"
    SET_LOCATION_URL = f"{BASE_URL}/profile/currentLocation"
    PROVIDERS_FROM_LOCATION_URL = "{}/provider/location/{}".format
    PATIENT_SEARCH_URL = f"{BASE_URL}/patient/smartIndex"
    PATIENT_INFO_URL = (BASE_URL + "/patient/{}").format
    GENERATE_CHART_NUMBER_URL = f"{BASE_URL}/patient/chartNumber/generate"
    PATIENT_INSURANCE_PLANS_URL = (BASE_URL + "/patientInsurancePlanREST/{}").format
    SET_ELIGIBILITY_URL = f"{BASE_URL}/patientInsurancePlanREST/setEligibilityStatus"
    GET_CLAIMS_URL = (BASE_URL + "/patient/ledger/payment/claim/partial/{}?view=GUARANTOR_VIEW").format
    LEDGER_LIST_URL = (BASE_URL + "/patient/{}/ledger/list").format
    GET_CLAIM_SERVICES_INFO = (
        "{}/patient/ledger/payment/insurance/distribution/create?amount={}&insuranceClaimId={}".format
    )
    DEDUCTIBLES_MET_URL = (BASE_URL + "/patient/ledger/payment/insurance/deductiblesMet?insuranceClaimId={}").format
    ADJUSTMENTS_URL = (BASE_URL + "/patient/ledger/payment/claim/{}/adjustment").format
    POST_PAYMENT_INFO_URL = f"{BASE_URL}/patient/ledger/payment"
    PATIENT_BALANCE_URL = (BASE_URL + "/patient/{}/ledger/agingBalance?view=GUARANTOR_VIEW").format
    SUBSEQUENT_INSURANCE_CLAIM_URL = (BASE_URL + "/subsequentInsuranceClaim/createSubsequentClaim/{}").format
    GET_DOCUMENTS_URL = (BASE_URL + "/patient/{}/document/list?setByteSize=true").format
    DOCUMENT_INFO_URL = (BASE_URL + "/document/{}/document").format
    ADD_TAG_TO_DOCUMENT_URL = (BASE_URL + "/document/{}/tag/tag").format
    DOCUMENT_EXPORT_URL = f"{BASE_URL}/document/export"
    CLINICAL_NOTES_URL = (BASE_URL + "/selectPatient/{}").format
    GENERATE_CLINICAL_NOTES_URL = (BASE_URL + "/patient/clinical/note/{}").format
    CLINICAL_NOTE_INFO_URL = (BASE_URL + "/patient/clinical/note/{}/{}").format
    INSURANCE_CLAIM_URL = (BASE_URL + "/insuranceClaim/{}").format
    LEDGER_URL = (BASE_URL + "/pm#/ledger/{}").format
    SUBMIT_CLAIM_URL = (BASE_URL + "/insuranceClaim/submit/{}").format
    GET_XRAY_EXAMS_URL = f"{BASE_URL}/rci/ClaimAttachment.aspx/GetNonHiddenExams"
    GET_XRAY_IMAGES_URL = f"{BASE_URL}/rci/ClaimAttachment.aspx/GetAllImages"
    PROBLEM_URL = f"{BASE_URL}/problem"
    SOLUTION_URL = f"{BASE_URL}/solution"
    ACTIVITY_URL = f"{BASE_URL}/activity"
    ATTACHMENTS_VALIDATION_URL = f"{BASE_URL}/insuranceClaim/attachmentsValidation"
    EXAMS_FOR_CLAIM_URL = (BASE_URL + "/patient/{}/perio/patientExamsForClaim").format
    CLAIM_NOTES_URL = (BASE_URL + "/patient/{}/progress/note/").format
    OVERDUE_CLAIMS_URL = f"{BASE_URL}/kpi/OVERDUE_CLAIMS"
    APPLY_CREDITS = (BASE_URL + "/patient/{}/ledger/allocateUnappliedCredits").format
    AGED_RECEIVABLES = f"{BASE_URL}/agedReceivables/create"
    BILLING_STATEMENT = f"{BASE_URL}/billingStatements"
    TRANSACTION_PAYMENT_URL = (BASE_URL + "/patient/ledger/payment/{}?isSpecific=false").format
    TRANSACTION_CHARGES_URL = (BASE_URL + "/patient/ledger/{}/distribution/read").format
    TRANSACTION_LEDGER_URL = (BASE_URL + "/patient/ledger/{}/{}").format
    APPOINTMENT_REST_URL = f"{BASE_URL}/appointmentREST"
    APPOINTMENT_WITH_PATIENT_URL = f"{APPOINTMENT_REST_URL}/appointmentWithPatient"
    UPDATE_APPOINTMENT_URL = f"{APPOINTMENT_WITH_PATIENT_URL}Lite"
    CARRIER_INSURANCE_PLAN_URL = (BASE_URL + "/carrierInsurancePlanREST/{}").format
    CARRIER_PLAN_COVERAGE_URL = (BASE_URL + "/carrierPlanCoverage/{}").format
    SUBSCRIBER_INSURANCE_PLAN_URL = (BASE_URL + "/subscriberInsurancePlanREST/showByPatientID/{}/").format
    LEDGER_INFO = "{}/patient/{}/ledger/agingBalance".format
    PATIENTS_BILLING_STATEMENT = (BASE_URL + "/billingStatements/{}").format
    GENERATE_BILLING_STATEMENT = f"{BASE_URL}/billingStatements/generate"
    IS_BILLING_LOCKED = f"{BASE_URL}/billingStatements/isLocked"
    QUERY_PATIENT_CONNECTION = (BASE_URL + "/patient/{}/connection/statement").format
    SEND_E_STATEMENT = f"{BASE_URL}/billingStatements/eStatement"
    BILLING_STATEMENT_UI = f"{BASE_URL}/pm#/billingReview"
    GET_GUARANTOR_RELATED_PATIENTS = "{}/patient/{}/ledger/guarantoredPatientsAsGuarantor".format
    PATIENTS_INFO_URL = f"{BASE_URL}/patient/lite/"
