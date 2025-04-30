from abc import ABC, abstractmethod

from InquirerPy import inquirer
from pyperclip import copy
from rich import print
from rich.panel import Panel

from rh_flow.managers.data_manager import DataManager
from rh_flow.models.key import wait_key_press
from rh_flow.models.task import Task
from rh_flow.utils.constants import console, spinner


class TaskRunner(ABC):
    def __init__(self, task: Task):
        self.task = task
        if self.task.df.empty:
            return
        return self.menu()

    def menu(self) -> None:
        """Displays the task menu"""
        console.print(
            Panel.fit(
                self.task.option,
                style="bold cyan",
            )
        )

        choose_itens = inquirer.confirm(
            message="Ver e escolher itens da lista?", default=False
        ).execute()
        if choose_itens:
            self._choose_itens()

        proceed = inquirer.confirm(message="Iniciar?", default=True).execute()
        if proceed:
            print("Abra o [bold violet]Ahgora[/bold violet] e vá para a URL abaixo.")
            copy(self.task.url)
            print(f"URL '{self.task.url}' copiada para a área de transferência!)")
            wait_key_press(self.KEY_CONTINUE)
            self.run()

        spinner()

    @abstractmethod
    def run() -> None:
        """Runs the task"""

    def exit_task(self):
        if inquirer.confirm(message="Atualizar dados", default=False).execute():
            self.task.path.unlink()

    def _choose_itens(
        self,
    ):
        itens = inquirer.fuzzy(
            message="Select actions:",
            choices=self.task.df.values.tolist(),
            keybindings={
                "answer": [
                    {"key": "enter"},
                ],
                "interrupt": [
                    {"key": "c-c"},
                    {"key": "c-e"},
                ],
                "skip": [
                    {"key": "c-z"},
                    {"key": "escape"},
                ],
                "down": [
                    {"key": "down"},
                ],
                "up": [
                    {"key": "up"},
                ],
                "toggle": [
                    {"key": "space"},
                ],
            },
            mandatory=False,
            multiselect=True,
            border=True,
        ).execute()
        if itens:
            ids = [item[0] for item in itens]
            self.task.df = DataManager.filter_df(self.task.df, ids)
