from datetime import datetime
from rich.console import Console
import inquirer
from rich import print
from rich.panel import Panel

from pathlib import Path
import json

INIT_CONFIG = {
    "ignore": {},
    "last_analisys": {"datetime": "", "time_since": ""},
    "last_download": {"datetime": "", "time_since": ""},
}


class Config:
    def __init__(self, data_dir: Path):
        self.path: Path = data_dir / "config.json"
        self.data: dict = self._load()
        self._update_time_since()

    def _load(self) -> dict:
        if self.path.exists():
            with open(self.path, "r") as f:
                return json.load(f)
        else:
            return self.create()

    def read(self) -> dict:
        return self.data

    def update(self, field: str, new_data: dict) -> None:
        if field not in self.data:
            self.data[field] = {}

        self.data[field].update(new_data)

        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def create(self) -> dict:
        with open(self.path, "w") as f:
            json.dump(INIT_CONFIG, f, indent=4)
        return INIT_CONFIG

    def remove(self, field: str, key: str) -> str:
        if field in self.data and key in self.data[field]:
            del self.data[field][key]
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=4)
            return f"Item '{key}' removido do campo '{field}'."
        else:
            return f"Item '{key}' não encontrado no campo '{field}'."

    def format_timedelta(self, td):
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"

    def config_panel(self, console: Console):
        config_data = self.read()
        ignore_data = config_data.get("ignore", {})
        last_analisys = self.data.get(
            "last_analisys", {"datetime": "", "time_since": ""}
        )
        last_download = self.data.get(
            "last_download", {"datetime": "", "time_since": ""}
        )

        if not ignore_data:
            print(
                "[bold yellow]Nenhum funcionário está sendo ignorado no momento.[/bold yellow]"
            )
            return

        console.print(Panel.fit("[bold]Configurações[/bold]", border_style="yellow"))

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

        if action == "Ver lista de ignorados":
            ignored_list = [
                f"{id} - {data['Data Admissao']} - {data['Nome']} - {data['Vinculo']}"
                for id, data in ignore_data.items()
            ]

            console.print(
                Panel.fit("[bold]Funcionários Ignorados[/bold]", border_style="yellow")
            )
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
                    self.remove("ignore", employee[:6])
                    console.print(
                        f"[bold green]Funcionário com matrícula {employee[:6]} removido da lista de ignorados.[/bold green]"
                    )

    def _update_time_since(self):
        last_analisys = self.data.get(
            "last_analisys", {"datetime": "", "time_since": ""}
        )
        last_download = self.data.get(
            "last_download", {"datetime": "", "time_since": ""}
        )

        now = datetime.now()

        if last_download["datetime"]:
            last_download_dt = datetime.strptime(
                last_download["datetime"], "%m/%d/%Y, %H:%M:%S"
            )
            time_since_last_download = now - last_download_dt
            last_download["time_since"] = self.format_timedelta(
                time_since_last_download
            )
            self.update("last_download", last_download)

        if last_analisys["datetime"]:
            last_analisys_dt = datetime.strptime(
                last_analisys["datetime"], "%m/%d/%Y, %H:%M:%S"
            )
            time_since_last_analisys = now - last_analisys_dt
            last_analisys["time_since"] = self.format_timedelta(
                time_since_last_analisys
            )
            self.update("last_analisys", last_analisys)

    def __str__(self):
        str_return = ""
        for key, value in self.read().items():
            str_return += f"{key}: {value}\n"

        return str_return
