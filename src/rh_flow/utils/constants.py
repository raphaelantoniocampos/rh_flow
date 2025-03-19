from pathlib import Path

BASE_DIR = Path(Path.cwd() / "src")
DATA_DIR = BASE_DIR / "data"
DOWNLOADS_DIR = BASE_DIR / "downloads"

KEYBINDINGS = {
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
    # "toggle-down": [
    #     {"key": "c-space"},
    # ],
    # "toggle-up": [
    #     {"key": "s-space"},
    # ],
    "toggle-all-true": [
        {"key": "a"},
    ],
    # "toggle-all-false": [
    #     {"key": "s-a"},
    # ],
}
