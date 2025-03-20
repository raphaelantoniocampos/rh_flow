
from tasks.task import Task
from rich.panel import Panel
from rich.console import Console
from tasks.task_runner import TaskRunner
from InquirerPy import inquirer


class ChangePositionsTask(TaskRunner):
    @staticmethod
    def menu():
        console = Console()
        console.print(
            Panel.fit(
                "Alterar Cargos",
                style="bold cyan",
            )
        )

        proceed = inquirer.confirm(message="Proceed?", default=True).execute()
        if proceed:
            cpt = ChangePositionsTask()
            cpt.run()
        return

    def run(self, task:Task):
        return
