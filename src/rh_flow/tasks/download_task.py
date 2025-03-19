import threading
from rich.panel import Panel
from rich.console import Console
from utils.constants import KEYBINDINGS
from managers.file_manager import FileManager
from browsers.ahgora_browser import AhgoraBrowser
from browsers.fiorilli_browser import FiorilliBrowser
from tasks.task_runner import TaskRunner
from InquirerPy import inquirer


class DownloadTask(TaskRunner):
    DOWNLOAD_OPTIONS = {
        "Funcionários Ahgora": AhgoraBrowser.download_employees_data,
        "Funcionários Fiorilli": FiorilliBrowser.download_employees_data,
        "Afastamentos Fiorilli": FiorilliBrowser.download_absences_data,
    }

    def menu():
        console = Console()
        console.print(
            Panel.fit(
                "BAIXAR DADOS",
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
        FileManager.move_downloads_to_data_dir()
