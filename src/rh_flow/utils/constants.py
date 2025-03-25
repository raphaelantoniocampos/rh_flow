import time
from pathlib import Path

from rich.console import Console

BASE_DIR = Path(Path.cwd() / "src")
DATA_DIR = BASE_DIR / "data"
DOWNLOADS_DIR = BASE_DIR / "downloads"

INQUIRER_KEYBINDINGS = {
    "answer": [
        {"key": "enter"},
    ],
    "interrupt": [
        {"key": "c-c"},
        {"key": "c-e"},
    ],
    "skip": [
        {"key": "c-z"},
        {"key": "escape"},
    ],
    "down": [
        {"key": "down"},
        {"key": "j"},
    ],
    "up": [
        {"key": "up"},
        {"key": "k"},
    ],
    "toggle": [
        {"key": "space"},
    ],
    "toggle-all-true": [
        {"key": "a"},
    ],
}


JSON_INIT_CONFIG = {
    "init_date": "",
    "last_analisys": {"datetime": "", "time_since": ""},
    "last_download": {
        "ahgora_employees": {"datetime": "", "time_since": ""},
        "fiorilli_employees": {"datetime": "", "time_since": ""},
        "fiorilli_absences": {"datetime": "", "time_since": ""},
        "fiorilli_vacations": {"datetime": "", "time_since": ""},
    },
}

MAIN_MENU_OPTIONS = [
    "Baixar Dados",
    "Analisar dados",
    "Tarefas",
    "Configurações",
    "Live Display",
    "Sair",
]

PT_MONTHS = {
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

PT_WEEKDAYS = {
    "Mon": "Seg",
    "Tue": "Ter",
    "Wed": "Qua",
    "Thu": "Qui",
    "Fri": "Sex",
    "Sat": "Sáb",
    "Sun": "Dom",
}


def spinner(
    wait_string: str = "Voltando",
    wait_time: float = 0.40,
    console: Console = Console(),
):
    with console.status(f"[bold green]{wait_string}...[/bold green]", spinner="dots"):
        time.sleep(wait_time)


class Key:
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.key = str(name)

    def __str__(self):
        return f"[bold {self.color}]{self.name.upper()}[/bold {self.color}]"
