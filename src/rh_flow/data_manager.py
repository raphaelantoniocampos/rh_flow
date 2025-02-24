from time import sleep
from pathlib import Path
import os

from datetime import datetime
import pandas as pd
from rich import print
from dataclasses import dataclass
from config import Config


@dataclass
class Actions:
    to_add: pd.DataFrame | None
    to_remove: pd.DataFrame | None


class DataManager:
    def __init__(self, working_dir_path: str, config: Config):
        self.data_dir_path = Path(working_dir_path) / "data"
        self.config = config

    def analyze(self) -> (pd.DataFrame, pd.DataFrame):
        try:
            print("--- Analisando dados de Funcionários entre Fiorilli e Ahgora ---\n")
            fiorilli_employees, ahgora_employees = self._get_employees_data()
            new_employees, dismissed_employees = self._generate_actions_dfs(
                fiorilli_employees, ahgora_employees
            )
            save_dir = self.data_dir_path / "actions"

            if not new_employees.empty:
                new_employees.to_csv(
                    os.path.join(save_dir, "new_employees.csv"),
                    index=False,
                    encoding="utf-8",
                )

            if not dismissed_employees.empty:
                dismissed_employees.to_csv(
                    os.path.join(save_dir, "dismissed_employees.csv"),
                    index=False,
                    encoding="utf-8",
                )
            now = datetime.now().strftime("%d/%m/%Y, %H:%M")
            self.config._update("last_analisys", {"datetime": now, "time_since": now})
            print("[bold green]Dados sincronizados com sucesso![/bold green]\n")
            sleep(1)
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao adicionar funcionários: {e}[/bold red]\n")
            sleep(1)

    def _read_csv(
        self,
        path: str,
        sep: str = ",",
        encoding: str = "utf-8",
        header: str | None = "infer",
        cols_names: list[str] = [],
    ):
        df = pd.read_csv(
            path,
            sep=sep,
            encoding=encoding,
            index_col=False,
            header=header,
            dtype={"Matricula": str},
        )

        return self._prepare_dataframe(df=df, cols_names=cols_names)

    def _prepare_dataframe(self, df, cols_names: list[str] = []):
        if cols_names:
            df.columns = cols_names

        df["Data Admissao"] = pd.to_datetime(
            df["Data Admissao"], dayfirst=True, errors="coerce"
        )

        try:
            df["CPF"] = df["CPF"].fillna("").astype(str).str.zfill(11)
        except KeyError:
            pass
        df["Nome"] = df["Nome"].str.strip().str.upper()

        df["Matricula"] = df["Matricula"].astype(str).str.zfill(6)

        df["Data Admissao"] = df["Data Admissao"].dt.strftime("%d/%m/%Y")

        return df

    def get_actions(self) -> Actions:
        actions_dir = self.data_dir_path / "actions"

        new_employees_path = actions_dir / "new_employees.csv"
        dismissed_employees_path = actions_dir / "dismissed_employees.csv"

        ignore_list = self.config.data.get("ignore", {})
        ignore_ids = set(ignore_list.keys())

        actions = Actions(None, None)

        if os.path.isfile(new_employees_path):
            df_new = self._read_csv(new_employees_path)
            df_new = df_new[~df_new["Matricula"].isin(ignore_ids)]
            actions.to_add = df_new

        if os.path.isfile(dismissed_employees_path):
            df_dismissed = self._read_csv(dismissed_employees_path)
            # df_dismissed = df_dismissed[~df_dismissed["Matricula"].isin(ignore_ids)]
            actions.to_remove = df_dismissed

        return actions

    def _get_employees_data(self) -> (pd.DataFrame, pd.DataFrame):
        fiorilli_employees_path = self.data_dir_path / "fiorilli" / "employees.txt"
        ahgora_employees_path = self.data_dir_path / "ahgora" / "employees.csv"

        fiorilli_employees = self._read_csv(
            fiorilli_employees_path,
            sep="|",
            encoding="latin1",
            header=None,
            cols_names=[
                "Matricula",
                "Nome",
                "CPF",
                "Sexo",
                "Data Nascimento",
                "PIS-PASEP",
                "Cargo",
                "Localizacao",
                "Departamento",
                "Vinculo",
                "Data Admissao",
                "Data Desligamento",
            ],
        )

        ahgora_employees = self._read_csv(
            ahgora_employees_path,
            header=None,
            cols_names=[
                "Matricula",
                "Nome",
                "Cargo",
                "Escala",
                "Departamento",
                "Localizacao",
                "Data Admissao",
                "Data Desligamento",
            ],
        )

        return fiorilli_employees, ahgora_employees

    def _generate_actions_dfs(
        self, fiorilli_employees: pd.DataFrame, ahgora_employees: pd.DataFrame
    ):
        fiorilli_dismissed_df = fiorilli_employees[
            fiorilli_employees["Data Desligamento"].notna()
        ]
        fiorilli_dismissed_ids = set(fiorilli_dismissed_df["Matricula"])

        ahgora_dismissed_df = ahgora_employees[
            ahgora_employees["Data Desligamento"].notna()
        ]
        ahgora_dismissed_ids = set(ahgora_dismissed_df["Matricula"])

        dismissed_ids = ahgora_dismissed_ids | fiorilli_dismissed_ids

        fiorilli_active_df = fiorilli_employees[
            ~fiorilli_employees["Matricula"].isin(dismissed_ids)
        ]

        ahgora_ids = set(ahgora_employees["Matricula"])

        new_employees = fiorilli_active_df[
            ~fiorilli_active_df["Matricula"].isin(ahgora_ids)
        ]

        dismissed_employees = ahgora_employees[
            ahgora_employees["Matricula"].isin(fiorilli_dismissed_ids)
            & ~ahgora_employees["Matricula"].isin(ahgora_dismissed_ids)
        ]

        dismissed_employees = dismissed_employees.drop(columns=["Data Desligamento"])
        dismissed_employees = dismissed_employees.merge(
            fiorilli_dismissed_df[["Matricula", "Data Desligamento"]],
            on="Matricula",
            how="left",
        )

        return new_employees, dismissed_employees
