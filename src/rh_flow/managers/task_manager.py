from managers.data_manager import DataManager
from pandas import DataFrame
from pathlib import Path
from utils.constants import DATA_DIR
from tasks.add_employees_task import AddEmployeesTask
from tasks.remove_employees_task import RemoveEmployeesTask
from tasks.change_positions_task import ChangePositionsTask
from tasks.add_absences_task import AddAbsencesTask
from tasks.task import Task
import time
from rich.panel import Panel
from rich.console import Console
from utils.constants import INQUIRER_KEYBINDINGS
from InquirerPy import inquirer


class TaskManager:
    @staticmethod
    def menu(tasks: list[Task]):
        console = Console()
        console.print(
            Panel.fit(
                "Escolher Tarefas",
                style="bold cyan",
            )
        )
        choices = [task.option for task in tasks]
        choices.append("Voltar")

        option = inquirer.rawlist(
            message="Selecione uma tarefa",
            choices=choices,
            keybindings=INQUIRER_KEYBINDINGS,
        ).execute()

        if choices[-1] in option:
            with console.status("[bold green]Voltando...[/bold green]", spinner="dots"):
                time.sleep(0.5)
            return

        proceed = inquirer.confirm(message="Continuar?", default=True).execute()
        if proceed:
            tm = TaskManager()
            tm.get_menu(answer)
            dt = DownloadTask()
            dt.run(selected_options)

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
        option = self._get_option(name, df.empty)
        print_string = self._get_print_string(name, df.empty)
        menu = self._get_menu(name)

        task = Task(
            name=name,
            df=df,
            option=option,
            print_string=print_string,
            menu=menu,
        )
        return task

    def get_menu(self, option: str):
        name = self._get_name(option)
        match name:
            case "add_employees":
                return AddEmployeesTask.menu
            case "dismissed_employees":
                return RemoveEmployeesTask.menu
            case "change_positions":
                return ChangePositionsTask.menu
            case "add_absences":
                return AddAbsencesTask.menu

    def _get_df(self, name) -> DataFrame | None:
        path = self._get_path(name)
        if not path.exists():
            return DataFrame()

        return DataManager.read_csv(path)

    def _get_path(self, name: str) -> Path:
        match name:
            case "add_employees":
                return DATA_DIR / "tasks" / "new.csv"
            case "remove_employees":
                return DATA_DIR / "tasks" / "dismissed.csv"
            case "change_positions":
                return DATA_DIR / "tasks" / "position.csv"
            case "add_absences":
                return DATA_DIR / "tasks" / "absences.csv"
            case "download":
                return ""

    def _get_option(self, name: str, df_is_empty) -> str:
        check = "➤" if not df_is_empty else ""
        match name:
            case "add_employees":
                return f"Adicionar funcionário {check}"

            case "dismissed_employees":
                return f"Remover funcionário {check}"

            case "change_positions":
                return f"Alterar cargos {check}"

            case "add_absences":
                return f"Adicionar afastamentos {check}"

            case "download":
                return f"Baixar dados {check}"

    def _get_print_string(self, name: str, df_is_empty: bool) -> str:
        match name:
            case "add_employees":
                if df_is_empty:
                    return "[bold yellow]Nenhum novo funcionário para adicionar no momento.[/bold yellow]"
                return f"[bold cyan]•[/] Adicionar [cyan]{self.len}[/] funcionários no Ahgora"

            case "dismissed_employees":
                if df_is_empty:
                    return "[bold yellow]Nenhum novo funcionário para remover no momento.[/bold yellow]"
                return f"[bold cyan]•[/] Remover [cyan]{self.len}[/] funcionários do Ahgora"

            case "change_positions":
                if df_is_empty:
                    return "[bold yellow]Nenhum cargo para alterar no momento.[/bold yellow]"
                return f"[bold cyan]•[/] Alterar [cyan]{self.len}[/] cargos no Ahgora"

            case "add_absences":
                if df_is_empty:
                    return "[bold yellow]Nenhum novo afastamento para adicionar no momento.[/bold yellow]"
                return f"[bold cyan]•[/] Adicionar [cyan]{self.len}[/] afastamentos no Ahgora"

            case "download":
                if df_is_empty:
                    return "[bold yellow]Nenhum novo afastamento para adicionar no momento.[/bold yellow]"
                return f"[bold cyan]•[/] Adicionar [cyan]{self.len}[/] afastamentos no Ahgora"
