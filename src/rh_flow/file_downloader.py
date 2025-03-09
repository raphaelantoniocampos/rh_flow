import os
import threading
import time
from datetime import date, datetime
from pathlib import Path

from config import Config
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

MAX_TRIES = 100
DELAY = 0.5
IGNORED_EXCEPTIONS = (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    StaleElementReferenceException,
)


class FileDownloader:
    def __init__(self, base_dir_path, config: Config):
        self.downloads_dir_path = Path(base_dir_path / "downloads")
        self.data_dir_path = Path(base_dir_path / "data")

    def run(self):
        # TODO: add progress panels
        downloaded_files = []

        fiorilli_thread = threading.Thread(target=self.fiorilli_downloads)
        ahgora_thread = threading.Thread(target=self.ahgora_downloads)

        # fiorilli_thread.start()
        ahgora_thread.start()

        # fiorilli_thread.join()
        ahgora_thread.join()

        while not len(downloaded_files) >= 4:
            for file in self.downloads_dir_path.iterdir():
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

        Config().move_files_from_downloads_dir(
            self.downloads_dir_path, self.data_dir_path
        )

    def _get_web_driver(self, app_name: str) -> webdriver.Firefox:
        print(f"--- Iniciando {app_name.upper()} Web Driver ---")
        options = webdriver.FirefoxOptions()
        # TODO: uncomment headless
        # options.add_argument("-headless")
        options.set_preference(
            "browser.download.folderList",
            2,
        )
        options.set_preference(
            "browser.download.dir",
            str(self.downloads_dir_path),
        )

        driver = webdriver.Firefox(
            options=options,
        )
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
        self.send_keys(
            driver,
            "O30_id-inputEl",
            user,
            selector_type=By.ID,
        )

        # password input
        self.send_keys(
            driver,
            "O34_id-inputEl",
            pwd,
            selector_type=By.ID,
        )

        # login btn
        self.click_element(
            driver,
            "O40_id-btnEl",
            selector_type=By.ID,
        )

        # wait acessando sip
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Acessando SIP 7.5')]",
        )

        self._download_fiorilli_employees(driver)
        self._download_fiorilli_absences(driver)

        time.sleep(1)
        driver.quit()

    def _download_fiorilli_employees(self, driver) -> None:
        # manutencao btn
        self.click_element(
            driver,
            "//*[contains(text(), '2 - Manutenção')]",
        )
        # cadastro btn
        self.click_element(
            driver,
            "//*[contains(text(), '2.1 - Cadastro de Trabalhadores')]",
        )

        # wait abrindo a tela
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Abrindo a tela, aguarde...')]",
        )

        # situacao li
        self.click_element(
            driver,
            "(//div[contains(@class, 'x-boundlist-list-ct')]//li)[1]",
        )

        # conteudo input
        self.select_and_send_keys(
            driver,
            "//div[contains(@style, 'border:none;font-family:Segoe UI;left:0px;top:22px')]//div[contains(@data-ref, 'inputWrap')]//input[contains(@data-ref, 'inputEl') and contains(@style, 'font-family:Segoe UI') and contains(@role, 'textbox') and contains(@aria-hidden, 'false') and contains(@aria-disabled, 'false')]",
            "0\\1\\2\\3\\4\\5\\6",
        )

        # plus btn
        self.click_element(
            driver,
            "//div[contains(@style, 'border:none;font-family:Segoe UI;left:0px;top:22px')]//span[contains(@class, 'x-btn-icon-el x-btn-icon-el-default-small fas fa-plus')]",
        )

        # filtrar btn
        self.click_element(
            driver,
            "//div[contains(@style, 'border:none;font-family:Segoe UI;left:0px;top:275px;width:294px;height:41px')]//*[contains(text(), 'Filtrar')]",
        )

        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Aguarde')]",
        )

        # grid tbl
        self.right_click_element(
            driver,
            "//div[contains(@class, 'x-grid-item-container')]",
        )

        # grid btn
        self.click_element(
            driver,
            "//span[contains(text(), 'Grid') and contains(@data-ref, 'textEl')]",
        )

        # exportar btn
        self.click_element(
            driver,
            "//span[contains(text(), 'Exportar') and contains(@class, 'item-indent-right-arrow')]",
        )

        # txt btn
        self.click_element(
            driver,
            "//span[contains(text(), 'Exportar em TXT')]",
        )
        # exportando
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Exportando')]",
        )

    def _download_fiorilli_absences(self, driver) -> None:
        # utilitarios btn
        self.click_element(
            driver,
            "//span[contains(text(), '7 - Utilitários')]",
        )

        # importar exportar btn
        self._retry_func(
            lambda: self.click_element(
                driver,
                "//span[contains(text(), '7.14 - Importar/Exportar')]",
            ),
            2,
        )

        # exportar btn
        self._retry_func(
            lambda: self.click_element(
                driver,
                "//span[contains(text(), '7.14.2 - Exportar')]",
            ),
            2,
        )

        # exportar arquivo btn
        self.click_element(
            driver,
            "//span[contains(text(), '7.14.2.2 - Exportar Arquivo')]",
        )

        # PontoFerias2 li
        self._insert_date_fiorilli_input(
            driver,
            name="PontoFerias2",
        )

        # PontoAfastamentos2 li
        self._insert_date_fiorilli_input(
            driver,
            name="PontoAfastamentos2",
        )

    def _insert_date_fiorilli_input(self, driver, name: str):
        first_day_str, today_str = self._get_today_date()

        # inicio input
        self.click_element(
            driver,
            f"//div[contains(text(), '{name}')]",
        )
        # inicio input
        self.select_and_send_keys(
            driver,
            f"//input[@value='{today_str}'][1]",
            first_day_str,
        )
        # prosseguir btn
        self.click_element(
            driver,
            "//span[contains(text(), 'Prosseguir')]",
        )
        # processar btn
        self.click_element(
            driver,
            "//span[contains(text(), 'Processar')]",
        )

    def ahgora_downloads(self):
        driver = self._get_web_driver("ahgora")
        driver.get("https://app.ahgora.com.br/")
        load_dotenv()

        user = os.getenv("AHGORA_USER")
        pwd = os.getenv("AHGORA_PASSWORD")
        company = os.getenv("AHGORA_COMPANY")

        # email input
        self.send_keys(
            driver,
            "email",
            user,
            selector_type=By.ID,
        )

        # entrar btn
        self.click_element(
            driver,
            "//*[contains(text(), 'Entrar')]",
        )

        # password input
        self.send_keys(
            driver,
            "password",
            pwd,
            selector_type=By.ID,
        )

        self.click_element(
            driver,
            "//*[contains(text(), 'Entrar')]",
        )

        # company input
        self.click_element(
            driver,
            f"//*[contains(text(), '{company}')]",
        )

        self.click_element(
            driver,
            "buttonAdjustPunch",
            selector_type=By.ID,
        )
        self._download_ahgora_employees(driver)
        self._download_ahgora_absences(driver)

        time.sleep(1)
        driver.quit()

    def _download_ahgora_employees(self, driver):
        driver.get("https://app.ahgora.com.br/funcionarios")

        # mostrar desligados btn
        self.click_element(
            driver,
            "filtro_demitido",
            selector_type=By.ID,
        )

        # plus btn
        self.click_element(
            driver,
            "mais",
            selector_type=By.ID,
        )

        # exportar csv
        self.click_element(
            driver,
            "arquivo_csv",
            selector_type=By.ID,
        )

    def _download_ahgora_absences(self, driver):
        driver.get("https://app.ahgora.com.br/relatorios")

        # gerar novos relatorios btn
        self.click_element(
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
        self.click_element(
            driver,
            "//*[contains(text(), 'Afastamentos')]",
        )

        # panel out
        self.click_element(
            driver,
            "tabpanel-0",
            selector_type=By.ID,
        )

        # date btn
        self.click_element(
            driver,
            "_2t8pekO7_rn5BQDaNUsF79",
            selector_type=By.CLASS_NAME,
        )

        # janeiro
        self.click_element(
            driver,
            "//*[contains(text(), 'janeiro')]",
        )

        # gerar btn
        self.click_element(
            driver,
            "//*[contains(text(), 'Gerar')]",
        )

        # gerando relatorio progress bar
        time.sleep(120)
        self.wait_desappear(
            driver,
            "//*[contains(text(), 'Estamos gerando seus relatórios...')]",
            delay=10,
        )
        # relatorio btn
        self.click_element(
            driver,
            "//a[contains(text(),'Afastamentos')]",
        )

        # formato do resultado btn
        self.click_element(
            driver,
            "//div[contains(@comp-textselect, 'Formato do resultado')]",
        )

        # matricula option
        self.click_element(
            driver,
            "//option[contains(@value, 'agrupadoM')]",
        )

        # date
        self.send_keys(
            driver,
            "//input[contains(@id, 'filterByStartDate')]",
            "01/01",
        )

        # gerar relatorio
        self.click_element(
            driver,
            "//button[contains(@id, 'generateReport')]",
        )

        # download icon
        self.click_element(
            driver,
            "//*[@data-testid='CloudDownloadIcon']",
        )

        # baixar em csv btn
        self.click_element(
            driver,
            "//li[contains(text(), 'Baixar em .csv')]",
        )

    def click_element(
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
            lambda: self._click_element_helper(
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

    def right_click_element(
        self,
        driver,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        max_tries=MAX_TRIES,
    ):
        time.sleep(DELAY)
        self._retry_func(
            lambda: self._right_click_button_helper(driver, selector, selector_type),
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

    def _click_element_helper(
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

    def _right_click_button_helper(
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
