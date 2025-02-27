import numpy as np
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
    absences: pd.DataFrame | None


class DataManager:
    def __init__(self, working_dir_path: str, config: Config):
        self.data_dir_path = Path(working_dir_path) / "data"
        self.config = config

    def analyze(self) -> (pd.DataFrame, pd.DataFrame):
        try:
            print("--- Analisando dados de Funcionários entre Fiorilli e Ahgora ---\n")
            self.analyze_absences()
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
        absences_path = actions_dir / "absences.csv"

        ignore_list = self.config.data.get("ignore", {})
        ignore_ids = set(ignore_list.keys())

        actions = Actions(None, None, None)

        if new_employees_path.exists():
            df_new = self._read_csv(new_employees_path)
            df_new = df_new[~df_new["id"].isin(ignore_ids)]
            actions.to_add = df_new

        if dismissed_employees_path.exists():
            df_dismissed = self._read_csv(dismissed_employees_path)
            # df_dismissed = df_dismissed[~df_dismissed["id"].isin(ignore_ids)]
            actions.to_remove = df_dismissed

        if absences_path.exists():
            df_absences = self._read_csv(absences_path)
            actions.absences = df_absences

        return actions

    def analyze_absences(self):
        try:
            print("--- Analisando afastamentos entre Fiorilli e Ahgora ---\n")

            fiorilli_absences, ahgora_absences = self._get_absences_data()

            fiorilli_ids = set(fiorilli_absences["id"])
            ahgora_ids = set(ahgora_absences["id"])

            # no_fio = fiorilli_absences[~fiorilli_absences["id"].isin(ahgora_ids)]
            # no_agora = ahgora_absences[~ahgora_absences["id"].isin(fiorilli_ids)]

            fiorilli_absences["key"] = (
                fiorilli_absences["id"].astype(str)
                + "-"
                + fiorilli_absences["start_date"].astype(str)
                + "-"
                + fiorilli_absences["end_date"].astype(str)
            )

            ahgora_absences["key"] = (
                ahgora_absences["id"].astype(str)
                + "-"
                + ahgora_absences["start_date"].astype(str)
                + "-"
                + ahgora_absences["end_date"].astype(str)
            )

            not_common_absences = fiorilli_absences[
                ~fiorilli_absences["key"].isin(ahgora_absences["key"])
            ].drop(columns=["key"])

            not_common_absences.to_csv("data\\actions\\absences.csv", index=False, header=False)
            # print(not_common_absences)

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
        columns: list[str] = [],
    ):
        df = pd.read_csv(
            path,
            sep=sep,
            encoding=encoding,
            index_col=False,
            header=header,
            dtype={"id": str},
        )
        return self._prepare_dataframe(df=df, columns=columns)

    def _prepare_dataframe(self, df, columns: list[str] = []):
        if columns:
            df.columns = columns
        else:
            columns = df.columns

        for col in df.columns:
            if "date" in col:
                df[col] = df[col].apply(self._convert_date)
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
                df[col] = df[col].dt.strftime("%d/%m/%Y")

        if "cpf" in df.columns:
            df["cpf"] = df["cpf"].fillna("").astype(str).str.zfill(11)

        if "cod" in df.columns:
            df["cod"] = df["cod"].fillna("").astype(str).str.zfill(3)

        if "name" in df.columns:
            df["name"] = df["name"].str.strip().str.upper()

        if "id" in df.columns:
            df["id"] = df["id"].astype(str).str.zfill(6)

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
            return np.nan
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
            columns=[
                "id",
                "name",
                "cpf",
                "sex",
                "birth_date",
                "pis_pasep",
                "position",
                "location",
                "department",
                "binding",
                "admission_date",
                "dismissal_date",
            ],
        )

        ahgora_employees = self._read_csv(
            ahgora_employees_path,
            header=None,
            columns=[
                "id",
                "name",
                "position",
                "scale",
                "department",
                "location",
                "admission_date",
                "dismissal_date",
            ],
        )
        return fiorilli_employees, ahgora_employees

    def _get_absences_data(self) -> (pd.DataFrame, pd.DataFrame):
        fiorilli_absences_path = self.data_dir_path / "fiorilli" / "absences.txt"
        fiorilli_vacationss_path = self.data_dir_path / "fiorilli" / "vacations.txt"
        ahgora_absences_path = self.data_dir_path / "ahgora" / "absences.csv"

        fiorilli_columns = [
            "id",
            "cod",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
        ]
        # fiorilli_absences = pd.concat(
        #     [
        #         self._read_csv(
        #             fiorilli_vacations_path,
        #             header=None,
        #             columns=fiorilli_columns,
        #         ),
        #         self._read_csv(
        #             fiorilli_absences_path,
        #             header=None,
        #             columns=fiorilli_columns,
        #         ),
        #     ]
        # )

        fiorilli_absences = self._read_csv(
            fiorilli_absences_path,
            header=None,
            columns=fiorilli_columns,
        )
        ahgora_absences = self._read_csv(
            ahgora_absences_path,
            sep=";",
            columns=[
                "name",
                "id",
                "pis_pasep",
                "cpf",
                "cod",
                "admission_date",
                "birth_date",
                "position",
                "department",
                "branch",
                "regime",
                "cost_center",
                "location",
                "day",
                "scale",
                "week_day",
                "total_absence",
                "reason",
                "start_date",
                "end_date",
                "dismissal_date",
            ],
        )

        return fiorilli_absences, ahgora_absences

    def _generate_actions_dfs(
        self, fiorilli_employees: pd.DataFrame, ahgora_employees: pd.DataFrame
    ):
        fiorilli_dismissed_df = fiorilli_employees[
            fiorilli_employees["dismissal_date"].notna()
        ]
        fiorilli_dismissed_ids = set(fiorilli_dismissed_df["id"])

        ahgora_dismissed_df = ahgora_employees[
            ahgora_employees["dismissal_date"].notna()
        ]
        ahgora_dismissed_ids = set(ahgora_dismissed_df["id"])

        dismissed_ids = ahgora_dismissed_ids | fiorilli_dismissed_ids

        fiorilli_active_df = fiorilli_employees[
            ~fiorilli_employees["id"].isin(dismissed_ids)
        ]

        ahgora_ids = set(ahgora_employees["id"])

        new_employees = fiorilli_active_df[
            ~fiorilli_active_df["id"].isin(ahgora_ids)
        ]

        dismissed_employees = ahgora_employees[
            ahgora_employees["id"].isin(fiorilli_dismissed_ids)
            & ~ahgora_employees["id"].isin(ahgora_dismissed_ids)
        ]

        dismissed_employees = dismissed_employees.drop(columns=["dismissal_date"])
        dismissed_employees = dismissed_employees.merge(
            fiorilli_dismissed_df[["id", "dismissal_date"]],
            on="id",
            how="left",
        )

        return new_employees, dismissed_employees

        # merged_employees = fiorilli_employees.merge(
        #     ahgora_employees,
        #     on="id",
        #     suffixes=('_fiorilli', '_ahgora'),
        #     how="inner"
        # )
        #
        # changed_position_employees = merged_employees[
        #     merged_employees["position_fiorilli"] == merged_employees["position_ahgora"]
        # ]
        #
        # for i, r in merged_employees.iterrows():
        #     print(i)
        #     print(r)
        #     print('\n')
        #     print(type(r["dismissal_date_fiorilli"]))
        #     print(r["dismissal_date_fiorilli"] + 55)
        #     break
        # print("Pronto")
        # sleep(999)
        #
        # return new_employees, dismissed_employees, changed_position_employees
        #
        #
