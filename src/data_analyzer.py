import os

import chardet
import pandas as pd
from rich import print


class DataAnalyzer:
    FIORILLI_EMPLOYEES_COLUMNS = [
        "Matricula",
        "Nome",
        "CPF",
        "Sexo",
        "Data Nascimento",
        "PIS-PASEP",
        "Cargo",
        "Localizacao",
        "Departamento",
        "Data Admissao",
        "Data Desligamento",
    ]

    AHGORA_EMPLOYEES_COLUMNS = [
        "Matricula",
        "Nome",
        "Cargo",
        "Escala",
        "Departamento",
        "Localizacao",
        "Data Admissao",
        "NaN",
    ]

    def __init__(self, working_dir: str):
        self.working_dir = working_dir
        self.data_dir = os.path.join(working_dir, "data")

    def run(self) -> (pd.DataFrame, pd.DataFrame):
        try:
            print("--- Sincronizando dados de Funcionários entre Fiorilli e Ahgora ---")
            fiorilli_employees, ahgora_employees = self._get_employees_data()
            new_employees, dismissed_employees = self._process_data(
                fiorilli_employees, ahgora_employees
            )

            save_dir = os.path.join(self.data_dir, "to_process")
            if not new_employees.empty:
                new_employees.to_csv(os.path.join(save_dir, "new_employees.csv"), index=False)

            if not dismissed_employees.empty:
                dismissed_employees.to_csv(os.path.join(save_dir, "dismissed_employees.csv"), index=False)

            print("[bold green]Dados sincronizados com sucesso![/bold green]")
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao adicionar funcionários: {e}[/bold red]")

    def _get_employees_data(self) -> (pd.DataFrame, pd.DataFrame):
        fiorilli_employees_path = os.path.join(
            self.data_dir, "fiorilli", "employees.txt"
        )
        ahgora_employees_path = os.path.join(self.data_dir, "ahgora", "employees.csv")

        fiorilli_employees = self._load(
            filepath=fiorilli_employees_path,
            sep="|",
            cols_names=self.FIORILLI_EMPLOYEES_COLUMNS,
        )

        ahgora_employees = self._load(
            filepath=ahgora_employees_path,
            sep=",",
            cols_names=self.AHGORA_EMPLOYEES_COLUMNS,
        )

        return fiorilli_employees, ahgora_employees

    def _load(
        self,
        filepath: str,
        sep: str,
        cols_names: list[str],
    ):
        encoding = self._detect_encoding(filepath)
        data = pd.read_csv(
            filepath,
            sep=sep,
            encoding=encoding,
            index_col=False,
            dtype={"Matricula": str},
        )
        data.columns = cols_names

        data["Data Admissao"] = pd.to_datetime(
            data["Data Admissao"], dayfirst=True, errors="coerce"
        )

        try:
            data["CPF"] = data["CPF"].fillna("").astype(str).str.zfill(11)
        except KeyError:
            pass
        data["Nome"] = data["Nome"].str.strip().str.upper()

        data["Matricula"] = data["Matricula"].astype(str).str.zfill(6)

        data = data.sort_values(by="Data Admissao", ascending=False)

        return data

    def _detect_encoding(self, filepath: str):
        with open(filepath, "rb") as f:
            return chardet.detect(f.read())["encoding"]

    def _process_data(
        self, fiorilli_employees: pd.DataFrame, ahgora_employees: pd.DataFrame
    ):
        self._standardize_employee_id(fiorilli_employees)
        self._process_date(fiorilli_employees)

        self._standardize_employee_id(ahgora_employees)
        self._process_date(ahgora_employees)

        dismissed_df = self._filter_active_employees(fiorilli_employees)
        dismissed_ids = set(dismissed_df["Matricula"])

        ahgora_ids = set(ahgora_employees["Matricula"])

        active_employees_df = fiorilli_employees[
            ~fiorilli_employees["Matricula"].isin(dismissed_ids)
        ]

        new_employees = active_employees_df[
            ~active_employees_df["Matricula"].isin(ahgora_ids)
        ]

        dismissed_employees = ahgora_employees[
            ahgora_employees["Matricula"].isin(dismissed_ids)
        ]

        return new_employees, dismissed_employees

    def _standardize_employee_id(self, df: pd.DataFrame) -> None:
        df["Matricula"] = df["Matricula"].astype(str).str.strip()

    def _filter_active_employees(self, fiorilli_employees: pd.DataFrame) -> pd.DataFrame:
        dismissed_df = fiorilli_employees[fiorilli_employees["Data Desligamento"].notna()]
        return dismissed_df

    def _process_date(self, df: pd.DataFrame) -> None:
        df["Data Admissao"] = df["Data Admissao"].dt.strftime("%d/%m/%Y")

    def _calculate_id_differences(
        self, portable_df, ahgora_df, dismissed_df
    ) -> (pd.DataFrame, pd.DataFrame):
        portable_ids = set(portable_df["Matricula"])
        ahgora_ids = set(ahgora_df["Matricula"])
        dismissed_ids = set(dismissed_df["Matricula"])

        new_employees = portable_ids - ahgora_ids
        dismissed_employees = ahgora_ids - dismissed_ids

        return new_employees, dismissed_employees
