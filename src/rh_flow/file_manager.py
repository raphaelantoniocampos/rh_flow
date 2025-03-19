from utils.constants import DATA_DIR, DOWNLOADS_DIR
from pathlib import Path


class FileManager:
    def move_files_from_downloads_dir(self):
        """Move arquivos da pasta de downloads para a pasta de dados, organizando-os por tipo."""
        for file in DOWNLOADS_DIR.iterdir():
            if "trabalhador" in file.name.lower():
                self._move_file(file, DATA_DIR / "fiorilli" / "employees.txt")
            elif "funcionarios" in file.name.lower():
                self._move_file(file, DATA_DIR / "ahgora" / "employees.csv")
            elif "tabledownloadcsv" in file.name.lower():
                self._move_file(file, DATA_DIR / "ahgora" / "absences.csv")
            elif "pontoafastamentos" in file.name.lower():
                self._move_file(file, DATA_DIR / "fiorilli" / "absences.txt")
            elif "pontoferias" in file.name.lower():
                self._move_file(file, DATA_DIR / "fiorilli" / "vacations.txt")

    def _move_file(self, source: Path, destination: Path):
        """Move um arquivo de um local para outro."""
        if not destination.parent.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
        source.replace(destination)
        print(
            f"[bold green]Arquivo movido: {source.name} -> {destination}[/bold green]"
        )
