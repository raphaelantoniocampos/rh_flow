from InquirerPy import inquirer
from rich.panel import Panel
from rh_flow.utils.constants import (
    console,
    JSON_INIT_CONFIG,
    DATA_DIR,
    INQUIRER_KEYBINDINGS,
    spinner,
)
from pathlib import Path
import json
from datetime import datetime, timedelta
from rh_flow.managers.file_manager import FileManager


class Config:
    def __init__(self):
        self.json_path: Path = DATA_DIR / "config.json"
        self.data: dict = self._load()
        self._update_time_since()

    def menu(self) -> None:
        console.print(
            Panel.fit(
                "CONFIGURAÇÕES",
                style="bold cyan",
            )
        )
        last_analisys = self.data.get("last_analisys")
        last_download_fiorilli = self.data.get("last_download")["fiorilli_employees"]
        last_download_ahgora = self.data.get("last_download")["ahgora_employees"]
        last_download_absences = self.data.get("last_download")["absences"]

        console.print(
            f"""
[cyan]•[/] [bold]Última análise[/]: {last_analisys["datetime"]} ([bold]{
                last_analisys["time_since"]
            }[/] atrás)

[cyan]•[/] [bold]Últimos downloads[/]: 
• Funcionários Fiorilli - {last_download_fiorilli["datetime"]} ([bold]{
                last_download_fiorilli["time_since"]
            }[/] atrás)
• Funcionários Ahgora - {last_download_ahgora["datetime"]} ([bold]{
                last_download_ahgora["time_since"]
            }[/] atrás)
• Afastamentos - {last_download_absences["datetime"]} ([bold]{
                last_download_absences["time_since"]
            }[/] atrás)
"""
        )

        answer = inquirer.rawlist(
            message="Selecione as opções de download",
            choices=["Voltar"],
            keybindings=INQUIRER_KEYBINDINGS,
            multiselect=True,
        ).execute()

        if answer == "Voltar":
            spinner()
            return

    @staticmethod
    def update_last_analisys():
        now = datetime.now()
        last_analisys = {"datetime": now.strftime("%d/%m/%Y, %H:%M"), "time_since": now}
        config = Config()
        config._update_analysis_time_since(last_analisys, now)

    def _load(self) -> dict:
        if self.json_path.exists():
            with open(self.json_path, "r") as f:
                return json.load(f)
        else:
            self.data = self._create()
            return self._update(
                "init_date", value=datetime.now().strftime("%d/%m/%Y, %H:%M")
            )

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

        with open(self.json_path, "w") as f:
            json.dump(self.data, f, indent=4)

        return self.data

    def _create(self) -> dict:
        with open(self.json_path, "w") as f:
            json.dump(JSON_INIT_CONFIG, f, indent=4)
        return JSON_INIT_CONFIG

    def _delete(self, field: str, key: str) -> str:
        if field in self.data and key in self.data[field]:
            del self.data[field][key]
            with open(self.json_path, "w") as f:
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
            self._update_downloads_time_since(last_download, "ahgora_employees", now)
            self._update_downloads_time_since(last_download, "fiorilli_employees", now)
            self._update_downloads_time_since(last_download, "absences", now)
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
        self, last_download: dict, file_name: str, now: timedelta
    ) -> None:
        file_last_download = last_download.get(file_name)

        file_last_download["datetime"] = self._get_last_download(file_name)

        last_download_dt = datetime.strptime(
            file_last_download["datetime"], "%d/%m/%Y, %H:%M"
        )
        time_since_last_download = now - last_download_dt
        file_last_download["time_since"] = self._format_timedelta(
            time_since_last_download
        )

        self._update("last_download", file_name, value=file_last_download)

    def _get_last_download(self, file_name: str) -> str:
        file_path = FileManager.file_name_to_file_path(file_name)

        return datetime.strftime(
            datetime.fromtimestamp(file_path.stat().st_mtime),
            "%d/%m/%Y, %H:%M",
        )

    def __str__(self):
        str_return = ""
        for key, value in self._read().items():
            str_return += f"{key}: {value}\n"

        return str_return
