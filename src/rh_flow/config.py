import json
from datetime import datetime, timedelta
from pathlib import Path

import inquirer
import pandas as pd
from action import Action
from rich import print
from rich.console import Console
from rich.panel import Panel

NO_IGNORED_STR = (
    "\n    [yellow]• Nenhum funcionário está sendo ignorado no momento.[/]\n"
)


class Config:
    def __init__(self, working_dir_path: Path):
        self.data_dir_path = Path(working_dir_path / "data")
        self.path: Path = self.data_dir_path / "config.json"
        self.data: dict = self._load()
        self._update_time_since()
        self._move_files_from_download(working_dir_path)

    def config_panel(self, console: Console) -> None:
        while True:
            config_data = self._read()
            ignore_data = config_data.get("ignore")
            last_analisys = self.data.get("last_analisys")
            last_download = self.data.get("last_download")

            console.print(
                Panel.fit("[bold]Configurações[/bold]", border_style="yellow")
            )

            ignored_list = [
                f"{id} - {data['admission_date']} - {data['name']} - {data['binding']}"
                for id, data in ignore_data.items()
            ]

            console.print(
                f"""
[cyan]•[/] [bold]Última análise[/]: {last_analisys["datetime"]} ([bold]{
                    last_analisys["time_since"]
                }[/] atrás)

[cyan]•[/] [bold]Últimos downloads[/]: 
    • Fiorilli - {last_download["fiorilli"]["datetime"]} ([bold]{
                    last_download["fiorilli"]["time_since"]
                }[/] atrás)
    • Ahgora - {last_download["ahgora"]["datetime"]} ([bold]{
                    last_download["ahgora"]["time_since"]
                }[/] atrás)

[cyan]•[/] [bold]Lista de funcionários ignorados[/]: 
{
                    NO_IGNORED_STR
                    if not ignored_list
                    else "\n".join([f"    • {ignored}" for ignored in ignored_list])
                }
"""
            )

            questions = [
                inquirer.List(
                    "action",
                    message="O que deseja fazer?",
                    choices=["Remover funcionários da lista de ignorados", "Voltar"],
                ),
            ]

            answers = inquirer.prompt(questions)
            action = answers["action"]

            if action == "Voltar":
                return

            if action == "Remover funcionários da lista de ignorados":
                if not ignored_list:
                    print(NO_IGNORED_STR)
                    continue

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

    def update_employees_to_ignore(self, action: Action) -> pd.DataFrame:
        ignore_dict = action.get_ignore_dict()
        ignore_list = action.get_ignore_list(ignore_dict)
        questions = [
            inquirer.Checkbox(
                "ignore",
                message="Selecione os funcionários para ignorar",
                choices=ignore_list,
            )
        ]

        employees_to_ignore = inquirer.prompt(questions).get("ignore")

        to_ignore_dict = {
            ignore.split(" - ")[0]: ignore_dict[ignore.split(" - ")[0]]
            for ignore in employees_to_ignore
        }

        self._update("ignore", value=to_ignore_dict)

        return action.df[~action.df["id"].isin(to_ignore_dict.keys())]

    def update_last_analisys(self):
        now = datetime.now()
        last_analisys = {"datetime": now.strftime("%d/%m/%Y, %H:%M"), "time_since": now}
        self._update_analysis_time_since(last_analisys, now)

    def _move_files_from_download(self, working_dir_path: Path):
        downloads_path = Path(working_dir_path / "downloads")
        for file in downloads_path.iterdir():
            if "trabalhador" in file.name.lower():
                file.replace(self.data_dir_path / "fiorilli" / "employees.txt")
            if "funcionarios" in file.name.lower():
                file.replace(self.data_dir_path / "ahgora" / "employees.csv")
            if "tabledownloadcsv" in file.name.lower():
                file.replace(self.data_dir_path / "ahgora" / "absences.csv")
            if "pontoafastamentos" in file.name.lower():
                file.replace(self.data_dir_path / "fiorilli" / "absences.txt")
            if "pontoferias" in file.name.lower():
                file.replace(self.data_dir_path / "fiorilli" / "vacations.txt")

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
            init_config = {
                "init_date": datetime.now().strftime("%d/%m/%Y, %H:%M"),
                "ignore": {},
                "last_analisys": {"datetime": "", "time_since": ""},
                "last_download": {
                    "ahgora": {"datetime": "", "time_since": ""},
                    "fiorilli": {"datetime": "", "time_since": ""},
                },
            }
            json.dump(init_config, f, indent=4)
        return init_config

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
        try:
            now = datetime.now()
            last_analisys = self.data.get("last_analisys")
            self._update_analysis_time_since(last_analisys, now)

            last_download = self.data.get("last_download")
            self._update_downloads_time_since(last_download, "ahgora", now)
            self._update_downloads_time_since(last_download, "fiorilli", now)
        except FileNotFoundError as error:
            raise Exception(
                f"{error}\nBaixe o arquivo e o coloque na pasta solicitada."
            )

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

    def _update_downloads_time_since(
        self, last_download: dict, app_name: str, now: timedelta
    ) -> None:
        app_last_download = last_download.get(app_name)

        app_last_download["datetime"] = self._get_last_download(app_name)

        last_download_dt = datetime.strptime(
            app_last_download["datetime"], "%d/%m/%Y, %H:%M"
        )
        time_since_last_download = now - last_download_dt
        app_last_download["time_since"] = self._format_timedelta(
            time_since_last_download
        )

        self._update("last_download", app_name, value=app_last_download)

    def _get_last_download(self, app_name: str) -> str:
        file_path = Path(
            self.data_dir_path
            / app_name
            / f"employees.{'csv' if app_name == 'ahgora' else 'txt'}"
        )
        return datetime.strftime(
            datetime.fromtimestamp(file_path.stat().st_mtime),
            "%d/%m/%Y, %H:%M",
        )

    def __str__(self):
        str_return = ""
        for key, value in self._read().items():
            str_return += f"{key}: {value}\n"

        return str_return
