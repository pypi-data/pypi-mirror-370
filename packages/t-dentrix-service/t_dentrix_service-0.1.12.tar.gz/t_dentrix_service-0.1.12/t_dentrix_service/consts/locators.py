"""Module that contains Locator object."""


class Locators:
    """Locators for Dentrix website."""

    class Login:
        """Locators for Dentrix login."""

        ORGANIZATION_XP = "//input[@id='organization']"
        USERNAME_XP = '//input[@id="username"]'
        CONTINUE_XP = '//input[@id="continue" and @type="button"]'
        PASSWORD_XP = '//input[@id="password"]'  # noqa: S105
        SEND_XP = '//*[@id="send"]'
        OVERVIEW_XP = '//*[@id="overviewContainer"]//h1[text()="Overview"]'

    class Patients:
        """Locators for Dentrix patients."""

        HOME = "//span[@title='Home']"
        CURRENT_LOCATION = "//span[@class='currentLocationName']"
        LOCATION_SEARCH_INPUT = "//input[@class='search-field']"
        LOCATION_SEARCH_RESULT = "//a[@class='locationNavigationLink']"
        LOCATION_SEARCH_RESULT_LOCATION = "span[@class='locationName']"
        PATIENT_SEARCH_INPUT = "//span[@class='newPatientSearch']//input"
        NO_PATIENT_SEARCH_RESULT = "//div[@class='noResultsFound emptyResult']"
        PATIENT_SEARCH_RESULT = "//ul[@class='patientsList']//a"
        TOTAL_CLAIMS = "//div[@class='totalClaims']"
        UNSENT_CLAIMS = "//div[text()='Unsent Claims']"
        UNSENT_CLAIMS_EDIT = "//button[@class='btn edit']"
        PATIENT_TAB = "//span[@title='Patient']"

    class Insurance:
        """Locators for Dentrix insurance."""

        INSURANCE = "//div[@id='insurance']"
        PATIENT_PLANS = "//table[@id='patientPlansTable']"
        INSURANCE_ROWS = "//table[@id='patientPlansTable']//tr[@class='insuranceList']"
        CARRIER = "//td[@class='carrier']"
        ORDER = "//span[@data-name='coverageType']"
        DIALOGUE = "//span[@class='ui-button-icon ui-icon ui-icon-closethick']"

    class Documents:
        """Locators for Dentrix documents."""

        PATIENT_OPENER = "//div[@class='patientOpener float-left']"
        DOCUMENT_MANAGER = "//a[@title='Document Manager']"
        SHOW_INFORMATION_BAR = "//div[@title='Show patient information bar']"
        SHADOW_ROOT_PARENT = "//div[@id='pageContent']"
        UPLOAD_BUTTON = "button[data-pendo='document-upload-button']"
        UPLOAD_SHADOW_ROOT = "//div[@id='react-shadow-Dialog']"
        UPLOAD_INPUT = "div[data-test='drag-and-drop-content'] input[type='file']#input-file"
        DIALOGUE = "div[data-test='dialog-box'] > div:nth-child(3) > div > div > button:nth-child(2)"
        CLOSE_BUTTON = (
            "//button[@class='ui-button ui-corner-all ui-widget ui-button-icon-only ui-dialog-titlebar-close']"
        )
        DIALOGUE_ALERT = "//div[@class='ui-dialog-buttonset']//button"
        CLOSE_ALERT = "//button[@aria-label='Close']"
        UPLOAD_MESSAGE = "span.message-title"
        UPLOAD_SCRIPT = """
            const shadowHost = document.querySelector("#react-shadow-Dialog");
            const shadowRoot = shadowHost.shadowRoot;
            const buttons = shadowRoot.querySelectorAll('button');
            let saveButton = null;
            buttons.forEach(button => {
                if (button.textContent.trim().toLowerCase() === 'save') {
                    saveButton = button;
                }
            });
            if (saveButton) {
                saveButton.click();
                return true;
            } else {
                return false;
            }
        """

    class Ledger:
        """Locators for Dentrix ledger."""

        MEDICAL_ALERT_TEXT = "Medical Alerts for"
        PROCEDURES_POSTED_TEXT = "One or more patients on this guarantor account have procedures posted"
        CLOSE_COVERAGE_GAP_ALERT = "//div[@class='close']"
        ATTACHMENTS_TAB = "//a[@href='#attachmentsTab']"
        ADD_IMAGES = "//button[@id='addFromImaging']"
        ATTACH_IMAGES = "//button[@id='addImages']"

    class Billing:
        """Locators related to billing process."""

        MESSAGE = '//*[@id="pacifierMessage"]'
        FORM_CHECK = '//span[contains(text(),"Generate Billing Statements")]'
        GENERATE_STATEMENT_FORM = '//*[@id="generateStatements"]'
        PENDING_CHARGE_BOX = '//*[@id="pendingCharges"]'
        SKIP_CLAIM_PENDING = '//label[contains(@class,"pendingChargesLabel")]'
        NOT_BILLED_SINCE_DATE_CHECK_BOX = '//*[@id="settingsNotBilledSinceDate"]'
        NOT_BILLED_SINCE_DATE_LABEL = '//label[contains(@class,"notBilledSinceDateLabel")]'
        NOT_BILLED_SINCE_DATE_INPUT = '//*[@id="settingsNotBilledSinceDateInput"]'
        DATE_TO_SELECT = '//td[@class="available " and text()="{}"]'.format
        PREVIOUS_AVAILABLE_MONTH = '//th[@class="prev available month"]'
        DUE_DATE_CHECK_BOX = '//*[@id="settingsDueDate"]'
        DUE_DATE_LABEL = '//label[contains(@class,"dueDateLabel")]'
        GENERATE_LIST = '//*[@id="settingsGenerateList"]'
        PERCENTAGE_LOADED = '//*[@id="percentageLoaded"]'
