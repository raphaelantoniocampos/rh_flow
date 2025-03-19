from utils.constants import DATA_DIR
from time import sleep

import pandas as pd
from pandas.errors import EmptyDataError
from rich import print


class DataManager:
    def analyze(self) -> (pd.DataFrame, pd.DataFrame):
        try:
            # TODO: add progress bars
            print("--- Analisando dados de Funcionários entre Fiorilli e Ahgora ---\n")
            ahgora_employees, fiorilli_employees = self._get_employees_data()
            fiorilli_absences = self._get_fiorilli_absences()

            return ahgora_employees, fiorilli_employees, fiorilli_absences

            # new_df, dismissed_df, position_df, absences_df = self._generate_tasks_dfs(
            #     fiorilli_employees,
            #     ahgora_employees,
            #     fiorilli_absences,
            # )
            #
            # save_dir = DATA_DIR / "tasks"
            #
            # if not new_df.empty:
            #     new_df.to_csv(
            #         Path(save_dir / "new.csv"),
            #         index=False,
            #         encoding="utf-8",
            #     )
            #
            # if not dismissed_df.empty:
            #     dismissed_df.to_csv(
            #         Path(save_dir / "dismissed.csv"),
            #         index=False,
            #         encoding="utf-8",
            #     )
            #
            # if not position_df.empty:
            #     position_df.to_csv(
            #         Path(save_dir / "position.csv"),
            #         index=False,
            #         encoding="utf-8",
            #     )
            #
            # if not absences_df.empty:
            #     absences_df.to_csv(
            #         Path(save_dir / "absences.txt"),
            #         index=False,
            #         header=False,
            #         encoding="utf-8",
            #     )

            print("[bold green]Dados sincronizados com sucesso![/bold green]\n")
            sleep(1)
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao sincronizar dados: {e}[/bold red]\n")
            sleep(1)

    @staticmethod
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
        )
        return DataManager.prepare_dataframe(df=df, columns=columns)

    @staticmethod
    def prepare_dataframe(df, columns: list[str] = []):
        if columns:
            df.columns = columns
        else:
            columns = df.columns

        for col in df.columns:
            if "date" in col:
                df[col] = df[col].apply(DataManager.convert_date)
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

    @staticmethod
    def convert_date(date_str):
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
        not_a_date = (
            pd.isna(date_str) or not isinstance(date_str, str) or date_str == " "
        )

        if not_a_date:
            return pd.NaT

        partes = date_str.split(", ")
        if len(partes) > 1:
            date_str = partes[1]
        for pt, en in meses.items():
            date_str = date_str.replace(f"{pt}/", f"{en}/")
        try:
            return pd.to_datetime(date_str, format="%d/%b/%Y", errors="raise")
        except ValueError:
            try:
                return pd.to_datetime(date_str, format="%d/%m/%Y", errors="raise")
            except ValueError:
                try:
                    return pd.to_datetime(
                        date_str, format="%d/%b/%Y %H:%M", errors="raise"
                    )
                except ValueError:
                    return pd.to_datetime(date_str, format="ISO8601", errors="coerce")

    def _get_employees_data(self) -> (pd.DataFrame, pd.DataFrame):
        fiorilli_employees_path = DATA_DIR / "fiorilli" / "employees.txt"
        ahgora_employees_path = DATA_DIR / "ahgora" / "employees.csv"

        fiorilli_employees = self.read_csv(
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

        ahgora_employees = self.read_csv(
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
        return (
            ahgora_employees,
            fiorilli_employees,
        )

    def _get_fiorilli_absences(self) -> pd.DataFrame:
        fiorilli_absences_path = DATA_DIR / "fiorilli" / "absences.txt"
        fiorilli_vacations_path = DATA_DIR / "fiorilli" / "vacations.txt"

        try:
            fiorilli_columns = [
                "id",
                "cod",
                "start_date",
                "start_time",
                "end_date",
                "end_time",
            ]

            return pd.concat(
                [
                    self.read_csv(
                        fiorilli_vacations_path,
                        header=None,
                        columns=fiorilli_columns,
                    ),
                    self.read_csv(
                        fiorilli_absences_path,
                        header=None,
                        columns=fiorilli_columns,
                    ),
                ]
            )
        except EmptyDataError:
            return pd.DataFrame
