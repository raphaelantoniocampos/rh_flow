from config import Config
from pathlib import Path
import json


def verify_paths():
    working_dir_path = Path.cwd()
    config_path = Path(working_dir_path / "data" / "config.json")
    if config_path.exists():
        with open(config_path, "r") as f:
            config_json = json.load(f)
            if config_json.get("init_date"):
                return

    needed_directories = [
        Path(working_dir_path / "downloads"),
        Path(working_dir_path / "data"),
        Path(working_dir_path / "data" / "ahgora"),
        Path(working_dir_path / "data" / "fiorilli"),
        Path(working_dir_path / "data" / "actions"),
    ]

    needed_files = [
        Path(working_dir_path / "data" / "ahgora" / "employees.csv"),
        Path(working_dir_path / "data" / "ahgora" / "absences.csv"),
        Path(working_dir_path / "data" / "fiorilli" / "employees.txt"),
        Path(working_dir_path / "data" / "fiorilli" / "absences.txt"),
        Path(working_dir_path / "data" / "fiorilli" / "vacations.txt"),
    ]

    for path in needed_directories:
        if not path.exists():
            path.mkdir(parents=True)

    for path in needed_files:
        if not path.exists():
            path.touch()
        else:
            if any(
                keyword in path.name.lower()
                for keyword in [
                    "trabalhador",
                    "funcionarios",
                    "tabledownloadcsv",
                    "pontoafastamentos",
                    "pontoferias",
                ]
            ):
                backup_path = path.with_name(f"backup_{path.name}")
                path.replace(backup_path)
                path.touch()

    Config(working_dir_path)
