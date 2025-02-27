from os import getenv
from os.path import join
from time import sleep

import pyautogui
from dotenv import load_dotenv
from selenium import webdriver


class AhgoraApp:
    def __init__(
        self,
        download_dir: str,
        interval: float,
        write_interval: float,
        import_files: list[str],
    ):
        self.download_dir = download_dir
        self.assets_path = join(download_dir, "assets", "ahgora")
        self.interval = interval
        self.write_interval = write_interval
        self.import_files = import_files
        self.center = None

    def add_absences(self):
        print("--- ADICIONAR AFASTAMENTOS ---")
        service = webdriver.ChromeService(service_args=["--log-level=OFF"])

        driver = webdriver.Chrome(service=service)
        driver.get("https://app.ahgora.com.br/afastamentos/importa")

        self._login()

        while True:
            try:
                button_location = pyautogui.locateOnScreen(
                    join(self.assets_path, "pw_afimport.png"), grayscale=True
                )
                pyautogui.click(button_location)
                self.center = button_location
                sleep(self.interval)
                break
            except pyautogui.ImageNotFoundException:
                sleep(self.interval)

        for file_name in self.import_files:
            while True:
                try:
                    button_location = pyautogui.locateOnScreen(
                        join(self.assets_path, "escolher.png"), grayscale=True
                    )
                    pyautogui.click(button_location)
                    sleep(self.interval)
                    break
                except pyautogui.ImageNotFoundException:
                    sleep(self.interval)

            while True:
                try:
                    x, y, _, _ = pyautogui.locateOnScreen(
                        join(self.assets_path, "path.png"), grayscale=True
                    )
                    pyautogui.click(x, y)
                    sleep(self.interval)
                    break
                except pyautogui.ImageNotFoundException:
                    sleep(self.interval)

            sleep(self.interval)
            pyautogui.write(self.download_dir)
            pyautogui.press("enter")

            sleep(self.interval)
            pyautogui.write(file_name)

            sleep(self.interval)
            pyautogui.press("enter")

            while True:
                try:
                    button_location = pyautogui.locateOnScreen(
                        join(self.assets_path, "obter.png"), grayscale=True
                    )
                    sleep(self.interval)
                    pyautogui.click(button_location)
                    sleep(10)
                    break
                except pyautogui.ImageNotFoundException:
                    pyautogui.click(self.center)
                    pyautogui.scroll(-100)
                    sleep(self.interval)

            while True:
                try:
                    button_location = pyautogui.locateOnScreen(
                        join(self.assets_path, "concluir.png"), grayscale=True
                    )
                    pyautogui.click(button_location)
                    sleep(self.interval)
                    break
                except pyautogui.ImageNotFoundException:
                    sleep(self.interval)

        sleep(5)

        # Close webdriver
        driver.quit()

    def _login(self):
        load_dotenv()

        user = getenv("AHGORA_USER")
        pwd = getenv("AHGORA_PASSWORD")

        sleep(2)

        pyautogui.press("tab", presses=2, interval=self.interval)
        sleep(self.interval)

        pyautogui.write(user, interval=self.write_interval)
        sleep(self.interval)

        pyautogui.press("enter")
        sleep(self.interval)

        while True:
            try:
                pyautogui.locateOnScreen(
                    join(self.assets_path, "senha.png"), grayscale=True
                )
                sleep(self.interval)
                break
            except pyautogui.ImageNotFoundException:
                sleep(self.interval)

        pyautogui.press("tab")
        sleep(self.interval)

        pyautogui.write(pwd, interval=self.write_interval)
        sleep(self.interval)

        pyautogui.press("enter")
        sleep(self.interval)

        sleep(2)

        pyautogui.press("tab", presses=2, interval=self.interval)
        sleep(self.interval)

        pyautogui.press("enter")
        sleep(self.interval)
