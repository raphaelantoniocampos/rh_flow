import os
import threading
import time
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from rich import print
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import Config

MAX_TRIES = 500
DELAY = 0.1
IGNORED_EXCEPTIONS = (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    StaleElementReferenceException,
)


class FileDownloader:
    def __init__(self, base_dir, config: Config):
        self.download_path = Path(base_dir / "downloads")
        self.data_path = Path(base_dir / "data")

    def run(self):
        # TODO: add progress panels
        downloaded_files = []

        fiorilli_thread = threading.Thread(target=self.fiorilli_downloads)
        ahora_thread = threading.Thread(target=self.ahgora_downloads)

        # fiorilli_thread.start()
        ahora_thread.start()

        # fiorilli_thread.join()
        ahora_thread.join()

        while not len(downloaded_files) >= 4:
            for file in self.download_path.iterdir():
                if "grid" in file.name.lower():
                    if file.name not in downloaded_files:
                        downloaded_files.append(file.name)
                if "pontoferias" in file.name.lower():
                    if file.name not in downloaded_files:
                        downloaded_files.append(file.name)
                if "pontoafast" in file.name.lower():
                    if file.name not in downloaded_files:
                        downloaded_files.append(file.name)
                if "funcionarios" in file.name.lower():
                    if file.name not in downloaded_files:
                        downloaded_files.append(file.name)
            time.sleep(30)

        print(downloaded_files)
        self.config.move_files_from_downloads_dir

    def _get_web_driver(self, app_name: str) -> webdriver.Firefox:
        print(f"--- Iniciando {app_name.upper()} Web Driver ---")
        options = webdriver.FirefoxOptions()
        # TODO: uncomment headless
        # options.add_argument("-headless")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(self.download_path))

        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(DELAY)

        return driver

    def _get_today_date(self) -> (str, str):
        today = datetime.today()

        today_str = today.strftime("%d/%m/%Y")

        first_day_str = date(today.year, 1, 1).strftime("%d/%m/%Y")

        return first_day_str, today_str

    def fiorilli_downloads(self):
        driver = self._get_web_driver("fiorilli")
        driver.get("https://pompeu-pm-sip.sigmix.net/sip/")
        load_dotenv()

        user = os.getenv("FIORILLI_USER")
        pwd = os.getenv("FIORILLI_PASSWORD")

        # user input
        self.send_keys(driver, "O30_id-inputEl", user, selector_type=By.ID)

        # password input
        self.send_keys(driver, "O34_id-inputEl", pwd, selector_type=By.ID)

        # login btn
        self.click_button(driver, "O40_id-btnEl", selector_type=By.ID)

        # wait acessando sip
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Acessando SIP 7.5')]",
        )

        self._download_fiorilli_employees(driver)
        self._download_fiorilli_absences(driver)

    def _download_fiorilli_employees(self, driver) -> None:
        # manutencao btn
        self.click_button(driver, "//*[contains(text(), '2 - Manutenção')]")
        # cadastro btn
        self.click_button(
            driver,
            "//*[contains(text(), '2.1 - Cadastro de Trabalhadores')]",
        )

        # wait abrindo a tela
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Abrindo a tela, aguarde...')]",
        )

        # situacao li
        self.click_button(
            driver,
            "(//div[contains(@class, 'x-boundlist-list-ct')]//li)[1]",
        )

        # search btn
        self.click_button(
            driver,
            "x-btn-icon-el x-btn-icon-el-default-small fas fa-search",
            selector_type=By.CLASS_NAME
        )

        # selecionar todos checkbox
        self.click_button(
            driver,
            "//*[contains(text(), 'Selecionar Todos')]",
        )

        # selecionar btn
        self.click_button(
            driver,
            "x-btn-inner x-btn-inner-default-small",
            selector_type=By.CLASS_NAME
        )

        # conteudo input
        # self.send_keys(
        #     driver,
        #     "//input["
        #     "contains(@class, 'x-form-field') and "
        #     "contains(@class, 'x-form-text') and "
        #     "contains(@class, 'x-form-text-default') and "
        #     "contains(@class, 'x-form-empty-field') and "
        #     "contains(@class, 'x-form-empty-field-default')"
        #     "]",
        #     "\\0\\2\\3\\4\\5\\6",
        # )

        # plus btn
        self.click_button(driver, "x-btn-icon-el x-btn-icon-el-default-small fas fa-plus", selector_type=By.CLASS_NAME)

        # filtrar btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Filtrar')]",
        )

        # grid tbl
        self.context_click_button(
            driver, "x-grid-item-container", selector_type=By.CLASS_NAME
        )

        # grid btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Grid')]",
        )

        # exportar btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Exportar')]",
        )

        # txt btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Exportar em TXT')]",
        )
        # exportando
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Exportando')]",
        )

    def _download_fiorilli_absences(self, driver) -> None:
        # utilitarios btn
        self.click_button(driver, "//*[contains(text(), '7 - Utilitários')]")

        # importar exportar btn
        self.click_button(
            driver,
            "//*[contains(text(), '7.14 - Importar/Exportar')]",
        )

        # exportar btn
        self.click_button(driver, "//*[contains(text(), '7.14.2 - Exportar')]")
        # exportar arquivo btn
        self.click_button(
            driver,
            "//*[contains(text(), '7.14.2.2 - Exportar Arquivo')]",
        )

        # PontoFerias2 li
        self._insert_date_fiorilli_input(driver, name="PontoFerias2")

        # PontoAfastamentos2 li
        self._insert_date_fiorilli_input(driver, name="PontoAfastamentos2")

    def _insert_date_fiorilli_input(self, driver, name: str):
        first_day_str, today_str = self._get_today_date()

        # inicio input
        self.click_button(driver, f"//*[contains(text(), '{name}')]")
        # inicio input
        self.select_and_send_keys(
            driver,
            f"//*[@value='{today_str}'][1]",
            first_day_str,
        )
        # prosseguir btn
        self.click_button(driver, "//*[contains(text(), 'Prosseguir')]")
        # processar btn
        self.click_button(driver, "//*[contains(text(), 'Processar')]")

    def ahgora_downloads(self):
        driver = self._get_web_driver("ahgora")
        driver.get("https://app.ahgora.com.br/")
        load_dotenv()

        user = os.getenv("AHGORA_USER")
        pwd = os.getenv("AHGORA_PASSWORD")
        company = os.getenv("AHGORA_COMPANY")

        # email input
        self.send_keys(driver, "email", user, selector_type=By.ID)

        # entrar btn
        self.click_button(driver, "//*[contains(text(), 'Entrar')]")

        # password input
        self.send_keys(driver, "password", pwd, selector_type=By.ID)

        self.click_button(driver, "//*[contains(text(), 'Entrar')]")

        # company input
        self.click_button(driver, f"//*[contains(text(), '{company}')]")

        self.click_button(driver, "buttonAdjustPunch", selector_type=By.ID)
        self._download_ahgora_employees(driver)
        self._download_ahgora_absences(driver)

    def _download_ahgora_employees(self, driver):
        driver.get("https://app.ahgora.com.br/funcionarios")

        # mostrar desligados btn
        self.click_button(driver, "filtro_demitido", selector_type=By.ID)

        # plus btn
        self.click_button(driver, "mais", selector_type=By.ID)

        # exportar csv
        self.click_button(driver, "arquivo_csv", selector_type=By.ID)

    def _download_ahgora_absences(self, driver):
        driver.get("https://app.ahgora.com.br/relatorios")

        # gerar novos relatorios btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Gerar novos relatórios')]",
        )

        # selecione btn
        self.send_keys(
            driver,
            "id-autocomplete-multiple-Selecione um relatório (obrigatório)",
            "Afastamentos",
            selector_type=By.ID,
        )

        # afastamentos li
        self.click_button(driver, "//*[contains(text(), 'Afastamentos')]")

        # panel out
        self.click_button(driver, "tabpanel-0", selector_type=By.ID)

        # date btn
        self.click_button(
            driver, "_2t8pekO7_rn5BQDaNUsF79", selector_type=By.CLASS_NAME
        )

        # janeiro
        self.click_button(driver, "//*[contains(text(), 'janeiro')]")

        # gerar btn
        self.click_button(driver, "//*[contains(text(), 'Gerar')]")

        # gerando relatorio progress bar
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Estamos gerando seus relatórios...')]",
            delay=240
        )
        # relatorio btn
        self.click_button(
            driver,
            "//a[contains(@href,'/relatorios/afastamentos')]",
        )

        # formato do resultado btn
        self.click_button(driver, "generateReportFilter", selector_type=By.ID)

        # matricula option
        self.click_button(driver, "//*[contains(text(), 'Agrupado por Mat')]")

        # date
        self.send_keys(driver, "filterByStartDate", "01/01", selector_type=By.ID)

        # gerar relatorio
        self.click_button(driver, "generateReport", selector_type=By.ID)

        # download icon
        self.click_button(
            driver,
            "//*[@data-testid='CloudDownloadIcon']",
        )

        # baixar em csv btn
        self.click_button(driver, "//*[contains(text(), 'Baixar em .csv')]")

    def click_button(
        self,
        driver,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        time.sleep(DELAY)
        self._retry_func(
            lambda: self._click_button_helper(
                driver, selector, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def send_keys(
        self,
        driver,
        selector,
        keys,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        time.sleep(DELAY)
        self._retry_func(
            lambda: self._send_keys_helper(
                driver, selector, keys, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def context_click_button(
        self,
        driver,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        max_tries=MAX_TRIES,
    ):
        time.sleep(DELAY)
        self._retry_func(
            lambda: self._context_click_button_helper(driver, selector, selector_type),
            max_tries,
        )

    def select_and_send_keys(
        self,
        driver,
        selector,
        keys,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        time.sleep(DELAY)
        self._retry_func(
            lambda: self._select_and_send_keys_helper(
                driver, selector, keys, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def wait_desappear(
        self,
        driver,
        selector,
        selector_type=By.XPATH,
        delay=30,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        time.sleep(DELAY)
        return self._retry_func(
            lambda: self._wait_desappear_helper(
                driver, selector, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def _click_button_helper(
        self,
        driver,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((selector_type, selector))
        ).click()

    def _send_keys_helper(
        self,
        driver,
        selector,
        keys,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((selector_type, selector))
        ).send_keys(keys)

    def _context_click_button_helper(
        self,
        driver,
        selector,
        selector_type=By.XPATH,
    ):
        ActionChains(driver).context_click(
            driver.find_element(selector_type, selector)
        ).perform()

    def _select_and_send_keys_helper(
        self,
        driver,
        selector,
        keys,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        ActionChains(driver).context_click(
            WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(
                EC.presence_of_element_located((selector_type, selector))
            )
        ).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(
            keys
        ).perform()

    def _wait_desappear_helper(
        self,
        driver,
        selector,
        selector_type=By.XPATH,
        delay=30,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        WebDriverWait(driver, delay).until(
            EC.invisibility_of_element_located((selector_type, selector))
        )

    def _retry_func(self, func, max_tries=MAX_TRIES):
        for i in range(max_tries):
            try:
                return func()
            except Exception as e:
                time.sleep(DELAY)
                if i >= max_tries - 1:
                    raise e
