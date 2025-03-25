import os
import time

from dotenv import load_dotenv
from rich import print
from rich.console import Console
from selenium.webdriver.common.by import By

from rh_flow.browsers.core_browser import CoreBrowser


class AhgoraBrowser(CoreBrowser):
    URL = "https://login.ahgora.com.br/"

    @staticmethod
    def download_employees_data() -> None:
        ahgora_browser = AhgoraBrowser()
        ahgora_browser._start_employees_download()

    def __init__(self):
        console = Console()
        with console.status("[yellow]Iniciando AHGORA webdriver[/]", spinner="dots"):
            super().__init__(self.URL)

    def _start_employees_download(self) -> None:
        console = Console()
        with console.status(
            "Baixando [yellow]funcionários[/] do AHGORA", spinner="dots"
        ):
            self._login()
            self.driver.get("https://app.ahgora.com.br/funcionarios")
            self._show_dismissed_employees()
            self._click_plus_button()
            self._export_to_csv()
            super().close_driver()
        print("[bold green]Download de funcionários do AHGORA concluído[/bold green]")

    def _login(self) -> None:
        load_dotenv()
        user = os.getenv("AHGORA_USER")
        pwd = os.getenv("AHGORA_PASSWORD")

        self._enter_username("email", user)
        self._click_enter_button()
        self._enter_password("password", pwd)
        self._click_enter_button()
        self._select_company()
        self._close_banner()
        time.sleep(super().DELAY)

    def _enter_username(self, selector: str, user: str) -> None:
        super().send_keys(selector, user, selector_type=By.ID)

    def _enter_password(self, selector: str, password: str) -> None:
        super().send_keys(selector, password, selector_type=By.ID)

    def _select_company(self) -> None:
        company = os.getenv("AHGORA_COMPANY")
        super().click_element(f"//*[contains(text(), '{company}')]")

    def _close_banner(self) -> None:
        super().click_element("buttonAdjustPunch", selector_type=By.ID)

    def _show_dismissed_employees(self) -> None:
        super().click_element("filtro_demitido", selector_type=By.ID)

    def _click_plus_button(self) -> None:
        super().click_element("mais", selector_type=By.ID)

    def _export_to_csv(self) -> None:
        super().click_element("arquivo_csv", selector_type=By.ID)
        time.sleep(30)

    def _click_enter_button(self) -> None:
        super().click_element("//*[contains(text(), 'Entrar')]")
