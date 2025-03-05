from data_manager import read_csv
from pathlib import Path
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

    def update_df(self, df: DataFrame):
        self.df = df
        self.len = self.get_len()
        self.option = self._get_option()
        self.order = self._get_order()
        return self

    def _get_df(self) -> DataFrame | None:
        if not self.path_exists():
            return DataFrame()

        return read_csv(self.path)

    def _get_path(self):
        base_dir_path = Path.cwd()

        if self.name == "new":
            path = Path(base_dir_path / "data" / "actions" / "new.csv")
        if self.name == "dismissed":
            path = Path(base_dir_path / "data" / "actions" / "dismissed.csv")
        if self.name == "position":
            path = Path(base_dir_path / "data" / "actions" / "position.csv")
        if self.name == "absences":
            path = Path(base_dir_path / "data" / "actions" / "absences.csv")

        return path

    def _get_option(self):
        check = '➤' if not self.is_empty() else ''
        if self.name == "new":
            return f"Adicionar no Ahgora {check}"

        if self.name == "dismissed":
            return f"Remover do Ahgora {check}"

        if self.name == "position":
            return f"Alterar cargos {check}"

        if self.name == "absences":
            return f"Adicionar afastamentos {check}"

    def _get_order(self):
        if self.name == "new":
            if self.is_empty():
                return "[bold yellow]Nenhum novo funcionário para adicionar no momento.[/bold yellow]"
            return (
                f"[bold cyan]•[/] Adicionar [cyan]{self.len}[/] funcionários no Ahgora"
            )

        if self.name == "dismissed":
            if self.is_empty():
                return "[bold yellow]Nenhum novo funcionário para remover no momento.[/bold yellow]"
            return f"[bold cyan]•[/] Remover [cyan]{self.len}[/] funcionários do Ahgora"

        if self.name == "position":
            if self.is_empty():
                return (
                    "[bold yellow]Nenhum cargo para alterar no momento.[/bold yellow]"
                )
            return f"[bold cyan]•[/] Alterar [cyan]{self.len}[/] cargos no Ahgora"

        if self.name == "absences":
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
-order: {self.order}
-fun: {self.fun}
-"""
