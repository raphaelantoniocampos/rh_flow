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

MAX_TRIES = 200
DELAY = 0.25
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
        # ahora_thread = threading.Thread(target=self.ahgora_downloads)

        fiorilli_thread.start()
        # ahora_thread.start()

        fiorilli_thread.join()
        # ahora_thread.join()

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
        self.send_keys(driver, "O30_id-inputEl", user)

        # password input
        self.send_keys(driver, "O34_id-inputEl", pwd)

        # login btn
        self.click_button(driver, "O40_id-btnEl")

        self._download_fiorilli_employees(driver)
        self._download_fiorilli_absences(driver)

    def _download_fiorilli_employees(self, driver) -> None:
        # manutencao btn
        self.click_button(
            driver, "//*[contains(text(), '2 - Manutenção')]", selector_type=By.XPATH
        )
        # cadastro btn
        self.click_button(
            driver,
            "//*[contains(text(), '2.1 - Cadastro de Trabalhadores')]",
            selector_type=By.XPATH,
        )

        # situacao li
        # self.click_button(
        #     driver, "//*[contains(text(), 'Situação ')]", selector_type=By.XPATH
        # )

        # conteudo input
        self.send_keys(
            driver,
            "//*[@data-ref='inputEl']",
            "\\0\\2\\3\\4\\5\\6",
            selector_type=By.XPATH,
        )
        # plus btn
        self.click_button(driver, "//*[@data-ref='btnIconEl']", selector_type=By.XPATH)

        # filtrar btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Filtrar')]",
            selector_type=By.XPATH,
        )

        # grid tbl
        self.context_click_button(
            driver, "x-grid-item-container", selector_type=By.CLASS_NAME
        )

        # grid btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Grid')]",
            selector_type=By.XPATH,
        )

        # exportar btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Exportar')]",
            selector_type=By.XPATH,
        )

        # txt btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Exportar em TXT')]",
            selector_type=By.XPATH,
        )
        # exportando
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Exportando')]",
            selector_type=By.XPATH,
        )

    def _download_fiorilli_absences(self, driver) -> None:
        # utilitarios btn
        self.click_button(
            driver, "//*[contains(text(), '7 - Utilitários')]", selector_type=By.XPATH
        )

        # importar exportar btn
        self.click_button(
            driver,
            "//*[contains(text(), '7.14 - Importar/Exportar')]",
            selector_type=By.XPATH,
        )

        # exportar btn
        self.click_button(
            driver, "//*[contains(text(), '7.14.2 - Exportar')]", selector_type=By.XPATH
        )
        # exportar arquivo btn
        self.click_button(
            driver,
            "//*[contains(text(), '7.14.2.2 - Exportar Arquivo')]",
            selector_type=By.XPATH,
        )

        # PontoFerias2 li
        self._insert_date_fiorilli_input(driver, name="PontoFerias2")

        # PontoAfastamentos2 li
        self._insert_date_fiorilli_input(driver, name="PontoAfastamentos2")

    def _insert_date_fiorilli_input(self, driver, name: str):
        first_day_str, today_str = self._get_today_date()

        # inicio input
        self.click_button(
            driver, f"//*[contains(text(), '{name}')]", selector_type=By.XPATH
        )
        # inicio input
        self.select_and_send_keys(
            driver,
            f"//*[@value='{today_str}'][1]",
            first_day_str,
            selector_type=By.XPATH,
        )
        # prosseguir btn
        self.click_button(
            driver, "//*[contains(text(), 'Prosseguir')]", selector_type=By.XPATH
        )
        # processar btn
        self.click_button(
            driver, "//*[contains(text(), 'Processar')]", selector_type=By.XPATH
        )

    def ahgora_downloads(self):
        driver = self._get_web_driver("ahgora")
        driver.get("https://app.ahgora.com.br/")
        load_dotenv()

        user = os.getenv("AHGORA_USER")
        pwd = os.getenv("AHGORA_PASSWORD")
        company = os.getenv("AHGORA_COMPANY")

        # email input
        self.send_keys(driver, "email", user)

        # entrar btn
        self.click_button(
            driver, "//*[contains(text(), 'Entrar')]", selector_type=By.XPATH
        )

        # password input
        self.send_keys(driver, "password", pwd)

        self.click_button(
            driver, "//*[contains(text(), 'Entrar')]", selector_type=By.XPATH
        )

        # company input
        self.click_button(
            driver, f"//*[contains(text(), '{company}')]", selector_type=By.XPATH
        )

        self.click_button(driver, "buttonAdjustPunch")
        self._download_ahgora_employees(driver)
        self._download_ahgora_absences(driver)

    def _download_ahgora_employees(self, driver):
        driver.get("https://app.ahgora.com.br/funcionarios")

        # mostrar desligados btn
        self.click_button(driver, "filtro_demitido")

        # plus btn
        self.click_button(driver, "mais")

        # exportar csv
        self.click_button(driver, "arquivo_csv")

    def _download_ahgora_absences(self, driver):
        driver.get("https://app.ahgora.com.br/relatorios")

        # gerar novos relatorios btn
        self.click_button(
            driver,
            "//*[contains(text(), 'Gerar novos relatórios')]",
            selector_type=By.XPATH,
        )

        # selecione btn
        self.send_keys(
            driver,
            "id-autocomplete-multiple-Selecione um relatório (obrigatório)",
            "Afastamentos",
        )

        # afastamentos li
        self.click_button(
            driver, "//*[contains(text(), 'Afastamentos')]", selector_type=By.XPATH
        )

        # panel out
        self.click_button(driver, "tabpanel-0")

        # date btn
        self.click_button(
            driver, "_2t8pekO7_rn5BQDaNUsF79", selector_type=By.CLASS_NAME
        )

        # janeiro
        self.click_button(
            driver, "//*[contains(text(), 'janeiro')]", selector_type=By.XPATH
        )

        # gerar btn
        self.click_button(
            driver, "//*[contains(text(), 'Gerar')]", selector_type=By.XPATH
        )

        # gerando relatorio progress bar
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Estamos gerando seus relatórios...')]",
            selector_type=By.XPATH,
        )
        # relatorio btn
        self.click_button(
            driver,
            "//a[contains(@href,'/relatorios/afastamentos')]",
            selector_type=By.XPATH,
        )

        # formato do resultado btn
        self.click_button(driver, "generateReportFilter")

        # matricula option
        self.click_button(
            driver, "//*[contains(text(), 'Agrupado por Mat')]", selector_type=By.XPATH
        )

        # date
        self.send_keys(driver, "filterByStartDate", "01/01")

        # gerar relatorio
        self.click_button(driver, "generateReport")

        # download icon
        self.click_button(
            driver,
            "//*[@data-testid='CloudDownloadIcon']",
            selector_type=By.XPATH,
        )

        # baixar em csv btn
        self.click_button(
            driver, "//*[contains(text(), 'Baixar em .csv')]", selector_type=By.XPATH
        )

    def click_button(
        self,
        driver,
        selector,
        selector_type=By.ID,
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
        selector_type=By.ID,
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
        selector_type=By.ID,
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
        selector_type=By.ID,
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
        selector_type=By.ID,
        delay=DELAY,
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
        selector_type=By.ID,
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
        selector_type=By.ID,
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
        selector_type=By.ID,
    ):
        ActionChains(driver).context_click(
            driver.find_element(selector_type, selector)
        ).perform()

    def _select_and_send_keys_helper(
        self,
        driver,
        selector,
        keys,
        selector_type=By.ID,
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
        selector_type=By.ID,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        WebDriverWait(driver, 60).until(
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
