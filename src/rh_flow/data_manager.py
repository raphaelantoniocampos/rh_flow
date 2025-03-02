import os
from pathlib import Path
from time import sleep

import pandas as pd
from rich import print


def read_csv(
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
    return prepare_dataframe(df=df, columns=columns)


def prepare_dataframe(df, columns: list[str] = []):
    if columns:
        df.columns = columns
    else:
        columns = df.columns

    for col in df.columns:
        if "date" in col:
            df[col] = df[col].apply(convert_date)
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


def convert_date(data_str):
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
            return pd.to_datetime(data_str, format="%d/%b/%Y %H:%M", errors="coerce")


class DataManager:
    def __init__(self, working_dir_path: str, config):
        self.data_dir_path = Path(working_dir_path) / "data"
        self.config = config

    def analyze(self) -> (pd.DataFrame, pd.DataFrame):
        try:
            # TODO: add progress bars
            print("--- Analisando dados de Funcionários entre Fiorilli e Ahgora ---\n")
            fiorilli_employees, ahgora_employees = self._get_employees_data()
            fiorilli_absences, ahgora_absences = self._get_absences_data()

            new_df, dismissed_df, position_df, absences_df = self._generate_actions_dfs(
                fiorilli_employees,
                ahgora_employees,
                ahgora_absences,
                fiorilli_absences,
            )

            save_dir = self.data_dir_path / "actions"

            if not new_df.empty:
                new_df.to_csv(
                    os.path.join(save_dir, "new.csv"),
                    index=False,
                    encoding="utf-8",
                )

            if not dismissed_df.empty:
                dismissed_df.to_csv(
                    os.path.join(save_dir, "dismissed.csv"),
                    index=False,
                    encoding="utf-8",
                )

            if not position_df.empty:
                position_df.to_csv(
                    os.path.join(save_dir, "position.csv"),
                    index=False,
                    encoding="utf-8",
                )

            if not absences_df.empty:
                absences_df.to_csv(
                    Path(self.data_dir_path / "actions" / "absences.csv"),
                    index=False,
                    header=False,
                )

            self.config.update_last_analisys()
            print("[bold green]Dados sincronizados com sucesso![/bold green]\n")
            sleep(1)
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao adicionar funcionários: {e}[/bold red]\n")
            sleep(1)

    # def analyze_absences(self):
    #     try:
    #         print("--- Analisando afastamentos entre Fiorilli e Ahgora ---\n")
    #
    #
    #         # fiorilli_ids = set(fiorilli_absences["id"])
    #         # ahgora_ids = set(ahgora_absences["id"])
    #
    #         # no_fio = fiorilli_absences[~fiorilli_absences["id"].isin(ahgora_ids)]
    #         # no_agora = ahgora_absences[~ahgora_absences["id"].isin(fiorilli_ids)]
    #
    #         fiorilli_absences["key"] = (
    #             fiorilli_absences["id"].astype(str)
    #             + "-"
    #             + fiorilli_absences["start_date"].astype(str)
    #             + "-"
    #             + fiorilli_absences["end_date"].astype(str)
    #         )
    #
    #         ahgora_absences["key"] = (
    #             ahgora_absences["id"].astype(str)
    #             + "-"
    #             + ahgora_absences["start_date"].astype(str)
    #             + "-"
    #             + ahgora_absences["end_date"].astype(str)
    #         )
    #
    #         not_common_absences = fiorilli_absences[
    #             ~fiorilli_absences["key"].isin(ahgora_absences["key"])
    #         ].drop(columns=["key"])
    #
    #         not_common_absences.to_csv(
    #             Path(self.data_dir_path / "actions" / "absences.csv"),
    #             index=False,
    #             header=False,
    #         )
    #
    #         print("[bold green]Afastamentos comparados com sucesso![/bold green]\n")
    #         sleep(1)
    #     except KeyboardInterrupt as e:
    #         print(f"[bold red]Erro ao analisar afastamentos: {e}[/bold red]\n")
    #         sleep(1)

    def _get_employees_data(self) -> (pd.DataFrame, pd.DataFrame):
        fiorilli_employees_path = self.data_dir_path / "fiorilli" / "employees.txt"
        ahgora_employees_path = self.data_dir_path / "ahgora" / "employees.csv"

        fiorilli_employees = read_csv(
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

        ahgora_employees = read_csv(
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
        fiorilli_vacations_path = self.data_dir_path / "fiorilli" / "vacations.txt"
        ahgora_absences_path = self.data_dir_path / "ahgora" / "absences.csv"

        fiorilli_columns = [
            "id",
            "cod",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
        ]

        fiorilli_absences = pd.concat(
            [
                read_csv(
                    fiorilli_vacations_path,
                    header=None,
                    columns=fiorilli_columns,
                ),
                read_csv(
                    fiorilli_absences_path,
                    header=None,
                    columns=fiorilli_columns,
                ),
            ]
        )

        fiorilli_absences = read_csv(
            fiorilli_absences_path,
            header=None,
            columns=fiorilli_columns,
        )
        ahgora_absences = read_csv(
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
                "reason_cod",
                "reason",
                "start_date",
                "end_date",
                "dismissal_date",
            ],
        )

        return fiorilli_absences, ahgora_absences

    def _split_absence(self, fiorilli_row, ahgora_absences_for_employee):
        f_start = fiorilli_row["start_date"]
        f_end = fiorilli_row["end_date"]

        # Filtrar ausências do Ahgora que sobrepõem com o Fiorilli
        mask = (ahgora_absences_for_employee["start_date"] <= f_end) & (
            ahgora_absences_for_employee["end_date"] >= f_start
        )
        overlaps = ahgora_absences_for_employee[mask].sort_values(by="start_date")

        new_periods = []
        current_start = f_start

        for _, overlap in overlaps.iterrows():
            a_start = overlap["start_date"]
            a_end = overlap["end_date"]

            if current_start < a_start:
                new_periods.append((current_start, a_start - pd.Timedelta(days=1)))

            print(a_start)
            print(a_end)
            current_start = max(current_start, a_end + pd.Timedelta(days=1))

        if current_start <= f_end:
            new_periods.append((current_start, f_end))

        # Gerar novas linhas para cada período não sobreposto
        new_rows = []
        for start, end in new_periods:
            new_row = fiorilli_row.copy()
            new_row["start_date"] = start
            new_row["end_date"] = end
            new_rows.append(new_row)

        return new_rows

    def _generate_actions_dfs(
        self,
        fiorilli_employees: pd.DataFrame,
        ahgora_employees: pd.DataFrame,
        ahgora_absences: pd.DataFrame,
        fiorilli_absences: pd.DataFrame,
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

        new_df = fiorilli_active_df[~fiorilli_active_df["id"].isin(ahgora_ids)]

        dismissed_df = ahgora_employees[
            ahgora_employees["id"].isin(fiorilli_dismissed_ids)
            & ~ahgora_employees["id"].isin(ahgora_dismissed_ids)
        ]

        dismissed_df = dismissed_df.drop(columns=["dismissal_date"])
        dismissed_df = dismissed_df.merge(
            fiorilli_dismissed_df[["id", "dismissal_date"]],
            on="id",
            how="left",
        )

        merged_employees = fiorilli_employees.merge(
            ahgora_employees, on="id", suffixes=("_fiorilli", "_ahgora"), how="inner"
        )

        position_df = merged_employees[
            merged_employees["position_fiorilli"] != merged_employees["position_ahgora"]
        ]

        # Agrupar ausências do Ahgora por ID para busca eficiente
        ahgora_absences_grouped = ahgora_absences.groupby("id")

        split_absences = []

        # Processar cada ausência do Fiorilli
        for _, f_row in fiorilli_absences.iterrows():
            employee_id = f_row["id"]

            # Obter ausências do Ahgora para o mesmo funcionário
            if employee_id in ahgora_absences_grouped.groups:
                ahgora_for_employee = ahgora_absences_grouped.get_group(employee_id)
            else:
                ahgora_for_employee = pd.DataFrame()

            # Dividir ausência do Fiorilli em períodos não sobrepostos
            split_rows = self._split_absence(f_row, ahgora_for_employee)
            split_absences.extend(split_rows)

        absences_df = pd.DataFrame(split_absences).drop(
            columns=["key"], errors="ignore"
        )

        # fiorilli_absences["key"] = (
        #     fiorilli_absences["id"].astype(str)
        #     + "-"
        #     + fiorilli_absences["start_date"].astype(str)
        #     + "-"
        #     + fiorilli_absences["end_date"].astype(str)
        # )
        #
        # ahgora_absences["key"] = (
        #     ahgora_absences["id"].astype(str)
        #     + "-"
        #     + ahgora_absences["start_date"].astype(str)
        #     + "-"
        #     + ahgora_absences["end_date"].astype(str)
        # )
        #
        # absences_df = fiorilli_absences[
        #     ~fiorilli_absences["key"].isin(ahgora_absences["key"])
        # ].drop(columns=["key"])

        return new_df, dismissed_df, position_df, absences_df
