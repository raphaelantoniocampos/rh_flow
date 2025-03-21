from abc import ABC, abstractmethod

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from utils.constants import spinner

from tasks.task import Task


class Key:
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.key = str(name)

    def __str__(self):
        return f"[bold {self.color}]{self.name.upper()}[/bold {self.color}]"


class TaskRunner(ABC):
    KEY_CONTINUE = Key("F2", "green")
    KEY_NEXT = Key("F3", "yellow")
    KEY_STOP = Key("F4", "red3")

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

    # def menu(self, config, tasks):
    #     while True:
    #         option: str = self._show_tasks_menu(tasks)[3:]
    #         if option == "Voltar":
    #             return
    #         for task in tasks:
    #             if option == task.option:
    #                 time.sleep(1)
    #                 if task.len == 0:
    #                     print(task.order)
    #                     return
    #                 self._prepare_list_and_run(task)

    @abstractmethod
    def run() -> None:
        """Runs the task"""

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
