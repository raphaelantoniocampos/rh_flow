from pathlib import Path
from time import sleep
import pandas as pd
from pandas.errors import EmptyDataError
from rich import print

class DataManager:
    def __init__(self, base_dir_path: str, config):
        self.data_dir_path = Path(base_dir_path) / "data"
        self.config = config

    def analyze(self) -> None:
        """Analisa os dados de funcionários e afastamentos, gerando tarefas."""
        try:
            print("--- Analisando dados de Funcionários entre Fiorilli e Ahgora ---\n")
            ahgora_employees, fiorilli_employees = self._get_employees_data()
            fiorilli_absences = self._get_fiorilli_absences()

            new_df, dismissed_df, position_df, absences_df = self._generate_tasks_dfs(
                fiorilli_employees, ahgora_employees, fiorilli_absences
            )

            self._save_tasks_to_csv(new_df, dismissed_df, position_df, absences_df)
            self.config.update_last_analysis()
            print("[bold green]Dados sincronizados com sucesso![/bold green]\n")
            sleep(1)
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao adicionar funcionários: {e}[/bold red]\n")
            sleep(1)

    def _get_employees_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Carrega os dados de funcionários do Fiorilli e Ahgora."""
        fiorilli_employees_path = self.data_dir_path / "fiorilli" / "employees.txt"
        ahgora_employees_path = self.data_dir_path / "ahgora" / "employees.csv"

        fiorilli_employees = self._read_csv(
            fiorilli_employees_path,
            sep="|",
            encoding="latin1",
            header=None,
            columns=[
                "id", "name", "cpf", "sex", "birth_date", "pis_pasep", "position",
                "location", "department", "binding", "admission_date", "dismissal_date",
            ],
        )

        ahgora_employees = self._read_csv(
            ahgora_employees_path,
            header=None,
            columns=[
                "id", "name", "position", "scale", "department", "location",
                "admission_date", "dismissal_date",
            ],
        )
        return ahgora_employees, fiorilli_employees

    def _get_fiorilli_absences(self) -> pd.DataFrame:
        """Carrega os dados de afastamentos do Fiorilli."""
        fiorilli_absences_path = self.data_dir_path / "fiorilli" / "absences.txt"
        fiorilli_vacations_path = self.data_dir_path / "fiorilli" / "vacations.txt"

        try:
            fiorilli_columns = ["id", "cod", "start_date", "start_time", "end_date", "end_time"]
            return pd.concat([
                self._read_csv(fiorilli_vacations_path, header=None, columns=fiorilli_columns),
                self._read_csv(fiorilli_absences_path, header=None, columns=fiorilli_columns),
            ])
        except EmptyDataError:
            return pd.DataFrame()

    def _generate_tasks_dfs(
        self,
        fiorilli_employees: pd.DataFrame,
        ahgora_employees: pd.DataFrame,
        fiorilli_absences: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Gera os DataFrames para as tarefas de novos funcionários, desligamentos, cargos e afastamentos."""
        fiorilli_dismissed_df = fiorilli_employees[fiorilli_employees["dismissal_date"].notna()]
        fiorilli_dismissed_ids = set(fiorilli_dismissed_df["id"])

        ahgora_dismissed_df = ahgora_employees[ahgora_employees["dismissal_date"].notna()]
        ahgora_dismissed_ids = set(ahgora_dismissed_df["id"])

        dismissed_ids = ahgora_dismissed_ids | fiorilli_dismissed_ids

        fiorilli_active_df = fiorilli_employees[~fiorilli_employees["id"].isin(dismissed_ids)]
        ahgora_ids = set(ahgora_employees["id"])

        new_df = fiorilli_active_df[~fiorilli_active_df["id"].isin(ahgora_ids)]
        dismissed_df = ahgora_employees[
            ahgora_employees["id"].isin(fiorilli_dismissed_ids) & ~ahgora_employees["id"].isin(ahgora_dismissed_ids)
        ].merge(fiorilli_dismissed_df[["id", "dismissal_date"]], on="id", how="left")

        merged_employees = fiorilli_employees.merge(
            ahgora_employees, on="id", suffixes=("_fiorilli", "_ahgora"), how="inner"
        )
        position_df = merged_employees[
            merged_employees["position_fiorilli"] != merged_employees["position_ahgora"]
        ]

        absences_df = fiorilli_absences
        return new_df, dismissed_df, position_df, absences_df

    def _save_tasks_to_csv(self, new_df, dismissed_df, position_df, absences_df) -> None:
        """Salva os DataFrames gerados em arquivos CSV."""
        save_dir = self.data_dir_path / "tasks"
        save_dir.mkdir(parents=True, exist_ok=True)

        if not new_df.empty:
            new_df.to_csv(save_dir / "new.csv", index=False, encoding="utf-8")
        if not dismissed_df.empty:
            dismissed_df.to_csv(save_dir / "dismissed.csv", index=False, encoding="utf-8")
        if not position_df.empty:
            position_df.to_csv(save_dir / "position.csv", index=False, encoding="utf-8")
        if not absences_df.empty:
            absences_df.to_csv(save_dir / "absences.txt", index=False, header=False, encoding="utf-8")

    @staticmethod
    def _read_csv(path: Path, **kwargs) -> pd.DataFrame:
        """Lê um arquivo CSV e retorna um DataFrame."""
        try:
            return pd.read_csv(path, **kwargs)
        except EmptyDataError:
            return pd.DataFrame()

class DataManagerFactory:
    @staticmethod
    def create_data_manager(manager_type: str, *args, **kwargs):
        if manager_type.lower() == "default":
            return DataManager(*args, **kwargs)
        elif manager_type.lower() == "advanced":
            return AdvancedDataManager(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported manager type: {manager_type}")
