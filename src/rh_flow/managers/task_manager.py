from managers.data_manager import DataManager
from tasks.add_employees_task import AddEmployeesTask
from tasks.add_absences_task import AddAbsencesTask
from tasks.remove_employees_task import RemoveEmployeesTask
from tasks.change_positions_task import ChangePositionsTask
from pandas import DataFrame
from pathlib import Path
from tasks.task import Task
from rich.panel import Panel
from rich.console import Console
from utils.constants import INQUIRER_KEYBINDINGS, DATA_DIR, spinner
from InquirerPy import inquirer


class TaskManager:
    def menu(self, tasks: list[Task]):
        console = Console()
        console.print(
            Panel.fit(
                "Escolher Tarefas",
                style="bold cyan",
            )
        )
        choice = {task.option: task for task in tasks if not task.df.empty}
        choice["Voltar"] = ""

        option = inquirer.rawlist(
            message="Selecione uma tarefa",
            choices=choice.keys(),
            keybindings=INQUIRER_KEYBINDINGS,
        ).execute()

        if "Voltar" in option:
            spinner()
            return

        self.get_task_runner(choice[option])

    def get_task_runner(self, task: Task):
        match task.name:
            case "add_employees":
                return AddEmployeesTask(task)
            case "remove_employees":
                return RemoveEmployeesTask(task)
            case "change_positions":
                return ChangePositionsTask(task)
            case "add_absences":
                return AddAbsencesTask(task)

    @staticmethod
    def get_tasks() -> list[Task]:
        tm = TaskManager()
        return [
            tm.name_to_task("add_employees"),
            tm.name_to_task("remove_employees"),
            tm.name_to_task("change_positions"),
            tm.name_to_task("add_absences"),
        ]

    def name_to_task(self, name: str) -> Task:
        df = self._get_df(name)
        option = self._get_option(name, df)

        task = Task(
            name=name,
            df=df,
            option=option,
        )
        return task

    def _get_df(self, name) -> DataFrame | None:
        data_manager = DataManager()
        path = self._get_path(name)
        if isinstance(path, str):
            return DataFrame()
        if not path.exists():
            return DataFrame()
        return data_manager.read_csv(path)

    def _get_path(self, name: str) -> Path:
        match name:
            case "add_employees":
                return DATA_DIR / "tasks" / "new_employees.csv"
            case "remove_employees":
                return DATA_DIR / "tasks" / "dismissed_employees.csv"
            case "change_positions":
                return DATA_DIR / "tasks" / "changed_positions.csv"
            case "add_absences":
                return DATA_DIR / "tasks" / "new_absences.csv"

    def _get_option(self, name: str, df: DataFrame) -> str:
        if df.empty:
            return ""

        match name:
            case "add_employees":
                return f"[bold cyan]•[/] Adicionar [cyan]{len(df)}[/] funcionários"

            case "remove_employees":
                return f"[bold cyan]•[/] Remover [cyan]{len(df)}[/] funcionários"

            case "change_positions":
                return f"[bold cyan]•[/] Alterar [cyan]{len(df)}[/] cargos"

            case "add_absences":
                return f"[bold cyan]•[/] Adicionar [cyan]{len(df)}[/] afastamentos"
