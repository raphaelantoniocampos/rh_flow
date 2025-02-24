import pandas as pd
from datetime import datetime, timedelta
from rich.console import Console
import inquirer
from rich import print
from rich.panel import Panel

from pathlib import Path
import json

INIT_CONFIG = {
    "ignore": {},
    "last_analisys": {"datetime": "", "time_since": ""},
    "last_download": {
        "ahgora": {"datetime": "", "time_since": ""},
        "fiorilli": {"datetime": "", "time_since": ""},
    },
}


class Config:
    def __init__(self, data_dir_path: Path):
        self.data_dir_path = data_dir_path
        self.path: Path = data_dir_path / "config.json"
        self.data: dict = self._load()
        self._update_time_since()

    def config_panel(self, console: Console) -> None:
        while True:
            config_data = self._read()
            ignore_data = config_data.get("ignore", {})
            last_analisys = self.data.get(
                "last_analisys", {"datetime": "", "time_since": ""}
            )
            last_download = self.data.get(
                "last_download", {"datetime": "", "time_since": ""}
            )

            console.print(
                Panel.fit("[bold]Configurações[/bold]", border_style="yellow")
            )

            console.print(
                f"""
[cyan]•[/] [bold]Último download[/]: {last_download["datetime"]} ([bold]{last_download["time_since"]}[/] atrás)
[cyan]•[/] [bold]Última análise[/]: {last_analisys["datetime"]} ([bold]{last_analisys["time_since"]}[/] atrás)
                """
            )

            questions = [
                inquirer.List(
                    "action",
                    message="O que deseja fazer?",
                    choices=["Ver lista de ignorados", "Voltar"],
                ),
            ]

            answers = inquirer.prompt(questions)
            action = answers["action"]

            if action == "Voltar":
                return

            if action == "Ver lista de ignorados":
                ignored_list = [
                    f"{id} - {data['Data Admissao']} - {data['Nome']} - {data['Vinculo']}"
                    for id, data in ignore_data.items()
                ]

                console.print(
                    Panel.fit(
                        "[bold]Funcionários Ignorados[/bold]", border_style="yellow"
                    )
                )

                if not ignored_list:
                    print(
                        "[bold yellow]Nenhum funcionário está sendo ignorado no momento.[/bold yellow]\n"
                    )

                else:
                    for ignored in ignored_list:
                        console.print(ignored)

                questions = [
                    inquirer.List(
                        "action",
                        message="O que deseja fazer?",
                        choices=["Remover um funcionário", "Voltar"],
                    ),
                ]

                answers = inquirer.prompt(questions)
                action = answers["action"]

                if action == "Voltar":
                    continue

                if action == "Remover um funcionário":
                    questions = [
                        inquirer.Checkbox(
                            "remove_ignore",
                            message="Escolha os funcionários para remover da lista de ignorados.",
                            choices=ignored_list,
                        ),
                    ]
                    remove_ignore = inquirer.prompt(questions).get("remove_ignore")

                    for employee in remove_ignore:
                        self._delete("ignore", employee[:6])
                        console.print(
                            f"[bold green]Funcionário com matrícula {employee[:6]} removido da lista de ignorados.[/bold green]"
                        )

    def update_employees_to_ignore(self, df: pd.DataFrame) -> pd.DataFrame:
        employees_dict = {
            str(series["Matricula"]): {
                "Matricula": series["Matricula"],
                "Data Admissao": series["Data Admissao"],
                "Nome": series["Nome"],
                "Vinculo": series["Vinculo"],
            }
            for _, series in df.iterrows()
        }
        employees_list = [
            f"{id} - {data['Data Admissao']} - {data['Nome']} - {data['Vinculo']}"
            for id, data in employees_dict.items()
        ]

        questions = [
            inquirer.Checkbox(
                "ignore",
                message="Matricula - Data Admissao - Nome - Vinculo",
                choices=employees_list,
            )
        ]

        print("Selecione os funcionários para ignorar")
        employees_to_ignore = inquirer.prompt(questions).get("ignore")

        to_ignore_dict = {
            ignore.split(" - ")[0]: employees_dict[ignore.split(" - ")[0]]
            for ignore in employees_to_ignore
        }

        self._update("ignore", to_ignore_dict)

        return df[~df["Matricula"].isin(to_ignore_dict.keys())]

    def _load(self) -> dict:
        if self.path.exists():
            with open(self.path, "r") as f:
                return json.load(f)
        else:
            return self._create()

    def _read(self) -> dict:
        return self.data

    def _update(self, *keys, value=None) -> dict:
        data = self.data
        *path, last_key = keys

        for key in path:
            if key not in data or not isinstance(data[key], dict):
                data[key] = {}
            data = data[key]

        if isinstance(data.get(last_key), dict) and isinstance(value, dict):
            data[last_key].update(value)
        else:
            data[last_key] = value

        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

        return self.data

    def _create(self) -> dict:
        with open(self.path, "w") as f:
            json.dump(INIT_CONFIG, f, indent=4)
        return INIT_CONFIG

    def _delete(self, field: str, key: str) -> str:
        if field in self.data and key in self.data[field]:
            del self.data[field][key]
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=4)
            return f"Item '{key}' removido do campo '{field}'."
        else:
            return f"Item '{key}' não encontrado no campo '{field}'."

    def _format_timedelta(self, td: timedelta) -> str:
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"

    def _update_time_since(self) -> None:
        now = datetime.now()
        last_analisys = self.data.get("last_analisys")
        self._update_analysis_time_since(last_analisys, now)

        last_download = self.data.get("last_download")
        print(last_download)
        print(type(last_download))
        self._update_downloads_time_since(last_download, "ahgora", now)
        # self._update_downloads_time_since(last_download, "fiorilli", now)

    def _update_analysis_time_since(self, last_analisys: dict, now: timedelta) -> None:
        if last_analisys["datetime"]:
            last_analisys_dt = datetime.strptime(
                last_analisys["datetime"], "%d/%m/%Y, %H:%M"
            )
            time_since_last_analisys = now - last_analisys_dt
            last_analisys["time_since"] = self._format_timedelta(
                time_since_last_analisys
            )
            self._update("last_analisys", value=last_analisys)

    def _update_downloads_time_since(self, last_download: dict, app_name: str, now: timedelta) -> None:
        app_last_download = last_download.get(app_name)

        print(f"{app_name}")

        if app_last_download["datetime"]:
            last_download_dt = datetime.strptime(
                app_last_download["datetime"], "%d/%m/%Y, %H:%M"
            )
            time_since_last_download = now - last_download_dt
            app_last_download["time_since"] = self._format_timedelta(
                time_since_last_download
            )
            print(app_last_download)
            self._update("last_download", app_name, "datetime",value=app_last_download)
        else:
            app_last_download = self._get_last_download(app_name)
            # self._update("last_download", app_name, "datetime", value=app_last_download)

    def _get_last_download(self, app_name: str) -> str:
        return datetime.strftime(
            datetime.fromtimestamp(
                Path(
                    self.data_dir_path
                    / app_name
                    / f"employees.{'csv' if app_name == 'ahgora' else 'txt'}"
                )
                .stat()
                .st_ctime
            ),
            "%d/%m/%Y, %H:%M",
        )

    def __str__(self):
        str_return = ""
        for key, value in self._read().items():
            str_return += f"{key}: {value}\n"

        return str_return
