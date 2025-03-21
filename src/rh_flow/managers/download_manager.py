import threading

from browsers.ahgora_browser import AhgoraBrowser
from browsers.fiorilli_browser import FiorilliBrowser
from InquirerPy import inquirer
from managers.file_manager import FileManager
from rich.console import Console
from rich.panel import Panel
from utils.constants import INQUIRER_KEYBINDINGS, spinner


class DownloadManager:
    DOWNLOAD_OPTIONS = {
        "Funcionários Ahgora": AhgoraBrowser.download_employees_data,
        "Funcionários Fiorilli": FiorilliBrowser.download_employees_data,
        "Afastamentos Fiorilli": FiorilliBrowser.download_absences_data,
    }

    def menu(self):
        console = Console()
        console.print(
            Panel.fit(
                "BAIXAR DADOS",
                style="bold cyan",
            )
        )
        choices = [option for option in self.DOWNLOAD_OPTIONS]
        choices.append("Voltar")

        answers = inquirer.rawlist(
            message="Selecione as opções de download",
            choices=choices,
            keybindings=INQUIRER_KEYBINDINGS,
            multiselect=True,
        ).execute()

        selected_options = []
        if choices[-1] in answers:
            spinner()
            return

        for answer in answers:
            selected_options.append(answer)

        proceed = inquirer.confirm(message="Continuar?", default=True).execute()
        if proceed:
            download_thread = threading.Thread(
                target=self.run,
                args=(selected_options,),
            )
            download_thread.start()

    def run(self, selected_options):
        threads = []
        for option in selected_options:
            fun = self.DOWNLOAD_OPTIONS[option]
            thread = threading.Thread(target=fun)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self._move_files_to_data_dir()

    def _move_files_to_data_dir(self):
        file_manager = FileManager()
        file_manager.move_downloads_to_data_dir()
