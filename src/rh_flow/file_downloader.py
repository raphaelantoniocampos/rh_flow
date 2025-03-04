import os
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
        self.driver = self._get_web_driver()

    def run(self):
        # TODO: add multiple downloads
        # TODO: add progress panels

        # self._fiorilli_downloads()
        self.ahgora_downloads()

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
                    print(file.name)
                    time.sleep(60)

        time.sleep(2**10)

    def _get_web_driver(self) -> webdriver.Firefox:
        print("--- Iniciando Web Driver ---")
        options = webdriver.FirefoxOptions()
        # options.add_argument("-headless")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(self.download_path))

        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(DELAY)

        return driver

    def fiorilli_downloads(self):
        self.driver.get("https://pompeu-pm-sip.sigmix.net/sip/")
        load_dotenv()

        user = os.getenv("FIORILLI_USER")
        pwd = os.getenv("FIORILLI_PASSWORD")

        # user input
        self.send_keys("O30_id-inputEl", user)

        # password input
        self.send_keys("O34_id-inputEl", pwd)

        # login btn
        self.click_button("O40_id-btnEl")

        self._download_fiorilli_employees()
        self._download_fiorilli_absences()

    def _download_fiorilli_employees(self) -> None:
        # manutencao btn
        self.click_button("O472_id-btnInnerEl")

        # cadastro btn
        self.click_button("O47E_id-textEl")

        # situacao li
        self.click_button("boundlist-1118-listEl")

        # conteudo input
        self.send_keys("OF05_id-inputEl", "\\0\\2\\3\\4\\5\\6")

        # plus btn
        self.click_button("OF31_id-btnIconEl")

        # filtrar btn
        self.click_button("OF6B_id-btnInnerEl")

        # grid tbl
        self.context_click_button("gridview-1109")

        # grid btn
        self.click_button("O2D5A_id-itemEl")

        # exportar btn
        self.click_button("O2D8B_id-textEl")

        # txt btn
        self.click_button("O2D97_id-textEl")

    def _download_fiorilli_absences(self) -> None:
        # utilidades btn
        self.click_button("OAF7_id-btnInnerEl")

        # importar exportar btn
        self.click_button("OB7F_id-textEl")

        # exportar btn
        self.click_button("OBA6_id-textEl")

        # exportar arquivo btn
        self.click_button("OBB7_id-textEl")

        # PontoFerias2 li
        self._insert_date_fiorilli_input(name="PontoFerias2", id="OE22_id-inputEl")

        # PontoAfastamentos2 li
        self._insert_date_fiorilli_input(
            name="PontoAfastamentos2", id="OE90_id-inputEl"
        )

    def _insert_date_fiorilli_input(self, name: str, id: str):
        # inicio input
        self.click_button(f"//*[contains(text(), '{name}')]", selector_type=By.XPATH)
        # inicio input
        self.select_and_send_keys(id, "01/01/2025")

        # prosseguir btn
        self.click_button("ODEE_id-btnEl")

        # processar btn
        self.click_button("OD1F_id-btnInnerEl")

    def ahgora_downloads(self):
        self.driver.get("https://app.ahgora.com.br/")
        load_dotenv()

        user = os.getenv("AHGORA_USER")
        pwd = os.getenv("AHGORA_PASSWORD")
        company = os.getenv("AHGORA_COMPANY")

        te = self.find_and_wait("email")
        print(te)
        print(type(te))
        time.sleep(600)
        # email input
        self.send_keys("email", user)

        # entrar btn
        self.click_button("//*[contains(text(), 'Entrar')]", selector_type=By.XPATH)

        # password input
        self.send_keys("password", pwd)

        self.click_button("//*[contains(text(), 'Entrar')]", selector_type=By.XPATH)

        # company input
        self.click_button(f"//*[contains(text(), '{company}')]", selector_type=By.XPATH)

        self.click_button("buttonAdjustPunch")
        self._download_ahgora_employees()
        self._download_ahgora_absences()

    def _download_ahgora_employees(self):
        self.driver.get("https://app.ahgora.com.br/funcionarios")

        # mostrar desligados btn
        self.click_button("filtro_demitido")

        # plus btn
        self.click_button("mais")

        # exportar csv
        self.click_button("arquivo_csv")

    def _download_ahgora_absences(self):
        self.driver.get("https://app.ahgora.com.br/relatorios")

        # gerar novos relatorios btn
        self.click_button(
            "//*[contains(text(), 'Gerar novos relatórios')]", selector_type=By.XPATH
        )

        # selecione btn
        self.send_keys(
            "id-autocomplete-multiple-Selecione um relatório (obrigatório)",
            "Afastamentos",
        )

        # afastamentos li
        self.click_button(
            "//*[contains(text(), 'Afastamentos')]", selector_type=By.XPATH
        )

        # panel out
        self.click_button("tabpanel-0")

        # # date btn
        # self.click_button("_2t8pekO7_rn5BQDaNUsF79", selector_type=By.CLASS_NAME)
        #
        # # janeiro
        # self.click_button("//*[contains(text(), 'janeiro')]", selector_type=By.XPATH)

        # gerar btn
        self.click_button("//*[contains(text(), 'Gerar')]", selector_type=By.XPATH)

        time.sleep(180)
        # relatorio btn
        self.click_button(
            "//a[contains(@href,'/relatorios/afastamentos')]", selector_type=By.XPATH
        )

        # formato do resultado btn
        self.click_button("generateReportFilter")

        # matricula option
        self.click_button(
            "//*[contains(text(), 'Agrupado por Mat')]", selector_type=By.XPATH
        )

        # date
        self.send_keys("filterByStartDate", "01/01")

        # gerar relatorio
        self.click_button("generateReport")

        # download icon
        self.click_button(
            "//*[contains(data-testid(), 'CloudDownloadIcon')]", selector_type=By.XPATH
        )

        # baixar em csv btn
        self.click_button(
            "//*[contains(text(), 'Baixar em .csv')]", selector_type=By.XPATH
        )

    def click_button(
        self,
        selector,
        selector_type=By.ID,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        time.sleep(DELAY)
        self._retry_func(
            lambda: self._click_button_helper(
                self.driver, selector, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def send_keys(
        self,
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
                self.driver, selector, keys, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def context_click_button(
        self,
        selector,
        selector_type=By.ID,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        time.sleep(DELAY)
        self._retry_func(
            lambda: self._context_click_button_helper(
                self.driver, selector, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def select_and_send_keys(
        self,
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
                self.driver, selector, keys, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def find_and_wait(
        self,
        selector,
        selector_type=By.ID,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        time.sleep(DELAY)
        return self._retry_func(
            lambda: self._find_and_wait_helper(
                self.driver, selector, selector_type, delay, ignored_exceptions
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
        keys,
        selector_type=By.ID,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        ActionChains(self.driver).context_click(
            WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(
                EC.presence_of_element_located((selector_type, selector))
            )
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
        ActionChains(self.driver).context_click(
            WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(
                EC.presence_of_element_located((selector_type, selector))
            )
        ).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(
            keys
        ).perform()

    def _find_and_wait_helper(
        self,
        driver,
        selector,
        selector_type=By.ID,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((selector_type, selector)))

    def _retry_func(self, func, max_tries=MAX_TRIES):
        for i in range(max_tries):
            try:
                return func()
            except Exception as e:
                time.sleep(DELAY)
                if i >= max_tries - 1:
                    raise e

    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting context: ", self, exc_type, exc_value, traceback)
        self.driver.close()

        return True
