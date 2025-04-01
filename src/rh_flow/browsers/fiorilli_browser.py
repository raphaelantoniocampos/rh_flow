import os
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from time import sleep

from dotenv import load_dotenv
from rich import print
from selenium.webdriver.common.by import By

from rich.console import Console
from rh_flow.browsers.core_browser import CoreBrowser


class FiorilliBrowser(CoreBrowser):
    URL = "https://pompeu-pm-sip.sigmix.net/sip/"

    @staticmethod
    def download_employees_data() -> None:
        fiorilli_browser = FiorilliBrowser()
        fiorilli_browser.retry_func(
            func=lambda: fiorilli_browser._start_employees_download(),
            max_tries=2,
        )

    @staticmethod
    def download_absences_data() -> None:
        fiorilli_browser = FiorilliBrowser()
        fiorilli_browser.retry_func(
            func=lambda: fiorilli_browser._start_absences_download(),
            max_tries=2,
        )

    def __init__(self):
        self.console = Console()
        with self.console.status(
            "[yellow]Iniciando FIORILLI webdriver[/]", spinner="dots"
        ):
            super().__init__(self.URL)

    def _start_employees_download(self) -> None:
        ()
        with self.console.status(
            "Baixando [yellow]funcionários[/] do FIORILLI", spinner="dots"
        ):
            self._login()
            self._navigate_to_maintenance_section()
            self._navigate_to_worker_registration()
            self._wait_for_screen_to_load()
            self._select_situation()
            self._input_content()
            self._click_add_button()
            self._click_filter_button()
            self._wait_for_processing()
            self._right_click_grid()
            self._move_to_grid_option()
            self._click_grid_option()
            self._click_export_option()
            self._click_export_txt_option()
            self._wait_for_export_to_complete()
            super().close_driver()
        print("[bold green]Download de funcionários do FIORILLI concluído[/bold green]")

    def _start_absences_download(self) -> None:
        ()
        with self.console.status(
            "Baixando [yellow]afastamentos[/] do FIORILLI", spinner="dots"
        ):
            self._login()
            self._navigate_to_utilities_section()
            self._navigate_to_import_export_section()
            self._navigate_to_export_section()
            self._navigate_to_export_file_section()
            self._insert_date_for_input(name="PontoFerias2")
            self._insert_date_for_input(name="PontoAfastamentos2")
            self._close_tab()
            super().close_driver()
        print("[bold green]Download de afastamentos do FIORILLI concluído[/bold green]")

    def _login(self) -> None:
        load_dotenv()
        user = os.getenv("FIORILLI_USER")
        pwd = os.getenv("FIORILLI_PASSWORD")

        self._enter_username("O30_id-inputEl", user)
        self._enter_password("O34_id-inputEl", pwd)
        self._click_login_button()
        self._wait_for_login_to_complete()
        sleep(super().DELAY)

    def _enter_username(self, selector: str, user: str) -> None:
        super().send_keys(selector, user, selector_type=By.ID)

    def _enter_password(self, selector: str, password: str) -> None:
        super().send_keys(selector, password, selector_type=By.ID)

    def _click_login_button(self) -> None:
        super().click_element("O40_id-btnEl", selector_type=By.ID)

    def _wait_for_login_to_complete(self) -> None:
        super().wait_desappear("//*[contains(text(), 'Acessando SIP 7.5')]")

    def _navigate_to_maintenance_section(self) -> None:
        super().click_element("//*[contains(text(), '2 - Manutenção')]")

    def _navigate_to_worker_registration(self) -> None:
        super().click_element(
            "//*[contains(text(), '2.1 - Cadastro de Trabalhadores')]"
        )

    def _wait_for_screen_to_load(self) -> None:
        super().wait_desappear("//*[contains(text(), 'Abrindo a tela, aguarde...')]")

    def _select_situation(self) -> None:
        super().click_element("(//div[contains(@class, 'x-boundlist-list-ct')]//li)[1]")

    def _input_content(self) -> None:
        content_input_xpath = "//div[contains(@style, 'border:none;font-family:Segoe UI;left:0px;top:22px')]//div[contains(@data-ref, 'inputWrap')]//input[contains(@data-ref, 'inputEl') and contains(@style, 'font-family:Segoe UI') and contains(@role, 'textbox') and contains(@aria-hidden, 'false') and contains(@aria-disabled, 'false')]"
        super().select_and_send_keys(content_input_xpath, "0\\1\\2\\3\\4\\5\\6")

    def _click_add_button(self) -> None:
        plus_button_xpath = "//div[contains(@style, 'border:none;font-family:Segoe UI;left:0px;top:22px')]//span[contains(@class, 'x-btn-icon-el x-btn-icon-el-default-small fas fa-plus')]"
        super().click_element(plus_button_xpath)

    def _click_filter_button(self) -> None:
        filter_button_xpath = "//div[contains(@style, 'border:none;font-family:Segoe UI;left:0px;top:275px;width:294px;height:41px')]//*[contains(text(), 'Filtrar')]"
        super().click_element(filter_button_xpath)

    def _wait_for_processing(self) -> None:
        super().wait_desappear(
            "//div[contains(@class, 'x-mask-loading')]//div[contains(text(), 'Aguarde')]",
        )

    def _right_click_grid(self) -> None:
        grid_xpath = "//div[contains(@class, 'x-grid-item-container')]//table[contains(@style, ';width:0')]//td[contains(@style , ';font-family:Segoe UI') and not(contains(@class, 'unselectable'))][1]"
        super().right_click_element(grid_xpath)

    def _move_to_grid_option(self) -> None:
        super().move_to_element(
            "//span[contains(text(), 'Grid') and contains(@data-ref, 'textEl')]"
        )

    def _click_grid_option(self) -> None:
        super().click_element(
            "//span[contains(text(), 'Grid') and contains(@data-ref, 'textEl')]"
        )

    def _click_export_option(self) -> None:
        super().click_element(
            "//div[contains(@aria-hidden, 'false')]//div//div//div//div//div//a//span[contains(text(), 'Exportar') and contains(@class, 'x-menu-item-text x-menu-item-text-default x-menu-item-indent-no-separator x-menu-item-indent-right-arrow')]",
        )

    def _click_export_txt_option(self) -> None:
        super().click_element("//span[contains(text(), 'Exportar em TXT')]")

    def _wait_for_export_to_complete(self) -> None:
        super().wait_desappear("//*[contains(text(), 'Exportando')]")

    def _navigate_to_utilities_section(self) -> None:
        super().click_element("//span[contains(text(), '7 - Utilitários')]")

    def _navigate_to_import_export_section(self) -> None:
        for i in range(2):
            super().click_element(
                "//span[contains(text(), '7.14 - Importar/Exportar')]",
            )

    def _navigate_to_export_section(self) -> None:
        for i in range(2):
            super().click_element(
                "//span[contains(text(), '7.14.2 - Exportar')]",
            )

    def _navigate_to_export_file_section(self) -> None:
        super().click_element("//span[contains(text(), '7.14.2.2 - Exportar Arquivo')]")

    def _insert_date_for_input(self, name: str) -> None:
        self._insert_date_fiorilli_input(name=name)

    def _insert_date_fiorilli_input(self, name: str) -> None:
        self._select_input_field(name)
        self._fill_input_field()
        self._click_proceed_button()
        self._click_process_button()

    def _select_input_field(self, name: str) -> None:
        super().click_element(f"//div[contains(text(), '{name}')]")

    def _fill_input_field(self) -> None:
        today = datetime.today()
        today_str = today.strftime("%d/%m/%Y")
        two_months_ago = (today - relativedelta(months=1)).strftime("%d/%m/%Y")
        year_end = date(today.year, 12, 31).strftime("%d/%m/%Y")
        super().select_and_send_keys(
            f"//input[@value='{today_str}']",
            [
                two_months_ago,
                year_end,
            ],
        )

    def _click_proceed_button(self) -> None:
        super().click_element("//span[contains(text(), 'Prosseguir')]")

    def _click_process_button(self) -> None:
        super().click_element("//span[contains(text(), 'Processar')]")

    def _close_tab(self) -> None:
        super().click_element(
            "//div//div//div[contains(@class, 'x-panel-body x-panel-body-default x-abs-layout-ct x-panel-body-default x-panel-default-outer-border-trbl')]//div//div//div//div//div//div//div//a//span//span//span[contains(@class, 'x-btn-icon-el x-btn-icon-el-default-small x-uni-btn-icon fas fa-sign-out-alt')]",
        )

    def _click_enter_button(self) -> None:
        super().click_element("//*[contains(text(), 'Entrar')]")
