import inquirer
from time import sleep
from pathlib import Path
import os

import pandas as pd
from rich import print
from dataclasses import dataclass
from utils import Utils


@dataclass
class Actions:
    to_add: pd.DataFrame | None
    to_remove: pd.DataFrame | None


class DataManager:
    def __init__(self, working_dir: str):
        self.data_dir = Path(working_dir) / "data"
        self.utils = Utils(data_dir=self.data_dir)

    def analyze(self) -> (pd.DataFrame, pd.DataFrame):
        try:
            print("--- Analisando dados de Funcionários entre Fiorilli e Ahgora ---\n")
            fiorilli_employees, ahgora_employees = self._get_employees_data()
            new_employees, dismissed_employees = self._generate_actions_dfs(
                fiorilli_employees, ahgora_employees
            )
            save_dir = self.data_dir / "actions"

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

            print("[bold green]Dados sincronizados com sucesso![/bold green]\n")
            sleep(1)
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao adicionar funcionários: {e}[/bold red]\n")
            sleep(1)

    def prepare_dataframe(self, df, cols_names: list[str] = []):
        if cols_names:
            df.columns = cols_names

        # if 'Vinculo' in df.columns:
        #     df = df[
        #         ~df["Vinculo"].isin(viculos)
        #     ]

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

        print(df)
        return df

    def update_employees_to_ignore(self, df: pd.DataFrame) -> pd.DataFrame:
        employees = [
            f"{series['Matricula']} - {series['Data Admissao']} - {series['Nome']} - {series['Vinculo']}"
            for _, series in df.iterrows()
        ]

        print("Selecione os funcionários para ignorar")
        employees_to_ignore = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "ignore",
                    message="Matricula - Data Admissao - Nome - Vinculo",
                    choices=employees
                    ,
                )
            ]
        ).get("ignore")

        self.utils.update("ignore", employees_to_ignore)
        to_ignore = [ignore[:6] for ignore in employees_to_ignore]
        return df[~df["Matricula"].isin(to_ignore)]

    def get_actions(self) -> Actions:
        actions_dir = self.data_dir / "actions"

        new_employees_path = actions_dir / "new_employees.csv"
        dismissed_employees_path = actions_dir / "dismissed_employees.csv"

        actions = Actions(None, None)

        if os.path.isfile(new_employees_path):
            df_new = pd.read_csv(
                new_employees_path,
                index_col=False,
                dtype={"Matricula": str},
            )

            df_new = self.prepare_dataframe(df_new)
            actions.to_add = df_new

        if os.path.isfile(dismissed_employees_path):
            df_dismissed = pd.read_csv(
                dismissed_employees_path,
                index_col=False,
                dtype={"Matricula": str},
            )
            df_dismissed = self.prepare_dataframe(df_dismissed)
            actions.to_remove = df_dismissed

        return actions

    def _get_employees_data(self) -> (pd.DataFrame, pd.DataFrame):
        fiorilli_employees_path = self.data_dir / "fiorilli" / "employees.txt"
        ahgora_employees_path = self.data_dir / "ahgora" / "employees.csv"

        fiorilli_employees = pd.read_csv(
            fiorilli_employees_path,
            encoding="latin1",
            sep="|",
            index_col=False,
            header=None,
            dtype={"Matricula": str},
        )

        fiorilli_employees = self.prepare_dataframe(
            fiorilli_employees,
            [
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

        ahgora_employees = pd.read_csv(
            ahgora_employees_path,
            sep=",",
            index_col=False,
            header=None,
            dtype={"Matricula": str},
        )

        ahgora_employees = self.prepare_dataframe(
            ahgora_employees,
            [
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
