from datetime import date
import os
from time import sleep

from rich import print

import pyautogui
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Exporter:
    WAIT_SECONDS = 0.2
    WRITE_INTERVAL = 0.01
    TAB_INTERVAL = 0.005

    def __init__(self, working_dir):
        self.working_dir = working_dir
        self.download_dir = os.path.join(working_dir, "downloads")
        self.assets_dir = os.path.join(working_dir, "assets")
        self.data_dir = os.path.join(working_dir, "data")

    def run(self):
        print("--- [red]Por favor, afaste-se do teclado e mouse![/] ---")
        for i in range(3, 0, -1):
            sleep(1)
            print(i)

        print("--- Iniciando Exportação ---")
        sleep(1)

        print("--- Limpando pasta de downloads ---")
        for file_paths in self._get_file_paths_from_dir(self.download_dir):
            os.remove(file_paths)

        self._get_file_paths_from_dir(self.download_dir)
        web_driver = self._create_web_driver()

        web_driver = self._download_from_fiorilli(web_driver)

        web_driver = self._download_from_ahgora(web_driver)

        web_driver.close()


        downloaded_files = self._get_file_paths_from_dir(self.download_dir)

        self._move_and_rename_files_to_data_dir(downloaded_files)

        print("[bold green]--- Exportação Concluida ---[/bold green]")

    def _get_file_paths_from_dir(self, dir: str) -> list[str]:
        file_paths = [
            os.path.join(self.download_dir, file_name)
            for file_name in os.listdir(self.download_dir)
        ]
        return file_paths

    def _move_and_rename_files_to_data_dir(self, file_paths: list[str]) -> None:
        print("--- Movendo arquivos ---")
        for file_path in file_paths:
            if "funcionarios.csv" in file_path:
                os.replace(file_path, os.path.join(self.data_dir, "ahgora", "employees_all.csv"))

            if "PontoFuncionario" in file_path:
                os.replace(file_path, os.path.join(self.data_dir, "fiorilli", "active_employees.txt"))

            if "PontoFerias" in file_path:
                os.replace(file_path, os.path.join(self.data_dir, "fiorilli", "vacations_all.txt"))

            if "PontoAfastamentos" in file_path:
                os.replace(file_path, os.path.join(self.data_dir, "fiorilli", "leaves_all.txt"))

            if "FUNCIONARIOS_ATIVOS" in file_path:
                os.replace(file_path, os.path.join(self.data_dir, "fiorilli", "employees_portable.csv"))


    def _create_web_driver(self) -> webdriver.Chrome:
        print("--- Iniciando Web Driver ---")
        chrome_options = Options()
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        service = webdriver.ChromeService(service_args=["--log-level=OFF"])

        web_driver = webdriver.Chrome(options=chrome_options, service=service)
        return web_driver

    def _download_from_fiorilli(self, web_driver: webdriver.Chrome) -> webdriver.Chrome:
        print("--- EXPORTAÇÃO FIORILLI ---")

        web_driver.get("https://pompeu-pm-sip.sigmix.net/sip/")

        self._login_to_fiorilli()

        while True:
            try:
                button_location = pyautogui.locateOnScreen(
                    os.path.join(self.assets_dir, "fiorilli", "7_utilitarios.png"),
                    grayscale=True,
                )
                pyautogui.click(button_location)
                sleep(1)
                break
            except pyautogui.ImageNotFoundException:
                sleep(1)

        pyautogui.click(
            os.path.join(self.assets_dir, "fiorilli", "importar_exportar.png")
        )
        sleep(self.WAIT_SECONDS)

        pyautogui.click(os.path.join(self.assets_dir, "fiorilli", "exportar.png"))
        sleep(self.WAIT_SECONDS)

        pyautogui.click(
            os.path.join(self.assets_dir, "fiorilli", "exportar_arquivo.png")
        )
        sleep(self.WAIT_SECONDS)

        today = date.today()
        today_formatted = today.strftime("%d/%m/%Y")
        year_start_formatted = today.replace(month=1, day=1).strftime("%d/%m/%Y")

        self._download_fiorilli_file(
            "PontoFuncionario.png", today_formatted[3:5], today_formatted[6:]
        )
        self._download_fiorilli_file(
            "FUNCIONARIOS_ATIVOS2.png", "01/01/2000", today_formatted
        )
        self._download_fiorilli_file(
            "ponto_ferias2.png", year_start_formatted, today_formatted
        )
        self._download_fiorilli_file(
            "ponto_afastamentos2.png", year_start_formatted, today_formatted
        )

        sleep(5)

        return web_driver

    def _login_to_fiorilli(self) -> None:
        load_dotenv()

        user = os.getenv("FIORILLI_USER")
        pwd = os.getenv("FIORILLI_PASSWORD")

        while True:
            try:
                pyautogui.locateOnScreen(
                    os.path.join(self.assets_dir, "fiorilli", "login.png"),
                    grayscale=True,
                )
                sleep(1)
                break
            except pyautogui.ImageNotFoundException:
                sleep(1)

        pyautogui.write(user, interval=self.WRITE_INTERVAL)
        sleep(self.WAIT_SECONDS)

        pyautogui.press("tab")
        sleep(self.WAIT_SECONDS)

        pyautogui.write(pwd, interval=self.WRITE_INTERVAL)
        sleep(self.WAIT_SECONDS)

        pyautogui.press("tab")
        sleep(self.WAIT_SECONDS)

        pyautogui.press("enter")
        sleep(self.WAIT_SECONDS)

    def _download_fiorilli_file(
        self, image_name: str, from_date: str, to_date: str
    ) -> None:
        while True:
            try:
                button_location = pyautogui.locateOnScreen(
                    os.path.join(self.assets_dir, "fiorilli", image_name),
                    grayscale=True,
                )
                pyautogui.click(button_location)
                sleep(1)
                break
            except pyautogui.ImageNotFoundException:
                sleep(1)

        while True:
            try:
                pyautogui.locateOnScreen(
                    os.path.join(self.assets_dir, "fiorilli", "parametros_folha.png"),
                    grayscale=True,
                )
                sleep(1)
                break
            except pyautogui.ImageNotFoundException:
                sleep(1)

        pyautogui.hotkey(["ctrl", "a"])
        sleep(self.WAIT_SECONDS)

        pyautogui.write(from_date, interval=self.WRITE_INTERVAL)
        sleep(self.WAIT_SECONDS)

        pyautogui.press("tab")
        sleep(self.WAIT_SECONDS)

        pyautogui.write(to_date, interval=self.WRITE_INTERVAL)
        sleep(self.WAIT_SECONDS)

        pyautogui.press("tab")
        sleep(self.WAIT_SECONDS)

        pyautogui.press("enter")
        sleep(self.WAIT_SECONDS)

        pyautogui.click(os.path.join(self.assets_dir, "fiorilli", "processar.png"))
        sleep(self.WAIT_SECONDS)

        sleep(3)

    def _download_from_ahgora(self, web_driver: webdriver.Chrome) -> webdriver.Chrome:
        print("--- EXPORTAÇÃO AHGORA ---")

        web_driver.get("https://app.ahgora.com.br/funcionarios")

        self._login_to_ahgora()
        sleep(self.WAIT_SECONDS)

        while True:
            try:
                pyautogui.locateOnScreen(
                    os.path.join(self.assets_dir, "ahgora", "funcionarios.png"),
                    grayscale=True,
                )
                sleep(1)
                break
            except pyautogui.ImageNotFoundException:
                sleep(1)

        pyautogui.press("tab", presses=13, interval=self.TAB_INTERVAL)
        sleep(self.WAIT_SECONDS)

        pyautogui.press("enter")
        sleep(self.WAIT_SECONDS)

        while True:
            try:
                button_location = pyautogui.locateOnScreen(
                    os.path.join(self.assets_dir, "ahgora", "ExportarCSV.png"),
                    grayscale=True,
                )
                pyautogui.click(button_location)
                sleep(1)
                break
            except pyautogui.ImageNotFoundException:
                sleep(1)

        sleep(3)
        return web_driver

    def _login_to_ahgora(self) -> None:
        load_dotenv()

        user = os.getenv("AHGORA_USER")
        pwd = os.getenv("AHGORA_PASSWORD")

        sleep(2)

        pyautogui.press("tab", presses=2, interval=self.TAB_INTERVAL)
        sleep(self.WAIT_SECONDS)

        pyautogui.write(user, interval=self.WRITE_INTERVAL)
        sleep(self.WAIT_SECONDS)

        pyautogui.press("enter")
        sleep(self.WAIT_SECONDS)

        while True:
            try:
                pyautogui.locateOnScreen(
                    os.path.join(self.assets_dir, "ahgora", "senha.png"), grayscale=True
                )
                sleep(1)
                break
            except pyautogui.ImageNotFoundException:
                sleep(1)

        pyautogui.press("tab")
        sleep(self.WAIT_SECONDS)

        pyautogui.write(pwd, interval=self.WRITE_INTERVAL)
        sleep(self.WAIT_SECONDS)

        pyautogui.press("enter")
        sleep(self.WAIT_SECONDS)

        sleep(2)

        pyautogui.press("tab", presses=2, interval=self.TAB_INTERVAL)
        sleep(self.WAIT_SECONDS)

        pyautogui.press("enter")
        sleep(self.WAIT_SECONDS)


