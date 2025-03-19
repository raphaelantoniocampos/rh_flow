from dotenv import load_dotenv
import os
from browsers.core_browser import CoreBrowser
from rich import print

from selenium.webdriver.common.by import By
from time import sleep


class AhgoraBrowser(CoreBrowser):
    URL = "https://login.ahgora.com.br/?state=4729a5c6da859a0d0cfd5aff43eb138d&response_type=code&approval_prompt=auto&redirect_uri=https%3A%2F%2Fapp.ahgora.com.br%2Flogin%2Foauth2&client_id=pontoweb"

    def __init__(self):
        super().__init__(self.URL)

    def download_data(self, option) -> None:
        print("[bold yellow]--- Iniciando Downloads AHGORA ---[/bold yellow]")
        self._login()
        sleep(super().DELAY)

        self._download_ahgora_employees()
        sleep(super().DELAY)

        super().close_driver()
        print("[bold green]--- Downloads AHGORA Concluídos ---[/bold green]")

    def _login(self) -> None:
        print("Fazendo [yellow]login[/] no AHGORA")
        load_dotenv()
        user = os.getenv("AHGORA_USER")
        pwd = os.getenv("AHGORA_PASSWORD")

        self._enter_username("email", user)
        self._click_enter_button()
        self._enter_password("password", pwd)
        self._click_enter_button()
        self._select_company()
        self._close_banner()

    def _enter_username(self, selector: str, user: str) -> None:
        super().send_keys(selector, user, selector_type=By.ID)

    def _enter_password(self, selector: str, password: str) -> None:
        super().send_keys(selector, password, selector_type=By.ID)

    def _select_company(self) -> None:
        company = os.getenv("AHGORA_COMPANY")
        super().click_element(f"//*[contains(text(), '{company}')]")

    def _close_banner(self) -> None:
        super().click_element("buttonAdjustPunch", selector_type=By.ID)

    def _download_ahgora_employees(self) -> None:
        print("Baixando dados de [yellow]funcionários[/] do AHGORA")
        self.driver.get("https://app.ahgora.com.br/funcionarios")
        self._show_dismissed_employees()
        self._click_plus_button()
        self._export_to_csv()
        sleep(super().DELAY)

        print("[green]Download de dados de funcionários do AHGORA concluído[/]")

    def _show_dismissed_employees(self) -> None:
        super().click_element("filtro_demitido", selector_type=By.ID)

    def _click_plus_button(self) -> None:
        super().click_element("mais", selector_type=By.ID)

    def _export_to_csv(self) -> None:
        super().click_element("arquivo_csv", selector_type=By.ID)

    def _click_enter_button(self) -> None:
        super().click_element("//*[contains(text(), 'Entrar')]")
