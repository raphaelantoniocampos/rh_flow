from abc import ABC, abstractmethod

from InquirerPy import inquirer
from managers.data_manager import DataManager
from managers.download_manager import DownloadManager
from rich.console import Console
from rich.panel import Panel
from utils.constants import spinner

from tasks.task import Task


class TaskRunner(ABC):
    def __init__(self, task: Task):
        self.task = task
        if self.task.df.empty:
            return
        return self.menu()

    def menu(self) -> None:
        """Displays the task menu"""
        console = Console()
        console.print(
            Panel.fit(
                self.task.option,
                style="bold cyan",
            )
        )

        see_list = inquirer.confirm(message="Ver lista?", default=True).execute()
        if see_list:
            self._see_list()

        proceed = inquirer.confirm(message="Continuar?", default=True).execute()
        if proceed:
            self.run()

        spinner()

    @abstractmethod
    def run() -> None:
        """Runs the task"""

    def exit_task(self):
        download_manager = DownloadManager()
        data_manager = DataManager()
        download_manager.run(["Funcionários Ahgora"])
        data_manager.analyze()

    def _see_list(
        self,
    ):
        inquirer.fuzzy(
            message="Select actions:",
            choices=self.task.df.values.tolist(),
            keybindings={
                "skip": [
                    {"key": "enter"},
                ],
            },
            mandatory=False,
        ).execute()
