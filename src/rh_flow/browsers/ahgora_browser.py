import time

from rich import print
from rich.console import Console
from selenium.webdriver.common.by import By
from rh_flow.utils.config import Config
from rh_flow.utils.creds import Creds

from rh_flow.browsers.core_browser import CoreBrowser


class AhgoraBrowser(CoreBrowser):
    URL = "https://auth.ahgora.com.br/#/login"

    @staticmethod
    def download_employees_data() -> None:
        ahgora_browser = AhgoraBrowser()
        ahgora_browser.retry_func(
            func=lambda: ahgora_browser._start_employees_download(),
            max_tries=2,
        )

    def __init__(self):
        self.console = Console()
        with self.console.status(
            "[yellow]Iniciando AHGORA webdriver[/]", spinner="dots"
        ):
            headless_mode = Config().data.get("headless_mode")
            super().__init__(url=self.URL, headless_mode=headless_mode)

    def _start_employees_download(self) -> None:
        with self.console.status(
            "Baixando [yellow]funcionários[/] do AHGORA", spinner="dots"
        ):
            self._login()
            self.driver.get("https://app.ahgora.com.br/funcionarios")
            self._show_dismissed_employees()
            self._click_plus_button()
            self._export_to_csv()
            self.close_driver()
        print("[bold green]Download de funcionários do AHGORA concluído[/bold green]")

    def _login(self) -> None:
        creds = Creds()
        user = creds.ahgora_user
        psw = creds.ahgora_psw
        company = creds.ahgora_company

        for i in range(2):
            self._enter_username("email", user)
            self._click_enter_button()
            self._enter_password("password", psw)
            self._click_enter_button()
        self._select_company(company)
        self._close_banner()
        time.sleep(self.DELAY)

    def _enter_username(self, selector: str, user: str) -> None:
        self.send_keys(selector, user, selector_type=By.NAME)

    def _enter_password(self, selector: str, password: str) -> None:
        self.send_keys(selector, password, selector_type=By.NAME)

    def _select_company(self, company) -> None:
        self.click_element(f"//*[contains(text(), '{company}')]")

    def _close_banner(self) -> None:
        try:
            self.click_element("buttonAdjustPunch", selector_type=By.ID, max_tries=5)
        except Exception:
            time.sleep(self.DELAY)

    def _show_dismissed_employees(self) -> None:
        self.click_element("filtro_demitido", selector_type=By.ID)

    def _click_plus_button(self) -> None:
        self.click_element("mais", selector_type=By.ID)

    def _export_to_csv(self) -> None:
        self.click_element("arquivo_csv", selector_type=By.ID)
        time.sleep(10)

    def _click_enter_button(self) -> None:
        self.click_element("//*[contains(text(), 'Entrar')]")
