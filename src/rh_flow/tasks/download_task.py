import threading
from rich.panel import Panel
from rich.console import Console
from utils.constants import DOWNLOADS_DIR, KEYBINDINGS
from file_manager import FileManager
from browsers.ahgora_browser import AhgoraBrowser
from browsers.fiorilli_browser import FiorilliBrowser
import time
from InquirerPy import inquirer


class DownloadTask:
    DOWNLOAD_OPTIONS = {
        "Funcionários Ahgora": {"browser": AhgoraBrowser, "data":"employees"},
        "Funcionários Fiorilli": {"browser":FiorilliBrowser, "data": "employees"},
        "Afastamentos Fiorilli": {"browser":FiorilliBrowser, "data": "absences"},
    }

    def menu():
        console = Console()
        console.print(
            Panel.fit(
                "DOWNLOADS",
                style="bold cyan",
            )
        )
        choices = [
            f"{index}. {option}"
            for index, option in enumerate(DownloadTask.DOWNLOAD_OPTIONS, start=1)
        ]
        choices.append(f"{len(choices) + 1}. Voltar")

        answers = inquirer.checkbox(
            message="Selecione as opções de download",
            choices=choices,
            keybindings=KEYBINDINGS,
        ).execute()

        selected_options = []
        if choices[-1] in answers:
            return

        for answer in answers:
            selected_options.append(answer[3:])

        download_task = DownloadTask()
        download_task.run(selected_options)

    def run(self, selected_options):
        downloaded_files = []

        threads = []
        for option in selected_options:
            browser = self.DOWNLOAD_OPTIONS[option]["browser"]()
            data = self.DOWNLOAD_OPTIONS[option]["data"]
            thread = threading.Thread(target=browser.download_data(data))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self._wait_for_downloads_to_complete(downloaded_files)
        self._move_files_to_data_dir()

    def _wait_for_downloads_to_complete(self, downloaded_files):
        while len(downloaded_files) < 4:
            for file in DOWNLOADS_DIR.iterdir():
                if any(
                    keyword in file.name.lower()
                    for keyword in ["grid", "pontoferias", "pontoafast", "funcionarios"]
                ):
                    if file.name not in downloaded_files:
                        downloaded_files.append(file.name)
            time.sleep(30)

    def _move_files_to_data_dir(self):
        FileManager.move_files_from_downloads_dir()