# afastamentos = [
#     file_name
#     for file_name in os.listdir(data_dir)
#     if os.getsize(os.path.join(data_dir, file_name)) > 0
# ]
#
# if afastamentos:
#     df_list = [
#         read_csv(os.path.join(data_dir, file_name), sep=",", header=None)
#         for file_name in afastamentos
#     ]
#     afastamentos_df = os.path.concat(df_list)
#     afastamentos_df.columns = [
#         "Matricula",
#         "Motivo",
#         "Data Inicio",
#         "Hora Inicio",
#         "Data Fim",
#         "Hora Fim",
#     ]
#     print("--- Afastamentos Baixados ---")
#     print(afastamentos_df)
#
#     start_import = input("Iniciar Importação? (s/n)")
#     if start_import == "s" or start_import == "":
#         ahgora_app = AhgoraApp(
#             download_dir=data_dir,
#             assets_path=join(working_dir, "leaves", "ahgora_app", "assets"),
#             interval=INTERVAL,
#             write_interval=WRITE_INTERVAL,
#             import_files=afastamentos,
#         )
#         ahgora_app.run()
# else:
#     print(f"Nenhum afastamento pro dia {export_date}.")
#
# sleep(1)
# print("--- Concluído ---")
# sleep(1)
# print("--- Fechando Automação ---")
# sleep(3)
