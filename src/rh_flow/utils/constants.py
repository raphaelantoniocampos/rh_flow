from pathlib import Path

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
