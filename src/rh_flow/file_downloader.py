import os
import threading
import time
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
    def __init__(self, working_dir):
        self.download_path = Path(working_dir / "downloads")
        self.data_path = Path(working_dir / "data")

    def run(self):
        # TODO: add multiple downloads
        # TODO: add progress panels

        fiorilli_thread = threading.Thread(target=self.fiorilli_downloads)
        ahora_thread = threading.Thread(target=self.ahgora_downloads)

        fiorilli_thread.start()
        # ahora_thread.start()

        fiorilli_thread.join()
        # ahora_thread.join()

        files = []
        while not len(files) >= 4:
            for file in self.download_path.iterdir():
                if "grid" in file.name.lower():
                    files.append(file.name.lower())
                if "pontoferias" in file.name.lower():
                    files.append(file.name.lower())
                if "pontoafastamentos" in file.name.lower():
                    files.append(file.name.lower())
                if "funcionarios" in file.name.lower():
                    files.append(file.name.lower())
                print(files)
                time.sleep(60)

        time.sleep(2**10)

    def _get_web_driver(self, app_name: str) -> webdriver.Firefox:
        print(f"--- Iniciando {app_name.upper()} Web Driver ---")
        options = webdriver.FirefoxOptions()
        # options.add_argument("-headless")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(self.download_path))

        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(DELAY)

        return driver

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
        self.click_button(driver, "O472_id-btnInnerEl")

        # cadastro btn
        self.click_button(driver, "O47E_id-textEl")

        # situacao li
        self.click_button(driver, "boundlist-1118-listEl")

        # conteudo input
        # TODO: uncomment
        # self.send_keys(driver, "OF05_id-inputEl", "\\0\\2\\3\\4\\5\\6")

        # plus btn
        self.click_button(driver, "OF31_id-btnIconEl")

        # filtrar btn
        self.click_button(driver, "OF6B_id-btnInnerEl")

        # grid tbl
        self.context_click_button(
            driver, "x-grid-item-container", selector_type=By.CLASS_NAME
        )

        # grid btn
        self.click_button(driver, "O2D5A_id-itemEl")

        # exportar btn
        self.click_button(driver, "O2D8B_id-textEl")

        # txt btn
        self.click_button(driver, "O2D97_id-textEl")

        self.wait_desappear(driver, "O34E7_id")

    def _download_fiorilli_absences(self, driver) -> None:
        # utilidades btn
        self.click_button(driver, "OAF7_id-btnInnerEl")

        # importar exportar btn
        self.click_button(driver, "OB7F_id-textEl")

        # exportar btn
        self.click_button(driver, "OBA6_id-textEl")

        # exportar arquivo btn
        self.click_button(driver, "OBB7_id-textEl")

        # PontoFerias2 li
        self._insert_date_fiorilli_input(
            driver, name="PontoFerias2", id="OE22_id-inputEl"
        )

        # PontoAfastamentos2 li
        self._insert_date_fiorilli_input(
            driver, name="PontoAfastamentos2", id="OE90_id-inputEl"
        )

    def _insert_date_fiorilli_input(self, driver, name: str, id: str):
        # inicio input
        self.click_button(
            driver, f"//*[contains(text(), '{name}')]", selector_type=By.XPATH
        )
        # inicio input
        self.select_and_send_keys(driver, id, "01/01/2025")

        # prosseguir btn
        self.click_button(driver, "ODEE_id-btnEl")

        # processar btn
        self.click_button(driver, "OD1F_id-btnInnerEl")

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
            "//*[contains(data-testid(), 'CloudDownloadIcon')]",
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
