"""Contains DentrixServiceLogin object."""

from typing import Any

from fake_useragent import UserAgent
from requests.sessions import Session
from retry import retry
from RPA.Browser.Selenium import Selenium
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from SeleniumLibrary.errors import ElementNotFound, NoOpenBrowser

from t_dentrix_service.consts.locators import Locators
from t_dentrix_service.consts.urls.dentrix_urls import DentrixUrls
from t_dentrix_service.utils.logger import logger
from t_dentrix_service.utils import gather_credentials

USER_AGENT = UserAgent(os="windows", min_percentage=1.3).chrome


class DentrixServiceLogin:
    """Segment of Dentrix Service solely responsible with the authentication process."""

    def __init__(self, dentrix_credentials: dict | tuple | Any, proxy_credentials: dict | tuple | Any = None) -> None:
        """Constructs Dentrix Service.

        Args:
            dentrix_credentials (dict | tuple | Any): Credentials for Dentrix login process, can be a dict with
            "username" and "password" keys, a (username, password) paired tuple or a object with username and password
            attributes.
            proxy_credentials (dict | tuple | Any, optional): _description_. Defaults to None.
        """
        self.session = Session()
        self.dentrix_credentials = dentrix_credentials
        self._set_credentials()
        self.browser = Selenium()
        if proxy_credentials is not None:
            self._set_proxy(proxy_credentials)

    def _set_proxy(self, proxy_credentials: dict | tuple | Any) -> None:
        """Set proxy for Dentrix Session."""
        vpn_username, vpn_password = gather_credentials(proxy_credentials)
        vpn_ip = "us9576.nordvpn.com"
        vpn_port = "89"

        proxies = {
            "https": f"https://{vpn_username}:{vpn_password}@{vpn_ip}:{vpn_port}",
        }

        self.session.proxies = proxies

    def _set_credentials(self) -> None:
        """Set credentials to dentrix login process."""
        self.username, self.password = gather_credentials(self.dentrix_credentials)

    def _click_element_if_exists(self, locator: str) -> None:
        """Clicks the element if it is visible; handles exceptions silently."""
        try:
            self.browser.click_element_when_visible(locator)
        except (ElementNotFound, AssertionError, ElementClickInterceptedException):
            pass

    def _get_index(self) -> dict:
        """Retrieves index information.

        Raises:
            HTTPError: Raised if the GET request fails for any reason.

        Returns:
            dict: The JSON response.
        """
        response = self.session.get(DentrixUrls.INDEX_URL, headers=self._headers())
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _headers(content_type: str = "application/json; charset=UTF-8", add_headers: dict = None) -> dict:
        """Returns the headers for the request with customizable content-type.

        Args:
            content_type (str): The content type of the request.
            add_headers (dict): Additional headers to add to the request.

        Returns:
            dict: The headers for the request.
        """
        headers = {"User-Agent": USER_AGENT, "x-requested-with": "XMLHttpRequest"}
        if content_type:
            headers["Content-Type"] = content_type

        if add_headers:
            headers.update(add_headers)
        return headers

    def _open_browser(self) -> None:
        """Opens a new browser instance, sets its window size, and maximizes it."""
        browser_options = Options()
        browser_options.add_argument("--no-sandbox")
        browser_options.add_argument("--disable-dev-shm-usage")
        self.browser.open_available_browser(
            url=DentrixUrls.LOGIN_URL,
            headless=True,
            browser_selection="Chrome",
            user_agent=USER_AGENT,
            options=browser_options,
        )
        self.browser.set_window_size(1920, 1080)
        self.browser.maximize_browser_window()

    @retry(tries=3, delay=1, backoff=2)
    def login_to_dentrix(self) -> None:
        """Logs into the Dentrix application and sets cookies for the session.

        Raises:
            Exception: Raised if logging into Dentrix fails at any stage, providing details about the specific error.
        """
        try:
            self._login()
            self._set_cookies()
            self._get_index()

        except Exception as error:
            self.browser.capture_page_screenshot("Login_failed_Attempt.png")
            self.browser.close_all_browsers()
            msg = "Logging into Dentrix failed"
            raise Exception(msg) from error

    def _login(self) -> None:
        """Automates the login process into the Dentrix system."""
        if self.is_browser_open():
            self.logout_and_close_browser()
        self._open_browser()
        self.browser.input_text_when_element_is_visible(Locators.Login.ORGANIZATION_XP, "SDP")
        self.browser.input_text_when_element_is_visible(
            Locators.Login.USERNAME_XP, self.dentrix_credentials["username"]
        )
        self.browser.click_element_when_visible(Locators.Login.CONTINUE_XP)
        self.browser.input_text_when_element_is_visible(
            Locators.Login.PASSWORD_XP, self.dentrix_credentials["password"]
        )
        self.browser.click_element_when_visible(Locators.Login.SEND_XP)
        self.browser.wait_until_element_is_visible(Locators.Login.OVERVIEW_XP, timeout=60)

    def _set_cookies(self) -> None:
        """Transfers cookies from the Selenium browser instance to the requests session object."""
        for name, value in self.browser.get_cookies(as_dict=True).items():
            self.session.cookies.set(name, value)

    def is_browser_open(self) -> bool:
        """Check if the browser is open."""
        try:
            return self.browser.driver is not None
        except NoOpenBrowser:
            return False

    def logout_and_close_browser(self) -> None:
        """Logout and close the browser."""
        self.browser.close_browser()

    def handle_unexpected_logout(self) -> bool:
        """Handles the case where the user is logged out of Dentrix."""
        if not self.is_browser_open() or self.browser.does_page_contain_element(Locators.Login.SEND_XP):
            logger.warning("Logged out of Dentrix. Attempting login again.")
            self.login_to_dentrix()
            return True
        return False
