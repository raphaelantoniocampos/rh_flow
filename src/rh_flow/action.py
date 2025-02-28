from pathlib import Path

from data_manager import read_csv
from pandas import DataFrame


class Action:
    def __init__(self, name: str, fun):
        self.name = name
        self.path = self._get_path()
        self.df = self._get_df()
        self.len = self.get_len()
        self.option = self._get_option()
        self.order = self._get_order()
        self.fun = fun

    def path_exists(self):
        return self.path.exists()

    def is_empty(self):
        try:
            return self.df.empty
        except AttributeError:
            return True

    def get_len(self):
        if self.is_empty():
            return 0
        return len(self._get_df())

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

    def _get_df(self) -> DataFrame | None:
        if not self.path_exists():
            return DataFrame()
        return read_csv(self.path)

    def _get_path(self):
        working_dir_path = Path.cwd()
        if self.name == "new":
            path = Path(working_dir_path / "data" / "actions" / "new.csv")
        if self.name == "dismissed":
            path = Path(working_dir_path / "data" / "actions" / "dismissed.csv")
        if self.name == "position":
            path = Path(working_dir_path / "data" / "actions" / "position.csv")
        if self.name == "absences":
            path = Path(working_dir_path / "data" / "actions" / "absences.csv")

        return path

    def _get_option(self):
        option = ""
        if self.name == "new":
            option = "Adicionar no Ahgora"
        if self.name == "dismissed":
            option = "Remover do Ahgora"
        if self.name == "position":
            option = "Alterar cargo"
        if self.name == "absences":
            option = "Adicionar afastamento"

        return option

    def _get_order(self):
        order = ""
        if self.name == "new":
            if self.is_empty():
                order = "[bold yellow]Nenhum novo funcionário para adicionar no momento.[/bold yellow]"
            else:
                order = f"[bold cyan]•[/] Adicionar [cyan]{self.len}[/] funcionários no Ahgora"
        if self.name == "dismissed":
            if self.is_empty():
                order = "[bold yellow]Nenhum novo funcionário para remover no momento.[/bold yellow]"
            else:
                order = f"[bold cyan]•[/] Remover [cyan]{self.len}[/] funcionários do Ahgora"
        if self.name == "position":
            if self.is_empty():
                order = (
                    "[bold yellow]Nenhum cargo para alterar no momento.[/bold yellow]"
                )
            else:
                order = (
                    f"[bold cyan]•[/] Alterar [cyan]{self.len}[/] cargos no Ahgora"
                )
        if self.name == "absences":
            if self.is_empty():
                order = "[bold yellow]Nenhum novo afastamento para adicionar no momento.[/bold yellow]"
            else:
                order = f"[bold cyan]•[/] Adicionar [cyan]{self.len}[/] afastamentos no Ahgora"

        return order

        def __str__(self):
            return f"""
name: {self.name}
path: {self.path}
df: {self.df}
len: {self.len}
option: {self.option}
order: {self.order}
fun: {self.fun}
"""
