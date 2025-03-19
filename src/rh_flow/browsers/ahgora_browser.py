import os
from time import sleep

from dotenv import load_dotenv
from rich import print
from selenium.webdriver.common.by import By

from browsers.core_browser import CoreBrowser


class AhgoraBrowser(CoreBrowser):
    URL = "https://login.ahgora.com.br/"

    @staticmethod
    def download_employees_data() -> None:
        ahgora_browser = AhgoraBrowser()
        ahgora_browser._start_employees_download()

    def __init__(self):
        super().__init__(self.URL)

    def _start_employees_download(self) -> None:
        print("Baixando dados de [yellow]funcionários[/] do AHGORA")
        super().__init__(self.URL)
        self._login()
        self.driver.get("https://app.ahgora.com.br/funcionarios")
        self._show_dismissed_employees()
        self._click_plus_button()
        self._export_to_csv()
        sleep(30)
        super().close_driver()
        print("[green]Download de dados de funcionários do AHGORA concluído[/]")

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
        sleep(super().DELAY)

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

    def _click_enter_button(self) -> None:
        super().click_element("//*[contains(text(), 'Entrar')]")
