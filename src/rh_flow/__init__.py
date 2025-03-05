from pathlib import Path


def verify_paths():
    base_dir_path = Path.cwd()

    needed_directories = [
        Path(base_dir_path / "downloads"),
        Path(base_dir_path / "data"),
        Path(base_dir_path / "data" / "ahgora"),
        Path(base_dir_path / "data" / "fiorilli"),
        Path(base_dir_path / "data" / "actions"),
    ]

    needed_files = [
        Path(base_dir_path / "data" / "ahgora" / "employees.csv"),
        Path(base_dir_path / "data" / "ahgora" / "absences.csv"),
        Path(base_dir_path / "data" / "fiorilli" / "employees.txt"),
        Path(base_dir_path / "data" / "fiorilli" / "absences.txt"),
        Path(base_dir_path / "data" / "fiorilli" / "vacations.txt"),
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
