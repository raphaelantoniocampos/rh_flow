import os

import chardet
import pandas as pd
from rich import print


class Synchronizer:
    FIORILLI_EMPLOYEES_PORTABLE_COLUMNS = [
        "Matricula",
        "Nome",
        "PIS-PASEP",
        "Cod",
        "Cargo",
        "Localizacao",
        "Cod2",
        "Data Admissao",
        "Departamento",
        "CPF",
        "Data Nascimento",
        "Sexo",
        "NaN",
    ]

    FIORILLI_EMPLOYEES_COLUMNS = [
        "Matricula",
        "CPF",
        "Nome",
        "Telefone",
        "Cod",
        "Data Admissao",
        "Data Desligamento",
        "PIS-PASEP",
        "Cargo",
        "Cod3",
        "Departamento",
        "Cod4",
        "Localizacao",
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
            employees_data = self._get_employees_data()
            new_employees, dismissed_employees = self._process_data(employees_data)

            new_employees = new_employees[
                [
                    "Nome",
                    "PIS-PASEP",
                    "CPF",
                    "Sexo",
                    "Data Nascimento",
                    "Matricula",
                    "Data Admissao",
                    "Cargo",
                    "Localizacao",
                ]
            ]

            dismissed_employees[
                ["Matricula", "Nome", "Departamento", "Cargo", "Data Admissao", "Data Desligamento" ]
            ]

            return new_employees, dismissed_employees

            print("[bold green]Funcionários adicionados com sucesso![/bold green]")
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao adicionar funcionários: {e}[/bold red]")

    def _get_employees_data(self) -> dict[str, pd.DataFrame]:
        fiorilli_employees_path = os.path.join(
            self.data_dir, "fiorilli", "employees.txt"
        )
        fiorilli_employees_portable_path = os.path.join(
            self.data_dir, "fiorilli", "employees_portable.csv"
        )
        ahgora_employees_path = os.path.join(self.data_dir, "ahgora", "employees.csv")

        fiorilli_employees = self._load(
            filepath=fiorilli_employees_path,
            sep="|",
            cols_names=self.FIORILLI_EMPLOYEES_COLUMNS,
        )

        fiorilli_employees_portable = self._load(
            filepath=fiorilli_employees_portable_path,
            sep=";",
            cols_names=self.FIORILLI_EMPLOYEES_PORTABLE_COLUMNS,
        )

        ahgora_employees = self._load(
            filepath=ahgora_employees_path,
            sep=",",
            cols_names=self.AHGORA_EMPLOYEES_COLUMNS,
        )

        employees_data = {
            "fiorilli_employees_portable": fiorilli_employees_portable,
            "fiorilli_employees": fiorilli_employees,
            "ahgora_employees": ahgora_employees,
        }

        return employees_data

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

    def _process_data(self, employees_data: dict[str, pd.DataFrame]):
        for df_key in [
            "fiorilli_employees",
            "fiorilli_employees_portable",
            "ahgora_employees",
        ]:
            self._standardize_employee_id(employees_data[df_key])

        dismissed_df = self._filter_active_employees(
            employees_data["fiorilli_employees"]
        )
        self._process_date(employees_data["fiorilli_employees_portable"])
        self._process_date(employees_data["ahgora_employees"])

        new_employees, dismissed_employees = self._calculate_id_differences(
            portable_df=employees_data["fiorilli_employees_portable"],
            ahgora_df=employees_data["ahgora_employees"],
            dismissed_df=dismissed_df,
        )

        debugger = (
            employees_data["fiorilli_employees_portable"][
                employees_data["fiorilli_employees_portable"]["Matricula"].isin(
                    new_employees
                )
            ],
            employees_data["fiorilli_employees_portable"][
                employees_data["fiorilli_employees_portable"]["Matricula"].isin(
                    dismissed_employees
                )
            ],
        )

        # print(debugger[0])

        return (
            employees_data["fiorilli_employees_portable"][
                employees_data["fiorilli_employees_portable"]["Matricula"].isin(
                    new_employees
                )
            ],
            employees_data["fiorilli_employees"][
                employees_data["fiorilli_employees"]["Matricula"].isin(
                    dismissed_employees
                )
            ],
        )

        # OLD
        # fiorilli_employees_portable = employees_data["fiorilli_employees_portable"]
        # fiorilli_employees_portable["Matricula"] = (
        #     fiorilli_employees_portable["Matricula"].astype(str).str.strip()
        # )
        # fiorilli_employees_portable["Data Admissao"] = fiorilli_employees_portable[
        #     "Data Admissao"
        # ].dt.strftime("%d/%m/%Y")
        #
        # ahgora_employees = employees_data["ahgora_employees"]
        # ahgora_employees["Matricula"] = (
        #     ahgora_employees["Matricula"].astype(str).str.strip()
        # )
        # ahgora_employees["Data Admissao"] = ahgora_employees[
        #     "Data Admissao"
        # ].dt.strftime("%d/%m/%Y")
        #
        # new_employees = set(fiorilli_employees_portable["Matricula"]) - set(
        #     ahgora_employees["Matricula"]
        # )
        #
        # dismissed_employees = set(ahgora_employees["Matricula"]) - set(
        #     fiorilli_employees["Matricula"]
        # )
        #
        # df_to_add = fiorilli_employees_portable[
        #     fiorilli_employees_portable["Matricula"].isin(new_employees)
        # ]
        # df_to_inactivate = ahgora_employees[
        #     ahgora_employees["Matricula"].isin(dismissed_employees)
        # ]
        #
        # return df_to_add, df_to_inactivate

    def _standardize_employee_id(self, df: pd.DataFrame) -> None:
        df["Matricula"] = df["Matricula"].astype(str).str.strip()

    def _filter_active_employees(self, df: pd.DataFrame) -> pd.DataFrame:
        df["Data Desligamento"] = pd.to_datetime(
            df["Data Desligamento"], errors="coerce"
        )
        df["Data Desligamento"] = df["Data Desligamento"].dt.strftime("%d/%m/%Y")
        df = df[(df["Data Desligamento"].notna()) & (df["Data Desligamento"] != "")]
        return df

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
