from utils.constants import BASE_DIR
from managers.data_manager import DataManager
from pathlib import Path
from pandas import DataFrame


class Task:
    def __init__(self, name: str, fun):
        self.name = name
        self.path = self._get_path()
        self.df = self._get_df()
        self.len = self.__len__()
        self.option = self._get_option()
        self.print_string = self._get_print_string()
        self.fun = fun

    def path_exists(self):
        return self.path.exists()

    def is_empty(self):
        try:
            return self.df.empty
        except AttributeError:
            return True

    def __len__(self):
        return len(self.df)

    def get_ignore_dict(self):
        ignore_dict = {}
        if self.name == "new":
            ignore_dict = {
                str(series["id"]): {
                    "id": series["id"],
                    "admission_date": series["admission_date"],
                    "name": series["name"],
                    "binding": series["binding"],
                }
                for _, series in self.df.iterrows()
            }
        if self.name == "dismissed":
            ignore_dict = {
                str(series["id"]): {
                    "id": series["id"],
                    "admission_date": series["admission_date"],
                    "name": series["name"],
                    "binding": series["dismissal_date"],
                }
                for _, series in self.df.iterrows()
            }
        return ignore_dict

    def get_ignore_list(self, ignore_dict: dict):
        return [
            f"{id} - {data['admission_date']} - {data['name']} - {data['binding']}"
            for id, data in ignore_dict.items()
        ]

    def update_df(self, df: DataFrame):
        self.df = df
        self.option = self._get_option()
        self.print_string = self._get_print_string()
        return self

    def _get_df(self) -> DataFrame | None:
        if not self.path_exists():
            return DataFrame()

        return DataManager.read_csv(self.path)

    def _get_path(self):
        if self.name == "new":
            path = Path(BASE_DIR / "data" / "tasks" / "new.csv")
        if self.name == "dismissed":
            path = Path(BASE_DIR / "data" / "tasks" / "dismissed.csv")
        if self.name == "position":
            path = Path(BASE_DIR / "data" / "tasks" / "position.csv")
        if self.name == "absences":
            path = Path(BASE_DIR / "data" / "tasks" / "absences.csv")

        return path

    def _get_option(self):
        check = "➤" if not self.is_empty() else ""
        if self.name == "add_employees":
            return f"Adicionar funcionário {check}"

        if self.name == "dismissed_employees":
            return f"Remover funcionário {check}"

        if self.name == "change_positions":
            return f"Alterar cargos {check}"

        if self.name == "add_absences":
            return f"Adicionar afastamentos {check}"

    def _get_print_string(self):
        if self.name == "add_employees":
            if self.is_empty():
                return "[bold yellow]Nenhum novo funcionário para adicionar no momento.[/bold yellow]"
            return (
                f"[bold cyan]•[/] Adicionar [cyan]{self.len}[/] funcionários no Ahgora"
            )

        if self.name == "dismissed_employees":
            if self.is_empty():
                return "[bold yellow]Nenhum novo funcionário para remover no momento.[/bold yellow]"
            return f"[bold cyan]•[/] Remover [cyan]{self.len}[/] funcionários do Ahgora"

        if self.name == "change_positions":
            if self.is_empty():
                return (
                    "[bold yellow]Nenhum cargo para alterar no momento.[/bold yellow]"
                )
            return f"[bold cyan]•[/] Alterar [cyan]{self.len}[/] cargos no Ahgora"

        if self.name == "add_absences":
            if self.is_empty():
                return "[bold yellow]Nenhum novo afastamento para adicionar no momento.[/bold yellow]"
            return (
                f"[bold cyan]•[/] Adicionar [cyan]{self.len}[/] afastamentos no Ahgora"
            )

    def __str__(self):
        return f"""
-name: {self.name}
-path: {self.path}
-df: {self.df}
-len: {self.len}
-option: {self.option}
-print_string: {self.print_string}
-fun: {self.fun}
-"""
