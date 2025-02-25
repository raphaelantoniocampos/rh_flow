from time import sleep
from pathlib import Path
import os

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

            self.config.update_last_analisys()
            print("[bold green]Dados sincronizados com sucesso![/bold green]\n")
            sleep(1)
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao adicionar funcionários: {e}[/bold red]\n")
            sleep(1)

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

    def analyze_leaves(self):
        try:
            print("--- Analisando afastamentos entre Fiorilli e Ahgora ---\n")

            fiorilli_leaves, ahgora_leaves = self._get_leaves_data()

            fiorilli_ids = set(fiorilli_leaves["Matricula"])
            ahgora_ids = set(ahgora_leaves["Matricula"])

            # no_fio = fiorilli_leaves[~fiorilli_leaves["Matricula"].isin(ahgora_ids)]
            # no_agora = ahgora_leaves[~ahgora_leaves["Matricula"].isin(fiorilli_ids)]

            fiorilli_leaves["key"] = (
                fiorilli_leaves["Matricula"].astype(str)
                + "-"
                + fiorilli_leaves["Data Inicio"].astype(str)
                + "-"
                + fiorilli_leaves["Data Fim"].astype(str)
            )

            ahgora_leaves["key"] = (
                ahgora_leaves["Matricula"].astype(str)
                + "-"
                + ahgora_leaves["Data Inicio"].astype(str)
                + "-"
                + ahgora_leaves["Data Fim"].astype(str)
            )

            not_common_leaves = fiorilli_leaves[
                ~fiorilli_leaves["key"].isin(ahgora_leaves["key"])
            ].drop(columns=["key"])

            not_common_leaves.to_csv("no.csv", index=False, header=False)
            print(not_common_leaves)

            print("[bold green]Afastamentos comparados com sucesso![/bold green]\n")
            sleep(1)
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao analisar afastamentos: {e}[/bold red]\n")
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
        if not cols_names:
            cols_names = df.columns
        df.columns = cols_names

        for col in cols_names:
            if "Data" in col:
                df[col] = df[col].apply(self._convert_date)
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
                df[col] = df[col].dt.strftime("%d/%m/%Y")

        if "CPF" in cols_names:
            df["CPF"] = df["CPF"].fillna("").astype(str).str.zfill(11)

        if "Cod" in cols_names:
            df["Cod"] = df["Cod"].fillna("").astype(str).str.zfill(3)

        if "Nome" in cols_names:
            df["Nome"] = df["Nome"].str.strip().str.upper()

        if "Matricula" in cols_names:
            df["Matricula"] = df["Matricula"].astype(str).str.zfill(6)

        return df

    def _convert_date(self, data_str):
        meses = {
            "Jan": "Jan",
            "Fev": "Feb",
            "Mar": "Mar",
            "Abr": "Apr",
            "Mai": "May",
            "Jun": "Jun",
            "Jul": "Jul",
            "Ago": "Aug",
            "Set": "Sep",
            "Out": "Oct",
            "Nov": "Nov",
            "Dez": "Dec",
        }
        if pd.isna(data_str) or not isinstance(data_str, str):
            return None
        partes = data_str.split(", ")
        if len(partes) > 1:
            data_str = partes[1]
        for pt, en in meses.items():
            data_str = data_str.replace(f"{pt}/", f"{en}/")
        try:
            return pd.to_datetime(data_str, format="%d/%b/%Y", errors="raise")
        except ValueError:
            try:
                return pd.to_datetime(data_str, format="%d/%m/%Y", errors="raise")
            except ValueError:
                return pd.to_datetime(
                    data_str, format="%d/%b/%Y %H:%M", errors="coerce"
                )

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

    def _get_leaves_data(self) -> (pd.DataFrame, pd.DataFrame):
        fiorilli_leaves_path = self.data_dir_path / "fiorilli" / "leaves.txt"
        fiorilli_vacation_path = self.data_dir_path / "fiorilli" / "vacation.txt"
        ahgora_leaves_path = self.data_dir_path / "ahgora" / "leaves.csv"

        fiorilli_columns = [
            "Matricula",
            "Cod",
            "Data Inicio",
            "Hora Inicio",
            "Data Fim",
            "Hora Fim",
        ]
        # fiorilli_leaves = pd.concat(
        #     [
        #         self._read_csv(
        #             fiorilli_vacation_path,
        #             header=None,
        #             cols_names=fiorilli_columns,
        #         ),
        #         self._read_csv(
        #             fiorilli_leaves_path,
        #             header=None,
        #             cols_names=fiorilli_columns,
        #         ),
        #     ]
        # )

        fiorilli_leaves = self._read_csv(
            fiorilli_leaves_path,
            header=None,
            cols_names=fiorilli_columns,
        )

        ahgora_leaves = self._read_csv(
            ahgora_leaves_path,
            sep=";",
            cols_names=[
                "Nome",
                "Matricula",
                "Cod",
                "Motivo",
                "Data Inicio",
                "Data Fim",
            ],
        )

        return fiorilli_leaves, ahgora_leaves

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
