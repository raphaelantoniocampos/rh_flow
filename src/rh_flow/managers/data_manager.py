from time import sleep

import pandas as pd
from pandas.errors import EmptyDataError
from rich import print
from utils.constants import DATA_DIR
from managers.file_manager import FileManager


class DataManager:
    def analyze(self) -> (pd.DataFrame, pd.DataFrame):
        try:
            print("--- Analisando dados de Funcionários entre Fiorilli e Ahgora ---\n")
            ahgora_employees, fiorilli_employees = self._get_employees_raw_data()
            fiorilli_absences = self._get_absences_raw_data()

            FileManager.save_df(
                df=ahgora_employees,
                path=DATA_DIR / "ahgora" / "employees.csv",
            )
            FileManager.save_df(
                df=fiorilli_employees,
                path=DATA_DIR / "fiorilli" / "employees.csv",
            )
            FileManager.save_df(
                df=fiorilli_absences,
                path=DATA_DIR / "fiorilli" / "absences.csv",
            )

            self.save_tasks_dfs(fiorilli_employees, ahgora_employees, fiorilli_absences)

            print("[bold green]Dados sincronizados com sucesso![/bold green]\n")
            sleep(1)
        except KeyboardInterrupt as e:
            print(f"[bold red]Erro ao sincronizar dados: {e}[/bold red]\n")
            sleep(1)

    def save_tasks_dfs(self, fiorilli_employees, ahgora_employees, fiorilli_absences):
        new_df, dismissed_df, position_df, absences_df = self._generate_tasks_dfs(
            fiorilli_employees,
            ahgora_employees,
            fiorilli_absences,
        )

        save_dir = DATA_DIR / "tasks"

        FileManager.save_df(
            df=new_df,
            path=save_dir / "add_employees.csv",
        )
        FileManager.save_df(
            df=dismissed_df,
            path=save_dir / "dismissed_employees.csv",
        )
        FileManager.save_df(
            df=position_df,
            path=save_dir / "change_positions.csv",
        )
        FileManager.save_df(
            df=absences_df,
            path=save_dir / "add_absences.csv",
        )

    def _generate_tasks_dfs(
        self,
        fiorilli_employees: pd.DataFrame,
        ahgora_employees: pd.DataFrame,
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

        # TODO: verify characters on positions
        position_df = merged_employees[
            merged_employees["position_fiorilli"] != merged_employees["position_ahgora"]
        ]

        absences_df = fiorilli_absences

        return new_df, dismissed_df, position_df, absences_df

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

    def _get_employees_raw_data(self) -> (pd.DataFrame, pd.DataFrame):
        raw_fiorilli_employees = DATA_DIR / "fiorilli" / "raw_employees.txt"
        raw_ahgora_employees = DATA_DIR / "ahgora" / "raw_employees.csv"

        fiorilli_employees = self.read_csv(
            raw_fiorilli_employees,
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
            raw_ahgora_employees,
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
        return ahgora_employees, fiorilli_employees

    def _get_absences_raw_data(self) -> pd.DataFrame:
        raw_fiorilli_absences = DATA_DIR / "fiorilli" / "raw_absences.txt"
        raw_fiorilli_vacations = DATA_DIR / "fiorilli" / "raw_vacations.txt"

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
                        raw_fiorilli_vacations,
                        header=None,
                        columns=fiorilli_columns,
                    ),
                    self.read_csv(
                        raw_fiorilli_absences,
                        header=None,
                        columns=fiorilli_columns,
                    ),
                ]
            )
        except EmptyDataError:
            return pd.DataFrame
