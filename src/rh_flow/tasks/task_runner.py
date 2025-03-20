from utils.constants import spinner
import time
from abc import ABC, abstractmethod

from InquirerPy import inquirer
from rich import print

from tasks.task import Task
from rich.console import Console
from rich.panel import Panel


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

    def _prepare_list_and_run(
        self,
        task: Task,
    ):
        time.sleep(1)
        print(task.order)
        print("\n")
        if task.df.size > 0:
            see_list = inquirer.prompt(
                [
                    inquirer.Confirm(
                        "yes",
                        message="Ver lista de funcionários",
                    )
                ]
            )

            if see_list["yes"] is None:
                return

            see_list: dict[str, bool] = see_list["yes"]
            if see_list:
                time.sleep(0.5)
                task.df = self.config.update_employees_to_ignore(task)

            ok_input = inquirer.prompt(
                [inquirer.Confirm("yes", message="Começar?", default="yes")]
            )
            time.sleep(0.5)
            if not ok_input["yes"]:
                return

            task.fun(task.df)
