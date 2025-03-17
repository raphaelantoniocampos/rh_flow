from core_browser import CoreBrowser

class FiorilliBrowser(CoreBrowser):
    def __init__(self, base_dir_path, config: Config):
        self.downloads_dir_path = Path(base_dir_path / "downloads")
        self.data_dir_path = Path(base_dir_path / "data")

    def run(self):
        # TODO: add progress panels later
        downloaded_files = []

        fiorilli_thread = threading.Thread(target=self.fiorilli_downloads)
        ahgora_thread = threading.Thread(target=self.ahgora_downloads)

        fiorilli_thread.start()
        ahgora_thread.start()

        fiorilli_thread.join()
        ahgora_thread.join()

        self._wait_for_downloads_to_complete(downloaded_files)
        self._move_files_to_data_dir()

    def _wait_for_downloads_to_complete(self, downloaded_files):
        while len(downloaded_files) < 4:
            for file in self.downloads_dir_path.iterdir():
                if any(
                    keyword in file.name.lower()
                    for keyword in ["grid", "pontoferias", "pontoafast", "funcionarios"]
                ):
                    if file.name not in downloaded_files:
                        downloaded_files.append(file.name)
            time.sleep(30)

    def _move_files_to_data_dir(self):
        Config.move_files_from_downloads_dir(
            self.downloads_dir_path, self.data_dir_path
        )


    def fiorilli_downloads(self) -> None:
        print("[bold yellow]--- Iniciando Downloads FIORILLI ---[/bold yellow]")
        driver = self._initialize_driver_and_navigate(
            "https://pompeu-pm-sip.sigmix.net/sip/"
        )
        self._login_to_fiorilli(driver)
        self._download_fiorilli_data(driver)
        self._close_driver(driver)
        print("[bold green]--- Downloads FIORILLI Concluídos ---[/bold green]")

    def ahgora_downloads(self) -> None:
        print("[bold yellow]--- Iniciando Downloads AHGORA ---[/bold yellow]")
        driver = self._initialize_driver_and_navigate("https://app.ahgora.com.br/")
        self._login_to_ahgora(driver)
        self._close_bannter(driver)
        self._download_ahgora_data(driver)
        self._close_driver(driver)
        print("[bold green]--- Downloads AHGORA Concluídos ---[/bold green]")

    def _initialize_driver_and_navigate(self, url):
        driver = self._get_web_driver()
        driver.get(url)
        load_dotenv()
        return driver

    def _login_to_fiorilli(self, driver) -> None:
        print("Fazendo [yellow]login[/] no FIORILLI")
        user = os.getenv("FIORILLI_USER")
        pwd = os.getenv("FIORILLI_PASSWORD")

        self._enter_username(driver, "O30_id-inputEl", user)
        self._enter_password(driver, "O34_id-inputEl", pwd)
        self._click_login_button(driver)
        self._wait_for_login_to_complete(driver)

    def _click_login_button(self, driver) -> None:
        self.click_element(driver, "O40_id-btnEl", selector_type=By.ID)

    def _wait_for_login_to_complete(self, driver) -> None:
        self.wait_desappear(driver, "//*[contains(text(), 'Acessando SIP 7.5')]")

    def _download_fiorilli_data(self, driver) -> None:
        self._download_fiorilli_absences(driver)
        time.sleep(DELAY)
        self._download_fiorilli_employees(driver)
        time.sleep(DELAY)

    def _close_driver(self, driver) -> None:
        driver.quit()

    def _download_fiorilli_employees(self, driver) -> None:
        print("Baixando dados de [yellow]funcionários[/] do FIORILLI")
        self._navigate_to_maintenance_section(driver)
        self._navigate_to_worker_registration(driver)
        self._wait_for_screen_to_load(driver)
        self._select_situation(driver)
        self._input_content(driver)
        self._click_add_button(driver)
        self._click_filter_button(driver)
        self._wait_for_processing(driver)
        self._right_click_grid(driver)
        self._move_to_grid_option(driver)
        self._click_grid_option(driver)
        self._click_export_option(driver)
        self._click_export_txt_option(driver)
        self._wait_for_export_to_complete(driver)
        print("[green]Download de dados de funcionários do FIORILLI concluído[/]")

    def _navigate_to_maintenance_section(self, driver) -> None:
        self.click_element(driver, "//*[contains(text(), '2 - Manutenção')]")

    def _navigate_to_worker_registration(self, driver) -> None:
        self.click_element(
            driver, "//*[contains(text(), '2.1 - Cadastro de Trabalhadores')]"
        )

    def _wait_for_screen_to_load(self, driver) -> None:
        self.wait_desappear(
            driver, "//*[contains(text(), 'Abrindo a tela, aguarde...')]"
        )

    def _select_situation(self, driver) -> None:
        self.click_element(
            driver, "(//div[contains(@class, 'x-boundlist-list-ct')]//li)[1]"
        )

    def _input_content(self, driver) -> None:
        content_input_xpath = "//div[contains(@style, 'border:none;font-family:Segoe UI;left:0px;top:22px')]//div[contains(@data-ref, 'inputWrap')]//input[contains(@data-ref, 'inputEl') and contains(@style, 'font-family:Segoe UI') and contains(@role, 'textbox') and contains(@aria-hidden, 'false') and contains(@aria-disabled, 'false')]"
        self.select_and_send_keys(driver, content_input_xpath, "0\\1\\2\\3\\4\\5\\6")

    def _click_add_button(self, driver) -> None:
        plus_button_xpath = "//div[contains(@style, 'border:none;font-family:Segoe UI;left:0px;top:22px')]//span[contains(@class, 'x-btn-icon-el x-btn-icon-el-default-small fas fa-plus')]"
        self.click_element(driver, plus_button_xpath)

    def _click_filter_button(self, driver) -> None:
        filter_button_xpath = "//div[contains(@style, 'border:none;font-family:Segoe UI;left:0px;top:275px;width:294px;height:41px')]//*[contains(text(), 'Filtrar')]"
        self.click_element(driver, filter_button_xpath)

    def _wait_for_processing(self, driver) -> None:
        self.wait_desappear(
            driver,
            "//div[contains(@class, 'x-mask-loading')]//div[contains(text(), 'Aguarde')]",
        )

    def _right_click_grid(self, driver) -> None:
        grid_xpath = "//div[contains(@class, 'x-grid-item-container')]//table[contains(@style, ';width:0')]//td[contains(@style , ';font-family:Segoe UI') and not(contains(@class, 'unselectable'))][1]"
        self.right_click_element(driver, grid_xpath)

    def _move_to_grid_option(self, driver) -> None:
        self.move_to_element(
            driver, "//span[contains(text(), 'Grid') and contains(@data-ref, 'textEl')]"
        )

    def _click_grid_option(self, driver) -> None:
        self.click_element(
            driver, "//span[contains(text(), 'Grid') and contains(@data-ref, 'textEl')]"
        )

    def _click_export_option(self, driver) -> None:
        self.click_element(
            driver,
            "//div[contains(@aria-hidden, 'false')]//div//div//div//div//div//a//span[contains(text(), 'Exportar') and contains(@class, 'x-menu-item-text x-menu-item-text-default x-menu-item-indent-no-separator x-menu-item-indent-right-arrow')]",
        )

    def _click_export_txt_option(self, driver) -> None:
        self.click_element(driver, "//span[contains(text(), 'Exportar em TXT')]")

    def _wait_for_export_to_complete(self, driver) -> None:
        self.wait_desappear(driver, "//*[contains(text(), 'Exportando')]")

    def _download_fiorilli_absences(self, driver) -> None:
        print("Baixando dados de [yellow]afastamentos[/] do FIORILLI")
        self._navigate_to_utilities_section(driver)
        self._navigate_to_import_export_section(driver)
        self._navigate_to_export_section(driver)
        self._navigate_to_export_file_section(driver)
        self._insert_date_for_input(driver, name="PontoFerias2")
        self._insert_date_for_input(driver, name="PontoAfastamentos2")
        self._close_tab(driver)
        print("[green]Download de dados de afastamentos do FIORILLI concluído[/]")

    def _navigate_to_utilities_section(self, driver) -> None:
        self.click_element(driver, "//span[contains(text(), '7 - Utilitários')]")

    def _navigate_to_import_export_section(self, driver) -> None:
        self._retry_func(
            lambda: self.click_element(
                driver,
                "//span[contains(text(), '7.14 - Importar/Exportar')]",
            ),
            2,
        )

    def _navigate_to_export_section(self, driver) -> None:
        self._retry_func(
            lambda: self.click_element(
                driver,
                "//span[contains(text(), '7.14.2 - Exportar')]",
            ),
            2,
        )

    def _navigate_to_export_file_section(self, driver) -> None:
        self.click_element(
            driver, "//span[contains(text(), '7.14.2.2 - Exportar Arquivo')]"
        )

    def _insert_date_for_input(self, driver, name: str) -> None:
        self._insert_date_fiorilli_input(driver, name=name)

    def _insert_date_fiorilli_input(self, driver, name: str) -> None:
        self._select_input_field(driver, name)
        self._fill_input_field(driver)
        self._click_proceed_button(driver)
        self._click_process_button(driver)

    def _select_input_field(self, driver, name: str) -> None:
        self.click_element(driver, f"//div[contains(text(), '{name}')]")

    def _fill_input_field(self, driver) -> None:
        today = datetime.today()
        today_str = today.strftime("%d/%m/%Y")
        self.select_and_send_keys(
            driver,
            f"//input[@value='{today_str}']",
            [
                date(today.year, 1, 1).strftime("%d/%m/%Y"),
                date(today.year, 12, 31).strftime("%d/%m/%Y"),
            ],
        )

    def _click_proceed_button(self, driver) -> None:
        self.click_element(driver, "//span[contains(text(), 'Prosseguir')]")

    def _click_process_button(self, driver) -> None:
        self.click_element(driver, "//span[contains(text(), 'Processar')]")

    def _login_to_ahgora(self, driver) -> None:
        print("Fazendo [yellow]login[/] no AHGORA")
        user = os.getenv("AHGORA_USER")
        pwd = os.getenv("AHGORA_PASSWORD")

        self._enter_username(driver, "email", user)
        self._click_enter_button(driver)
        self._enter_password(driver, "password", pwd)
        self._click_enter_button(driver)
        self._select_company(driver)

    def _close_tab(self, driver) -> None:
        self.click_element(
            driver,
            "//div//div//div[contains(@class, 'x-panel-body x-panel-body-default x-abs-layout-ct x-panel-body-default x-panel-default-outer-border-trbl')]//div//div//div//div//div//div//div//a//span//span//span[contains(@class, 'x-btn-icon-el x-btn-icon-el-default-small x-uni-btn-icon fas fa-sign-out-alt')]",
        )

    def _enter_username(self, driver, selector: str, email: str) -> None:
        self.send_keys(driver, selector, email, selector_type=By.ID)

    def _enter_password(self, driver, selector: str, password: str) -> None:
        self.send_keys(driver, selector, password, selector_type=By.ID)

    def _click_enter_button(self, driver) -> None:
        self.click_element(driver, "//*[contains(text(), 'Entrar')]")

    def _select_company(self, driver) -> None:
        company = os.getenv("AHGORA_COMPANY")
        self.click_element(driver, f"//*[contains(text(), '{company}')]")

    def _close_bannter(self, driver) -> None:
        self.click_element(driver, "buttonAdjustPunch", selector_type=By.ID)

    def _download_ahgora_data(self, driver) -> None:
        self._download_ahgora_employees(driver)
        # self._download_ahgora_absences(driver)
        time.sleep(30)
        print("[green]Download de dados de funcionários do AHGORA concluído[/]")

    def _close_driver(self, driver) -> None:
        driver.quit()

    def _download_ahgora_employees(self, driver) -> None:
        print("Baixando dados de [yellow]funcionários[/] do AHGORA")
        driver.get("https://app.ahgora.com.br/funcionarios")
        self._show_dismissed_employees(driver)
        self._click_plus_button(driver)
        self._export_to_csv(driver)

    def _show_dismissed_employees(self, driver) -> None:
        self.click_element(driver, "filtro_demitido", selector_type=By.ID)

    def _click_plus_button(self, driver) -> None:
        self.click_element(driver, "mais", selector_type=By.ID)

    def _export_to_csv(self, driver) -> None:
        self.click_element(driver, "arquivo_csv", selector_type=By.ID)

    def _download_ahgora_absences(self, driver) -> None:
        driver.get("https://app.ahgora.com.br/relatorios")
        self._generate_new_reports(driver)
        self._select_absences_report(driver)
        self._select_date_range(driver)
        self._generate_report(driver)
        self._download_report_as_csv(driver)

    def _generate_new_reports(self, driver) -> None:
        self.click_element(driver, "//*[contains(text(), 'Gerar novos relatórios')]")

    def _select_absences_report(self, driver) -> None:
        self.send_keys(
            driver,
            "id-autocomplete-multiple-Selecione um relatório (obrigatório)",
            "Afastamentos",
            selector_type=By.ID,
        )
        self.click_element(driver, "//*[contains(text(), 'Afastamentos')]")

    def _select_date_range(self, driver) -> None:
        self.click_element(driver, "tabpanel-0", selector_type=By.ID)
        self.click_element(
            driver, "_2t8pekO7_rn5BQDaNUsF79", selector_type=By.CLASS_NAME
        )
        self.click_element(driver, "//*[contains(text(), 'janeiro')]")

    def _generate_report(self, driver) -> None:
        self.click_element(driver, "//*[contains(text(), 'Gerar')]")
        time.sleep(120)
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Estamos gerando seus relatórios...')]",
            delay=10,
        )
        self.click_element(driver, "//a[contains(text(),'Afastamentos')]")

    def _download_report_as_csv(self, driver) -> None:
        self.click_element(
            driver, "//div[contains(@comp-textselect, 'Formato do resultado')]"
        )
        self.click_element(driver, "//option[contains(@value, 'agrupadoM')]")
        self.send_keys(driver, "//input[contains(@id, 'filterByStartDate')]", "01/01")
        self.click_element(driver, "//button[contains(@id, 'generateReport')]")
        self.click_element(driver, "//*[@data-testid='CloudDownloadIcon']")
        self.click_element(driver, "//li[contains(text(), 'Baixar em .csv')]")
