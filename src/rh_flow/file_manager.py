from pathlib import Path


class FileManager:
    @staticmethod
    def move_files_from_downloads_dir(downloads_dir_path: Path, data_dir_path: Path):
        for file in downloads_dir_path.iterdir():
            if "trabalhador" in file.name.lower():
                file.replace(data_dir_path / "fiorilli" / "employees.txt")
            if "funcionarios" in file.name.lower():
                file.replace(data_dir_path / "ahgora" / "employees.csv")
            if "tabledownloadcsv" in file.name.lower():
                file.replace(data_dir_path / "ahgora" / "absences.csv")
            if "pontoafastamentos" in file.name.lower():
                file.replace(data_dir_path / "fiorilli" / "absences.txt")
            if "pontoferias" in file.name.lower():
                file.replace(data_dir_path / "fiorilli" / "vacations.txt")
