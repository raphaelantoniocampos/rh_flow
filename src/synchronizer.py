import os

import chardet
from pandas import DataFrame, read_csv, to_datetime
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
        "Cod2",
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

    def run(self) -> DataFrame:
        try:
            print("--- Sincronizando dados de Funcionários entre Fiorilli e Ahgora ---")
            employees_data = self._get_employees_data()
            df_to_add, df_to_inactivate = self._process_data(employees_data)

            # df_to_add = df_to_add[
            #     [
            #         "Nome",
            #         "PIS-PASEP",
            #         "CPF",
            #         "Sexo",
            #         "Data Nascimento",
            #         "Matricula",
            #         "Data Admissao",
            #         "Cargo",
            #         "Localizacao",
            #     ]
            # ]

            # df_to_inactivate[
            #     ["Matricula", "Nome", "Data Admissao", "Departamento", "Cargo"]
            # ]

            print(f"{len(df_to_add)} Novos funcionários para adicionar no Ahgora")
            return df_to_add
            # _manual_add(df_to_inactivate, "remover/verificar")

            print("[bold green]Funcionários adicionados com sucesso![/bold green]")
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao adicionar funcionários: {e}[/bold red]")

    def _get_employees_data(self):
        fiorilli_employees_portable_path = os.path.join(
            self.data_dir, "fiorilli", "employees_portable.csv"
        )
        fiorilli_employees_path = os.path.join(
            self.data_dir, "fiorilli", "employees_all.txt"
        )
        ahgora_employees_path = os.path.join(
            self.data_dir, "ahgora", "employees_all.csv"
        )

        fiorilli_employees_portable = self._load(
            filepath=fiorilli_employees_path,
            sep="|",
            cols_names=self.FIORILLI_EMPLOYEES_COLUMNS,
        )

        fiorilli_employees = self._load(
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
        data = read_csv(
            filepath,
            sep=sep,
            encoding=encoding,
            index_col=False,
            dtype={"Matricula": str},
        )
        data.columns = cols_names

        data["Data Admissao"] = to_datetime(
            data["Data Admissao"], dayfirst=True, errors="coerce"
        )

        try:
            data["CPF"] = data["CPF"].fillna("").astype(str).str.zfill(11)
        except KeyError:
            pass
        data["Nome"] = data["Nome"].str.strip().str.upper()

        data["Matricula"] = data["Matricula"].astype(str).str.zfill(6)

        data = data.sort_values(by="Data Admissao", ascending=False)

        # if all(col in data.columns for col in id_columns):
        #     data = data.sort_values(by="Data Admissao", ascending=False)
        #     data = data.drop_duplicates(subset=id_columns, keep="first")

        return data

    def _detect_encoding(self, filepath: str):
        with open(filepath, "rb") as f:
            return chardet.detect(f.read())["encoding"]

    def _process_data(self, employees_data):
        fiorilli_employees = employees_data['fiorilli_employees']
        fiorilli_employees_portable = employees_data['fiorilli_employees_portable']
        ahgora_employees = employees_data['ahgora_employees']

        fiorilli_employees_portable["Matricula"] = fiorilli_employees["Matricula"].astype(str).str.strip()
        ahgora_employees["Matricula"] = ahgora_employees["Matricula"].astype(str).str.strip()

        fiorilli_employees_portable["Data Admissao"] = fiorilli_employees_portable["Data Admissao"].dt.strftime(
            "%d/%m/%Y"
        )
        ahgora_employees["Data Admissao"] = ahgora_employees["Data Admissao"].dt.strftime(
            "%d/%m/%Y"
        )

        new_to_add = set(fiorilli_employees_portable["Matricula"]) - set(ahgora_employees["Matricula"])

        inactivate_ahgora = set(ahgora_employees["Matricula"]) - set(
            fiorilli_employees_portable["Matricula"]
        )

        df_to_add = fiorilli_employees_portable[fiorilli_employees_portable["Matricula"].isin(new_to_add)]
        df_to_inactivate = ahgora_employees[ahgora_employees["Matricula"].isin(inactivate_ahgora)]

        return df_to_add, df_to_inactivate
