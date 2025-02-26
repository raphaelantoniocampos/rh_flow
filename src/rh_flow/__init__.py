import datetime
from pathlib import Path
from config import Config


def verify_paths():
    working_dir_path = Path.cwd()
    needed_directories = [
        Path(working_dir_path / "downloads"),
        Path(working_dir_path / "data"),
        Path(working_dir_path / "data" / "ahgora"),
        Path(working_dir_path / "data" / "fiorilli"),
        Path(working_dir_path / "data" / "actions"),
    ]

    needed_files = [
        Path(working_dir_path / "data" / "ahgora" / "employees.csv"),
        Path(working_dir_path / "data" / "fiorilli" / "employees.txt"),
    ]

    for path in needed_directories:
        if not path.exists():
            path.mkdir(parents=True)

    for path in needed_files:
        if not path.exists():
            path.touch()
        else:
            if any(keyword in path.name for keyword in ["Trabalhador", "funcionarios"]):
                backup_path = path.with_name(f"backup_{path.name}")
                path.replace(backup_path)
                path.touch()

    config = Config(working_dir_path)
    if not config.data.get("init_date"):
        config.update("init_date", value=datetime.now().strftime("%d/%m/%Y"))
