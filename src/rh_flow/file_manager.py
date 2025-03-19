from pathlib import Path

class FileManager:
    def __init__(self, downloads_dir_path: Path, data_dir_path: Path):
        self.downloads_dir_path = downloads_dir_path
        self.data_dir_path = data_dir_path

    def move_files_from_downloads_dir(self):
        """Move arquivos da pasta de downloads para a pasta de dados, organizando-os por tipo."""
        for file in self.downloads_dir_path.iterdir():
            if "trabalhador" in file.name.lower():
                self._move_file(file, self.data_dir_path / "fiorilli" / "employees.txt")
            elif "funcionarios" in file.name.lower():
                self._move_file(file, self.data_dir_path / "ahgora" / "employees.csv")
            elif "tabledownloadcsv" in file.name.lower():
                self._move_file(file, self.data_dir_path / "ahgora" / "absences.csv")
            elif "pontoafastamentos" in file.name.lower():
                self._move_file(file, self.data_dir_path / "fiorilli" / "absences.txt")
            elif "pontoferias" in file.name.lower():
                self._move_file(file, self.data_dir_path / "fiorilli" / "vacations.txt")

    def _move_file(self, source: Path, destination: Path):
        """Move um arquivo de um local para outro."""
        if not destination.parent.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
        source.replace(destination)
        print(f"[bold green]Arquivo movido: {source.name} -> {destination}[/bold green]")
