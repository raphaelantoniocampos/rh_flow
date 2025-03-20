from pathlib import Path

import time
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
    "Sair",
]


def spinner(
    wait_string: str = "Voltando",
    wait_time: float = 0.40,
    console: Console = Console(),
):
    with console.status(f"[bold green]{wait_string}...[/bold green]", spinner="dots"):
        time.sleep(wait_time)
