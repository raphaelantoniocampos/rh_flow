from rich import print
from pandas import DataFrame
from utils.constants import DATA_DIR, DOWNLOADS_DIR
from pathlib import Path


class FileManager:
    @staticmethod
    def move_downloads_to_data_dir():
        for file in DOWNLOADS_DIR.iterdir():
            if "trabalhador" in file.name.lower():
                FileManager.move_file(
                    source=file,
                    destination=DATA_DIR / "fiorilli" / "raw_employees.txt",
                )
            elif "funcionarios" in file.name.lower():
                FileManager.move_file(
                    source=file,
                    destination=DATA_DIR / "ahgora" / "raw_employees.csv",
                )
            elif "pontoafastamentos" in file.name.lower():
                FileManager.move_file(
                    source=file,
                    destination=DATA_DIR / "fiorilli" / "raw_absences.txt",
                )
            elif "pontoferias" in file.name.lower():
                FileManager.move_file(
                    source=file,
                    destination=DATA_DIR / "fiorilli" / "raw_vacations.txt",
                )

    @staticmethod
    def move_file(source: Path, destination: Path):
        if not destination.parent.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
        source.replace(destination)
        print(f"[bold green]Arquivo movido:[/bold green]{source.name} -> {destination}")

    @staticmethod
    def save_df(df: DataFrame, path: Path):
        if not df.empty:
            df.to_csv(
                path,
                index=False,
                encoding="utf-8",
            )
