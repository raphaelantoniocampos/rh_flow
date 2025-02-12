from datetime import date
from os import getenv
from os.path import join
from time import sleep

import pyautogui
from dotenv import load_dotenv
from rich import print
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class FiorilliApp:
    def __init__(
        self,
        working_dir: str,
        interval: float,
        write_interval: float,
    ):
        self.working_dir = working_dir
        self.assets_path = join(working_dir, "assets", "fiorilli")
        self.interval = interval
        self.write_interval = write_interval
        self.today = date.today()
        # self.today = today.strftime("%d/%m/%Y")
        # self.init_date = today.replace(month=1, day=1).strftime("%d/%m/%Y")

    def export_data(self):
        print("--- EXPORTAÇÃO FIORILLI ---")

        # Start webdriver
        chrome_options = Options()
        prefs = {
            "download.default_directory": join(self.working_dir, "downloads"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        service = webdriver.ChromeService(service_args=["--log-level=OFF"])

        driver = webdriver.Chrome(options=chrome_options, service=service)
        driver.get("https://pompeu-pm-sip.sigmix.net/sip/")

        # Login
        load_dotenv()

        user = getenv("FIORILLI_USER")
        pwd = getenv("FIORILLI_PASSWORD")

        while True:
            try:
                pyautogui.locateOnScreen(join(self.assets_path, "login.png"))
                sleep(self.interval)
                break
            except pyautogui.ImageNotFoundException:
                sleep(self.interval)

        pyautogui.write(user, interval=self.write_interval)
        sleep(self.interval)

        pyautogui.press("tab")
        sleep(self.interval)

        pyautogui.write(pwd, interval=self.write_interval)
        sleep(self.interval)

        pyautogui.press("tab")
        sleep(self.interval)

        pyautogui.press("enter")
        sleep(self.interval)

        # Start exporting
        while True:
            try:
                pyautogui.locateOnScreen(join(self.assets_path, "7_utilitarios.png"))
                sleep(self.interval)
                break
            except pyautogui.ImageNotFoundException:
                sleep(self.interval)

        pyautogui.click(join(self.assets_path, "7_utilitarios.png"))
        sleep(self.interval)

        pyautogui.click(join(self.assets_path, "importar_exportar.png"))
        sleep(self.interval)

        pyautogui.click(join(self.assets_path, "exportar.png"))
        sleep(self.interval)

        pyautogui.click(join(self.assets_path, "exportar_arquivo.png"))
        sleep(self.interval)

        today_formatted = self.today.strftime("%d/%m/%Y")
        year_start_formatted = self.today.replace(month=1, day=1).strftime("%d/%m/%Y")
        self.download_file("PontoFuncionario.png", "01", "02")
        # self.download_file("FUNCIONARIOS_ATIVOS2.png", "01/01/2000", today_formatted)
        # self.download_file("ponto_ferias2.png", year_start_formatted, today_formatted)
        # self.download_file("ponto_afastamentos2.png", year_start_formatted, today_formatted)

        sleep(self.interval)

        # Close webdriver
        driver.quit()

    def download_file(self, image_name: str, from_date: str, to_date: str):
        while True:
            try:
                pyautogui.locateOnScreen(join(self.assets_path, image_name))
                sleep(self.interval)
                break
            except pyautogui.ImageNotFoundException:
                sleep(self.interval)

        pyautogui.click(join(self.assets_path, image_name))
        sleep(self.interval)

        while True:
            try:
                pyautogui.locateOnScreen(
                    join(self.assets_path, "parametros_ferias.png")
                )
                sleep(self.interval)
                break
            except pyautogui.ImageNotFoundException:
                sleep(self.interval)

        pyautogui.hotkey(["ctrl", "a"])

        sleep(self.interval)
        pyautogui.write(from_date, interval=self.write_interval)

        sleep(self.interval)
        pyautogui.press("tab")

        sleep(self.interval)
        pyautogui.write(to_date, interval=self.write_interval)

        sleep(self.interval)
        pyautogui.press("tab")

        sleep(self.interval)
        pyautogui.press("enter")

        sleep(self.interval)
        pyautogui.click(join(self.assets_path, "processar.png"))

        sleep(3)
